from __future__ import annotations
from datetime import datetime
from sqlmodel import SQLModel, Field
from shared.backend.utils.uuid import generateId
import uuid

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: uuid.UUID = Field(default_factory=generateId, primary_key=True)
    user_id: uuid.UUID = Field(index=True, foreign_key="users.id")
    token_hash: str = Field(unique=True, index=True)
    expires_at: datetime
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<RefreshToken {self.id} for User {self.user_id}>"
