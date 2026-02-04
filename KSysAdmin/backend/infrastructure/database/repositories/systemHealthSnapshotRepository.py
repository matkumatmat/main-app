from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KSysAdmin.backend.domain.models.systemHealthSnapshot import SystemHealthSnapshot


class SystemHealthSnapshotRepository(BaseRepository[SystemHealthSnapshot]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemHealthSnapshot, session)

    async def getByTimeRange(
        self,
        start: datetime,
        end: datetime,
        limit: int = 1000
    ) -> list[SystemHealthSnapshot]:
        """Retrieve health snapshots within time range"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.timestamp >= start)
            .where(self.model.timestamp <= end)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def getLatest(self, limit: int = 10) -> list[SystemHealthSnapshot]:
        """Retrieve latest health snapshots"""
        result = await self.session.execute(
            select(self.model)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
