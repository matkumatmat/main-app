from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String, DateTime, Integer
from shared.backend.utils.uuid import generateId

class RateLimitViolation(SQLModel, table=True):
    __tablename__ = "rate_limit_violation"
    __table_args__ = (
        Index('ix_rate_limit_timestamp', 'timestamp'),
        Index('ix_rate_limit_service', 'service'),
        Index('ix_rate_limit_remote_ip', 'remote_ip'),
        Index('ix_rate_limit_remote_ip_timestamp', 'remote_ip', 'timestamp'),
    )

    id: UUID = Field(default_factory=generateId, primary_key=True)
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    service: str = Field(sa_column=Column(String(50), nullable=False))
    remote_ip: str = Field(sa_column=Column(String(45), nullable=False))
    violation_count: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    user_id: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
