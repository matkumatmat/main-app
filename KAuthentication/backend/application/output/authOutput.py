from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime

class AuthOutput(BaseModel):
    """Output schema for authentication responses"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user_id: str
    email: str
    username: str

class UserProfileOutput(BaseModel):
    """Output schema for user profile"""
    user_id: str
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    phone: str | None
    active: bool
    created_at: datetime

class MessageOutput(BaseModel):
    """Output schema for simple message responses"""
    message: str
    success: bool = True
