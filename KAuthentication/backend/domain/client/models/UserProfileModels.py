from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import Field, Column
from sqlalchemy import JSON
from domain.utilities.BaseModel import BaseModels

class UserModel(BaseModels, table=True):
    """User profile model with authentication credentials"""
    __tablename__ = "users_profiles"

    sid: UUID = Field(primary_key=True, nullable=False)
    username: str = Field(max_length=255, nullable=False, unique=True, index=True)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password: str = Field(max_length=255, nullable=False)

    first_name: str | None = Field(default=None, max_length=255, nullable=True)
    last_name: str | None = Field(default=None, max_length=255, nullable=True)
    phone: str | None = Field(default=None, max_length=50, nullable=True, unique=True, index=True)
    address: str | None = Field(default=None, nullable=True)
    region: str | None = Field(default=None, max_length=50, nullable=True)

    metadata_info: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    devices: str | None = Field(default=None, max_length=10, nullable=True)

    active: bool = Field(default=False, nullable=False)
    actived_at: datetime | None = Field(default=None, nullable=True)

    def __repr__(self) -> str:
        return f"UserModel(sid={self.sid}, username={self.username})"

