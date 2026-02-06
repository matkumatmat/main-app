from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class MetricSnapshotOutput(BaseModel):
    id: str
    timestamp: datetime
    service: str
    remote_ip: str
    request_id: str
    method: str
    url: str
    status: int
    rate_limited: bool
    nginx_latency_ms: float | None = None
    backend_latency_ms: float | None = None
    user_id: str | None = None

    class Config:
        from_attributes = True


class MetricListOutput(BaseModel):
    service: str
    count: int
    start: datetime | None = None
    end: datetime | None = None
    metrics: list[MetricSnapshotOutput]


class HourlyAggregationOutput(BaseModel):
    id: str
    hour_start: datetime
    service: str
    total_requests: int
    successful_requests: int
    client_errors: int
    server_errors: int
    rate_limited_requests: int
    avg_nginx_latency_ms: float | None = None
    avg_backend_latency_ms: float | None = None
    p95_nginx_latency_ms: float | None = None
    p95_backend_latency_ms: float | None = None
    unique_ips: int

    class Config:
        from_attributes = True


class HourlyAggregationListOutput(BaseModel):
    service: str
    count: int
    aggregations: list[HourlyAggregationOutput]


class RateLimitedRequestsOutput(BaseModel):
    id: str
    timestamp: datetime
    service: str
    remote_ip: str
    url: str
    user_id: str | None = None

    class Config:
        from_attributes = True


class RateLimitedRequestsListOutput(BaseModel):
    count: int
    rate_limited_requests: list[RateLimitedRequestsOutput]


class ErrorRequestOutput(BaseModel):
    id: str
    timestamp: datetime
    service: str
    remote_ip: str
    method: str
    url: str
    status: int
    backend_latency_ms: float | None = None

    class Config:
        from_attributes = True


class ErrorRequestsListOutput(BaseModel):
    count: int
    error_requests: list[ErrorRequestOutput]


class MetricsByIpOutput(BaseModel):
    id: str
    timestamp: datetime
    service: str
    method: str
    url: str
    status: int
    rate_limited: bool

    class Config:
        from_attributes = True


class MetricsByIpListOutput(BaseModel):
    remote_ip: str
    count: int
    metrics: list[MetricsByIpOutput]
