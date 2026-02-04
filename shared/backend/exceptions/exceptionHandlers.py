from __future__ import annotations
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from .baseException import BaseAppException
from .errorResponse import ErrorResponseFactory, getRequestId
from shared.backend.loggingFactory import LoggerFactory

systemLogger = LoggerFactory.getSystemLogger("SharedExceptionHandler")


async def appExceptionHandler(request: Request, exc: BaseAppException) -> JSONResponse:
    request_id = getRequestId()

    systemLogger.application(
        label="application_error",
        message=exc.message,
        level="error",
        error_code=exc.code,
        status_code=exc.status_code,
        path=str(request.url),
        method=request.method
    )

    response_data = ErrorResponseFactory.create(
        exception=exc,
        request_id=request_id
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validationExceptionHandler(
    request: Request,
    exc: RequestValidationError | ValidationError
) -> JSONResponse:
    request_id = getRequestId()

    errors = exc.errors() if hasattr(exc, 'errors') else []
    error_messages = []

    for error in errors:
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        error_messages.append(f"{loc}: {msg}")

    combined_message = "; ".join(error_messages) if error_messages else "Validation failed"

    systemLogger.application(
        label="validation_error",
        message=combined_message,
        level="error",
        path=str(request.url),
        method=request.method,
        errors=errors
    )

    response_data = ErrorResponseFactory.createValidation(
        message=combined_message,
        request_id=request_id
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def genericExceptionHandler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getRequestId()

    systemLogger.error(
        label="unhandled_exception",
        exception=exc,
        message="Unhandled exception occurred",
        path=str(request.url),
        method=request.method
    )

    response_data = ErrorResponseFactory.createGeneric(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        status_code=500,
        request_id=request_id
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


def registerExceptionHandlers(app) -> None:
    app.add_exception_handler(BaseAppException, appExceptionHandler)
    app.add_exception_handler(RequestValidationError, validationExceptionHandler)
    app.add_exception_handler(ValidationError, validationExceptionHandler)
    app.add_exception_handler(Exception, genericExceptionHandler)
