from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String, DateTime, Boolean, Float
from shared.backend.utils.uuid import generateId

class MetricSnapshot(SQLModel, table=True):
    __tablename__ = "metric_snapshot"
    __table_args__ = (
        Index('ix_metric_snapshot_timestamp', 'timestamp'),
        Index('ix_metric_snapshot_service', 'service'),
        Index('ix_metric_snapshot_remote_ip', 'remote_ip'),
        Index('ix_metric_snapshot_rate_limited', 'rate_limited'),
        Index('ix_metric_snapshot_user_id', 'user_id'),
        Index('ix_metric_snapshot_service_timestamp', 'service', 'timestamp'),
        Index('ix_metric_snapshot_remote_ip_timestamp', 'remote_ip', 'timestamp'),
    )

    id: UUID = Field(default_factory=generateId, primary_key=True)
    timestamp: datetime = Field(sa_column=Column(DateTime, nullable=False))
    service: str = Field(sa_column=Column(String(50), nullable=False))
    remote_ip: str = Field(sa_column=Column(String(45), nullable=False))
    request_id: str = Field(sa_column=Column(String(100), nullable=False))
    method: str = Field(sa_column=Column(String(10), nullable=False))
    url: str = Field(sa_column=Column(String(500), nullable=False))
    status: int = Field(nullable=False)
    rate_limited: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    user_agent: str = Field(sa_column=Column(String(500), nullable=True))
    nginx_latency_ms: float = Field(sa_column=Column(Float, nullable=False))
    backend_latency_ms: float | None = Field(default=None, sa_column=Column(Float, nullable=True))
    user_id: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
