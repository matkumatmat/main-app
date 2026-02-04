from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot


class MetricSnapshotRepository(BaseRepository[MetricSnapshot]):
    def __init__(self, session: AsyncSession):
        super().__init__(MetricSnapshot, session)

    async def getByService(
        self,
        service: str,
        limit: int = 1000
    ) -> list[MetricSnapshot]:
        """Retrieve metrics by service"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.service == service)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getByIp(
        self,
        remote_ip: str,
        limit: int = 100
    ) -> list[MetricSnapshot]:
        """Retrieve metrics by IP"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.remote_ip == remote_ip)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getByUserId(
        self,
        user_id: str,
        limit: int = 100
    ) -> list[MetricSnapshot]:
        """Retrieve metrics by user ID"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getByTimeRange(
        self,
        start: datetime,
        end: datetime,
        service: str | None = None,
        limit: int = 10000
    ) -> list[MetricSnapshot]:
        """Retrieve metrics within time range, optionally filtered by service"""
        query = select(self.model).where(
            self.model.timestamp >= start,
            self.model.timestamp <= end
        )

        if service:
            query = query.where(self.model.service == service)

        query = query.order_by(desc(self.model.timestamp)).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def getRateLimited(
        self,
        limit: int = 100
    ) -> list[MetricSnapshot]:
        """Retrieve rate-limited requests"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.rate_limited == True)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getErrorRequests(
        self,
        limit: int = 100
    ) -> list[MetricSnapshot]:
        """Retrieve error requests (status >= 400)"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.status >= 400)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def countByService(self, service: str) -> int:
        """Count total requests for service"""
        result = await self.session.execute(
            select(func.count()).where(self.model.service == service)
        )
        return result.scalar_one()
