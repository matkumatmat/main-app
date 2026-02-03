from __future__ import annotations
from typing import Any


class BaseAppException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        field: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        self.details = details or {}


class ValidationException(BaseAppException):
    def __init__(
        self,
        message: str,
        field: str | None = None,
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=422,
            field=field,
            details=details
        )


class NotFoundException(BaseAppException):
    def __init__(
        self,
        message: str,
        code: str = "NOT_FOUND",
        field: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=404,
            field=field,
            details=details
        )


class UnauthorizedException(BaseAppException):
    def __init__(
        self,
        message: str = "Unauthorized",
        code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details
        )


class ForbiddenException(BaseAppException):
    def __init__(
        self,
        message: str = "Forbidden",
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details
        )


class ConflictException(BaseAppException):
    def __init__(
        self,
        message: str,
        code: str = "CONFLICT",
        field: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=409,
            field=field,
            details=details
        )


class BadRequestException(BaseAppException):
    def __init__(
        self,
        message: str,
        code: str = "BAD_REQUEST",
        field: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            field=field,
            details=details
        )


class InternalServerException(BaseAppException):
    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_SERVER_ERROR",
        details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=500,
            details=details
        )
