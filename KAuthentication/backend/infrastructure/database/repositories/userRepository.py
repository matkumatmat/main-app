from __future__ import annotations
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from domain.client.models.UserProfileModels import UserModel

class UserRepository(BaseRepository[UserModel]):
    """Repository for User entity operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)

    async def getById(self, user_id: UUID) -> UserModel | None:
        """Get user by ID (overrides base to use 'sid' field)"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.sid == user_id)
        )
        return result.scalar_one_or_none()

    async def createUser(
        self,
        user_id: UUID,
        username: str,
        email: str,
        hashed_password: str,
        active: bool = False
    ) -> UserModel:
        """Create new user"""
        user = UserModel(
            sid=user_id,
            username=username,
            email=email,
            password=hashed_password,
            active=active,
            actived_at=None
        )
        return await self.create(user)

    async def getByEmail(self, email: str) -> UserModel | None:
        """Get user by email"""
        return await self.getOneByField("email", email)

    async def getByUsername(self, username: str) -> UserModel | None:
        """Get user by username"""
        return await self.getOneByField("username", username)

    async def existsByEmail(self, email: str) -> bool:
        """Check if email exists"""
        result = await self.session.execute(
            select(UserModel.sid).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def existsByUsername(self, username: str) -> bool:
        """Check if username exists"""
        result = await self.session.execute(
            select(UserModel.sid).where(UserModel.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def activateUser(self, user_id: UUID) -> None:
        """Activate user account"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.sid == user_id)
            .values(
                active=True,
                actived_at=datetime.now(UTC)
            )
        )
        await self.session.flush()

    async def updatePassword(
        self,
        user_id: UUID,
        hashed_password: str
    ) -> None:
        """Update user password"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.sid == user_id)
            .values(password=hashed_password)
        )
        await self.session.flush()
