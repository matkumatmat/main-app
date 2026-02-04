from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.infrastructure.database.repositories.systemHealthSnapshotRepository import SystemHealthSnapshotRepository
from KSysAdmin.backend.domain.models.systemHealthSnapshot import SystemHealthSnapshot


class HealthCheckService:
    """
    Domain service for system health monitoring.
    Manages health snapshots and status tracking.
    """

    def __init__(self, session: AsyncSession):
        self.repo = SystemHealthSnapshotRepository(session)

    async def recordHealthSnapshot(
        self,
        db_status: str,
        db_latency_ms: float,
        redis_status: str,
        redis_latency_ms: float,
        crypto_status: str
    ) -> SystemHealthSnapshot:
        """Record a new system health snapshot"""
        snapshot = SystemHealthSnapshot(
            timestamp=datetime.utcnow(),
            db_status=db_status,
            db_latency_ms=db_latency_ms,
            redis_status=redis_status,
            redis_latency_ms=redis_latency_ms,
            crypto_status=crypto_status
        )
        return await self.repo.create(snapshot)

    async def getLatestHealth(self, limit: int = 10) -> list[SystemHealthSnapshot]:
        """Retrieve latest health snapshots"""
        return await self.repo.getLatest(limit)

    async def getHealthHistory(
        self,
        start: datetime,
        end: datetime,
        limit: int = 1000
    ) -> list[SystemHealthSnapshot]:
        """Retrieve health snapshots within time range"""
        return await self.repo.getByTimeRange(start, end, limit)

    def analyzeHealth(self, snapshots: list[SystemHealthSnapshot]) -> dict:
        """
        Analyze health snapshots and return summary.
        Business logic for health status evaluation.
        """
        if not snapshots:
            return {
                "status": "unknown",
                "db_availability": 0.0,
                "redis_availability": 0.0,
                "avg_db_latency": 0.0,
                "avg_redis_latency": 0.0
            }

        total = len(snapshots)
        db_healthy = sum(1 for s in snapshots if s.db_status == "healthy")
        redis_healthy = sum(1 for s in snapshots if s.redis_status == "healthy")

        avg_db_latency = sum(s.db_latency_ms for s in snapshots) / total
        avg_redis_latency = sum(s.redis_latency_ms for s in snapshots) / total

        overall_status = "healthy"
        if db_healthy / total < 0.95 or redis_healthy / total < 0.95:
            overall_status = "degraded"
        if db_healthy / total < 0.5 or redis_healthy / total < 0.5:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "db_availability": round(db_healthy / total * 100, 2),
            "redis_availability": round(redis_healthy / total * 100, 2),
            "avg_db_latency": round(avg_db_latency, 2),
            "avg_redis_latency": round(avg_redis_latency, 2),
            "total_snapshots": total
        }
