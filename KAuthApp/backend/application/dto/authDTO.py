from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime
import uuid
from typing import Optional, Generic, TypeVar

# Input DTOs
class SignUpInput(BaseModel):
    fullName: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class SignInInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class VerifyOtpInput(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")

class ResendOtpInput(BaseModel):
    email: EmailStr

class RefreshTokenInput(BaseModel):
    refreshToken: str

# Output DTOs
class UserDTO(BaseModel):
    id: uuid.UUID
    email: str
    fullName: str
    isVerified: bool
    createdAt: datetime

class TokenDTO(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    expiresIn: int

class AuthData(BaseModel):
    user: Optional[UserDTO] = None
    tokens: Optional[TokenDTO] = None
    message: Optional[str] = None

class RefreshTokenData(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int

T = TypeVar("T")

class AuthResponse(BaseModel, Generic[T]):
    success: bool
    data: T
    message: Optional[str] = None
