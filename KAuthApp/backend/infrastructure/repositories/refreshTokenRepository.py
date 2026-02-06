from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KAuthApp.backend.domain.models.refreshToken import RefreshToken

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def getByTokenHash(self, token_hash: str) -> RefreshToken | None:
        return await self.getOneByField("token_hash", token_hash)
