from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import datetime

class BaseModels(SQLModel):
    """Base model with audit fields for all database models"""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: datetime | None = Field(default=None, nullable=True)
    deleted: bool = Field(default=False, nullable=False)
    deleted_at: datetime | None = Field(default=None, nullable=True)
