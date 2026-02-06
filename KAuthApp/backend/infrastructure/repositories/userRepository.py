from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from KAuthApp.backend.domain.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def getByEmail(self, email: str) -> User | None:
        return await self.getOneByField("email", email)

    async def existsByEmail(self, email: str) -> bool:
        user = await self.getByEmail(email)
        return user is not None
