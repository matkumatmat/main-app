from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Any


class SuspiciousActivityOutput(BaseModel):
    id: str
    timestamp: datetime
    remote_ip: str
    activity_type: str
    severity: str
    details: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class SuspiciousActivitiesListOutput(BaseModel):
    count: int
    activities: list[SuspiciousActivityOutput]


class SuspiciousActivitiesByIpOutput(BaseModel):
    remote_ip: str
    count: int
    activities: list[SuspiciousActivityOutput]


class SuspiciousActivitiesBySeverityOutput(BaseModel):
    severity: str
    count: int
    activities: list[SuspiciousActivityOutput]


class ThreatAssessmentOutput(BaseModel):
    threat_level: str
    total_activities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    high_risk_ips: list[str]
    recommendations: list[str]


class ThreatAssessmentResponseOutput(BaseModel):
    assessment: ThreatAssessmentOutput
    analyzed_activities: int


class RateLimitViolationOutput(BaseModel):
    id: str
    timestamp: datetime
    service: str
    remote_ip: str
    violation_count: int
    user_id: str | None = None

    class Config:
        from_attributes = True


class RateLimitViolationsListOutput(BaseModel):
    count: int
    violations: list[RateLimitViolationOutput]


class RateLimitViolationsByIpOutput(BaseModel):
    remote_ip: str
    count: int
    violations: list[RateLimitViolationOutput]


class RateLimitViolationsByServiceOutput(BaseModel):
    service: str
    count: int
    violations: list[RateLimitViolationOutput]
