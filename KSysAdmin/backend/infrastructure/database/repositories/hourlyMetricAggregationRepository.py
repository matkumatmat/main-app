from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KSysAdmin.backend.domain.models.hourlyMetricAggregation import HourlyMetricAggregation


class HourlyMetricAggregationRepository(BaseRepository[HourlyMetricAggregation]):
    def __init__(self, session: AsyncSession):
        super().__init__(HourlyMetricAggregation, session)

    async def getByService(
        self,
        service: str,
        limit: int = 168  # 1 week of hourly data
    ) -> list[HourlyMetricAggregation]:
        """Retrieve metrics by service"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.service == service)
            .order_by(desc(self.model.hour_start))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getByServiceAndTimeRange(
        self,
        service: str,
        start: datetime,
        end: datetime
    ) -> list[HourlyMetricAggregation]:
        """Retrieve metrics by service within time range"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.service == service)
            .where(self.model.hour_start >= start)
            .where(self.model.hour_start <= end)
            .order_by(desc(self.model.hour_start))
        )
        return list(result.scalars().all())

    async def getLatestForAllServices(self, limit_per_service: int = 24) -> list[HourlyMetricAggregation]:
        """Retrieve latest metrics for all services"""
        result = await self.session.execute(
            select(self.model)
            .order_by(desc(self.model.hour_start))
            .limit(limit_per_service * 3)  # Assuming 3 services max
        )
        return list(result.scalars().all())
