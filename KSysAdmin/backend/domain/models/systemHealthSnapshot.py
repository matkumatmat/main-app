from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String, DateTime, Float
from shared.backend.utils.uuid import generateId

class SystemHealthSnapshot(SQLModel, table=True):
    __tablename__ = "system_health_snapshot"
    __table_args__ = (
        Index('ix_health_timestamp', 'timestamp'),
    )

    id: UUID = Field(default_factory=generateId, primary_key=True)
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    db_status: str = Field(sa_column=Column(String(20), nullable=False))
    db_latency_ms: float = Field(sa_column=Column(Float, nullable=False))
    redis_status: str = Field(sa_column=Column(String(20), nullable=False))
    redis_latency_ms: float = Field(sa_column=Column(Float, nullable=False))
    crypto_status: str = Field(sa_column=Column(String(20), nullable=False))
