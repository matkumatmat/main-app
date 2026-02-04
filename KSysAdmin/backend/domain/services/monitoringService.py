from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.infrastructure.database.repositories.metricSnapshotRepository import MetricSnapshotRepository
from KSysAdmin.backend.infrastructure.database.repositories.hourlyMetricAggregationRepository import HourlyMetricAggregationRepository
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from KSysAdmin.backend.domain.models.hourlyMetricAggregation import HourlyMetricAggregation


class MonitoringService:
    """
    Domain service for monitoring and metrics operations.
    Orchestrates metric snapshot and aggregation logic.
    """

    def __init__(self, session: AsyncSession):
        self.metricRepo = MetricSnapshotRepository(session)
        self.hourlyRepo = HourlyMetricAggregationRepository(session)

    async def recordMetric(
        self,
        service: str,
        remote_ip: str,
        request_id: str,
        method: str,
        url: str,
        status: int,
        nginx_latency_ms: float,
        backend_latency_ms: float | None = None,
        user_id: str | None = None,
        rate_limited: bool = False,
        user_agent: str | None = None
    ) -> MetricSnapshot:
        """Record a new metric snapshot"""
        metric = MetricSnapshot(
            timestamp=datetime.utcnow(),
            service=service,
            remote_ip=remote_ip,
            request_id=request_id,
            method=method,
            url=url,
            status=status,
            rate_limited=rate_limited,
            user_agent=user_agent,
            nginx_latency_ms=nginx_latency_ms,
            backend_latency_ms=backend_latency_ms,
            user_id=user_id
        )
        return await self.metricRepo.create(metric)

    async def getServiceMetrics(
        self,
        service: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000
    ) -> list[MetricSnapshot]:
        """Retrieve metrics for a service, optionally within time range"""
        if start and end:
            return await self.metricRepo.getByTimeRange(start, end, service, limit)
        return await self.metricRepo.getByService(service, limit)

    async def getHourlyAggregation(
        self,
        service: str,
        start: datetime | None = None,
        end: datetime | None = None
    ) -> list[HourlyMetricAggregation]:
        """Retrieve hourly aggregated metrics"""
        if start and end:
            return await self.hourlyRepo.getByServiceAndTimeRange(service, start, end)
        return await self.hourlyRepo.getByService(service)

    async def getRateLimitedRequests(self, limit: int = 100) -> list[MetricSnapshot]:
        """Retrieve requests that were rate limited"""
        return await self.metricRepo.getRateLimited(limit)

    async def getErrorRequests(self, limit: int = 100) -> list[MetricSnapshot]:
        """Retrieve requests with error status codes"""
        return await self.metricRepo.getErrorRequests(limit)

    async def getMetricsByIp(self, remote_ip: str, limit: int = 100) -> list[MetricSnapshot]:
        """Retrieve all metrics for a specific IP"""
        return await self.metricRepo.getByIp(remote_ip, limit)

    async def getMetricsByUserId(self, user_id: str, limit: int = 100) -> list[MetricSnapshot]:
        """Retrieve all metrics for a specific user"""
        return await self.metricRepo.getByUserId(user_id, limit)
