from __future__ import annotations
from typing import Any
from datetime import datetime, UTC
from .baseException import BaseAppException
import structlog


class ErrorResponseFactory:
    @staticmethod
    def create(
        exception: BaseAppException,
        request_id: str | None = None
    ) -> dict[str, Any]:
        error_data: dict[str, Any] = {
            "code": exception.code,
            "message": exception.message
        }

        if exception.field:
            error_data["field"] = exception.field

        if exception.details:
            error_data["details"] = exception.details

        response = {
            "error": error_data,
            "timestamp": datetime.now(UTC).isoformat()
        }

        if request_id:
            response["request_id"] = request_id

        return response

    @staticmethod
    def createValidation(
        message: str,
        field: str | None = None,
        request_id: str | None = None
    ) -> dict[str, Any]:
        response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message
            },
            "timestamp": datetime.now(UTC).isoformat()
        }

        if field:
            response["error"]["field"] = field

        if request_id:
            response["request_id"] = request_id

        return response

    @staticmethod
    def createGeneric(
        code: str,
        message: str,
        status_code: int = 500,
        request_id: str | None = None,
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        error_data: dict[str, Any] = {
            "code": code,
            "message": message
        }

        if details:
            error_data["details"] = details

        response = {
            "error": error_data,
            "timestamp": datetime.now(UTC).isoformat()
        }

        if request_id:
            response["request_id"] = request_id

        return response


def getRequestId() -> str | None:
    try:
        log = structlog.get_logger()
        context = log._context
        return context.get("request_id")
    except (AttributeError, KeyError):
        return None
