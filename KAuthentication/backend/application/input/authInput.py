from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterInput(BaseModel):
    """Input schema for user registration"""
    username: str = Field(min_length=4, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validateUsername(cls, v: str) -> str:
        """Validate username contains only alphanumeric and underscores"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validatePassword(cls, v: str) -> str:
        """Validate password meets complexity requirements"""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, v):
            raise ValueError(
                "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
        return v

class LoginInput(BaseModel):
    """Input schema for user login"""
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class TokenRefreshInput(BaseModel):
    """Input schema for token refresh"""
    refresh_token: str = Field(min_length=10)

class PasswordResetRequestInput(BaseModel):
    """Input schema for password reset request"""
    email: EmailStr

class PasswordResetInput(BaseModel):
    """Input schema for password reset with token"""
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validatePassword(cls, v: str) -> str:
        """Validate new password meets complexity requirements"""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, v):
            raise ValueError(
                "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
        return v

class PasswordChangeInput(BaseModel):
    """Input schema for password change (authenticated)"""
    old_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validatePassword(cls, v: str) -> str:
        """Validate new password meets complexity requirements"""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, v):
            raise ValueError(
                "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
        return v

class EmailVerifyInput(BaseModel):
    """Input schema for email verification"""
    token: str = Field(min_length=10)
