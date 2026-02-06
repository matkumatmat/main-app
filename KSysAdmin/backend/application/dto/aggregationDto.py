from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class TriggerHourlyAggregationInput(BaseModel):
    hour: datetime | None = None


class TriggerHourlyAggregationOutput(BaseModel):
    status: str
    hour: str
    services_aggregated: int
    details: dict[str, int]


class TriggerSecurityAnalysisOutput(BaseModel):
    status: str
    suspicious_activities_detected: int


class TriggerCleanupInput(BaseModel):
    retention_days: int | None = None


class TriggerCleanupOutput(BaseModel):
    status: str
    total_deleted: int
    details: dict[str, int]
