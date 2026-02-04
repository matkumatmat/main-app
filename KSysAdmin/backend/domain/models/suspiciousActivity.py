from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String, DateTime, JSON
from shared.backend.utils.uuid import generateId

class SuspiciousActivity(SQLModel, table=True):
    __tablename__ = "suspicious_activity"
    __table_args__ = (
        Index('ix_suspicious_timestamp', 'timestamp'),
        Index('ix_suspicious_remote_ip', 'remote_ip'),
        Index('ix_suspicious_severity', 'severity'),
        Index('ix_suspicious_remote_ip_timestamp', 'remote_ip', 'timestamp'),
    )

    id: UUID = Field(default_factory=generateId, primary_key=True)
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    remote_ip: str = Field(sa_column=Column(String(45), nullable=False))
    activity_type: str = Field(sa_column=Column(String(50), nullable=False))
    severity: str = Field(sa_column=Column(String(20), nullable=False))
    details: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
