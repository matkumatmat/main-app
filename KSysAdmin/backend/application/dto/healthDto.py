from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class SystemHealthSnapshotOutput(BaseModel):
    id: str
    timestamp: datetime
    db_status: str
    db_latency_ms: float | None = None
    redis_status: str
    redis_latency_ms: float | None = None
    crypto_status: str

    class Config:
        from_attributes = True


class SystemHealthSnapshotsListOutput(BaseModel):
    count: int
    snapshots: list[SystemHealthSnapshotOutput]


class SystemHealthHistoryOutput(BaseModel):
    start: datetime
    end: datetime
    count: int
    snapshots: list[SystemHealthSnapshotOutput]


class HealthAnalysisOutput(BaseModel):
    total_snapshots: int
    db_uptime_percentage: float
    redis_uptime_percentage: float
    crypto_uptime_percentage: float
    avg_db_latency_ms: float
    avg_redis_latency_ms: float
    max_db_latency_ms: float
    max_redis_latency_ms: float


class HealthStatusAnalysisOutput(BaseModel):
    time_range: dict[str, datetime]
    analysis: HealthAnalysisOutput
