from __future__ import annotations
from datetime import datetime
from sqlmodel import SQLModel, Field
from shared.backend.utils.uuid import generateId
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=generateId, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"
