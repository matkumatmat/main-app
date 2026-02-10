from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import Field
from domain.utilities.BaseModel import BaseModels

class SessionModel(BaseModels, table=True):
    """User session model for JWT token management"""
    __tablename__ = "user_sessions"

    model_config = {"populate_by_name": True}

    sid: UUID = Field(primary_key=True, nullable=False)
    user_id: UUID = Field(nullable=False, index=True)
    active: datetime = Field(nullable=False)
    expiry: datetime = Field(nullable=False, index=True)

    access_token: str = Field(max_length=500, nullable=False, unique=True, index=True, alias="_at")
    refresh_token: str = Field(max_length=500, nullable=False, unique=True, index=True, alias="_rt")
    fingerprint: str = Field(max_length=255, nullable=False, index=True, alias="_fp")
    cookie: str = Field(max_length=255, nullable=False, index=True, unique=True, alias="_cookie")
    session_metadata: str = Field(nullable=False, alias="_md")

    def __repr__(self) -> str:
        return f"SessionModel(sid={self.sid}, user_id={self.user_id})"

