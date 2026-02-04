from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String, DateTime, Integer, Float, UniqueConstraint
from shared.backend.utils.uuid import generateId

class HourlyMetricAggregation(SQLModel, table=True):
    __tablename__ = "hourly_metric_aggregation"
    __table_args__ = (
        UniqueConstraint('hour_start', 'service', name='uq_hourly_metric_hour_service'),
        Index('ix_hourly_metric_hour_start', 'hour_start'),
        Index('ix_hourly_metric_service', 'service'),
        Index('ix_hourly_metric_service_hour', 'service', 'hour_start'),
    )

    id: UUID = Field(default_factory=generateId, primary_key=True)
    hour_start: datetime = Field(sa_column=Column(DateTime, nullable=False))
    service: str = Field(sa_column=Column(String(50), nullable=False))
    total_requests: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    successful_requests: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    client_errors: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    server_errors: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    rate_limited_requests: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    avg_nginx_latency_ms: float = Field(default=0.0, sa_column=Column(Float, nullable=False))
    avg_backend_latency_ms: float = Field(default=0.0, sa_column=Column(Float, nullable=False))
    p95_nginx_latency_ms: float = Field(default=0.0, sa_column=Column(Float, nullable=False))
    p95_backend_latency_ms: float = Field(default=0.0, sa_column=Column(Float, nullable=False))
    unique_ips: int = Field(default=0, sa_column=Column(Integer, nullable=False))
