from __future__ import annotations
from uuid import UUID
from datetime import datetime, UTC, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.baseRepository import BaseRepository
from domain.client.models.UserSessionModels import SessionModel
from shared.backend.utils.uuid import generateId
import secrets

class SessionRepository(BaseRepository[SessionModel]):
    """Repository for Session entity operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(SessionModel, session)

    async def createSession(
        self,
        user_id: UUID,
        access_token: str,
        refresh_token: str,
        fingerprint: str,
        metadata: dict
    ) -> SessionModel:
        """Create new session"""
        session_id = generateId()
        cookie_id = secrets.token_urlsafe(32)

        now = datetime.utcnow()
        expiry = now + timedelta(days=7)  # 7 days session expiry

        session_obj = SessionModel(
            sid=session_id,
            user_id=user_id,
            active=now,
            expiry=expiry,
            access_token=access_token,
            refresh_token=refresh_token,
            fingerprint=fingerprint,
            cookie=cookie_id,
            session_metadata=str(metadata)  # Store as JSON string
        )

        return await self.create(session_obj)

    async def getByRefreshToken(self, refresh_token: str) -> SessionModel | None:
        """Get session by refresh token"""
        return await self.getOneByField("refresh_token", refresh_token)

    async def getByAccessToken(self, access_token: str) -> SessionModel | None:
        """Get session by access token"""
        return await self.getOneByField("access_token", access_token)

    async def updateSession(
        self,
        session_id: UUID,
        access_token: str,
        refresh_token: str
    ) -> None:
        """Update session tokens"""
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.sid == session_id)
            .values(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
        await self.session.flush()

    async def invalidateSession(self, session_id: UUID) -> None:
        """Invalidate session (soft delete)"""
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.sid == session_id)
            .values(deleted=True, deleted_at=datetime.utcnow())
        )
        await self.session.flush()

    async def invalidateAllUserSessions(self, user_id: UUID) -> None:
        """Invalidate all sessions for a user"""
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.user_id == user_id)
            .values(deleted=True, deleted_at=datetime.utcnow())
        )
        await self.session.flush()

    async def cleanupExpiredSessions(self) -> int:
        """Delete expired sessions (cleanup task)"""
        now = datetime.now(UTC)
        result = await self.session.execute(
            update(SessionModel)
            .where(SessionModel.expiry < now)
            .values(deleted=True, deleted_at=now)
        )
        await self.session.flush()
        return result.rowcount or 0
