from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KSysAdmin.backend.domain.models.suspiciousActivity import SuspiciousActivity


class SuspiciousActivityRepository(BaseRepository[SuspiciousActivity]):
    def __init__(self, session: AsyncSession):
        super().__init__(SuspiciousActivity, session)

    async def getByIp(
        self,
        remote_ip: str,
        limit: int = 100
    ) -> list[SuspiciousActivity]:
        """Retrieve suspicious activities by IP"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.remote_ip == remote_ip)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getBySeverity(
        self,
        severity: str,
        limit: int = 100
    ) -> list[SuspiciousActivity]:
        """Retrieve activities by severity level"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.severity == severity)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getByTimeRange(
        self,
        start: datetime,
        end: datetime,
        limit: int = 1000
    ) -> list[SuspiciousActivity]:
        """Retrieve activities within time range"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.timestamp >= start)
            .where(self.model.timestamp <= end)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getRecent(self, limit: int = 50) -> list[SuspiciousActivity]:
        """Retrieve recent suspicious activities"""
        result = await self.session.execute(
            select(self.model)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
