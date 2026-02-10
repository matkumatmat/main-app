from __future__ import annotations
from shared.backend.exceptions.baseException import (
    UnauthorizedException,
    BadRequestException,
    ConflictException,
    NotFoundException
)

class InvalidCredentialsException(UnauthorizedException):
    """Raised when login credentials are invalid"""
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS"
        )

class UserInactiveException(UnauthorizedException):
    """Raised when user account is not activated"""
    def __init__(self):
        super().__init__(
            message="Account not activated. Please verify your email.",
            code="USER_INACTIVE"
        )

class InvalidTokenException(UnauthorizedException):
    """Raised when JWT token is invalid or expired"""
    def __init__(self, reason: str = "Invalid or expired token"):
        super().__init__(
            message=reason,
            code="INVALID_TOKEN"
        )

class TokenExpiredException(UnauthorizedException):
    """Raised when refresh token has expired"""
    def __init__(self):
        super().__init__(
            message="Refresh token expired. Please login again.",
            code="TOKEN_EXPIRED"
        )

class EmailAlreadyExistsException(ConflictException):
    """Raised when email is already registered"""
    def __init__(self, email: str):
        super().__init__(
            message=f"Email {email} is already registered",
            code="EMAIL_EXISTS",
            field="email"
        )

class UsernameAlreadyExistsException(ConflictException):
    """Raised when username is already taken"""
    def __init__(self, username: str):
        super().__init__(
            message=f"Username {username} is already taken",
            code="USERNAME_EXISTS",
            field="username"
        )

class WeakPasswordException(BadRequestException):
    """Raised when password doesn't meet complexity requirements"""
    def __init__(self):
        super().__init__(
            message="Password must be at least 8 characters with uppercase, lowercase, number, and special character",
            code="WEAK_PASSWORD",
            field="password"
        )

class InvalidVerificationTokenException(BadRequestException):
    """Raised when email verification token is invalid"""
    def __init__(self):
        super().__init__(
            message="Invalid or expired verification token",
            code="INVALID_VERIFICATION_TOKEN"
        )

class PasswordResetTokenInvalidException(BadRequestException):
    """Raised when password reset token is invalid"""
    def __init__(self):
        super().__init__(
            message="Invalid or expired password reset token",
            code="INVALID_RESET_TOKEN"
        )

class UserNotFoundException(NotFoundException):
    """Raised when user is not found"""
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User not found: {identifier}",
            code="USER_NOT_FOUND"
        )
