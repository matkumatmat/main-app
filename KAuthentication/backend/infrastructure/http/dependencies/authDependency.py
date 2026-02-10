from __future__ import annotations
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from shared.backend.database.engine import getDb
from domain.services.tokenService import TokenService
from domain.exceptions.authenticationException import InvalidTokenException

security = HTTPBearer()

async def getCurrentUser(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(getDb)
) -> UUID:
    """
    Extract and validate current user from JWT access token.
    Used as FastAPI dependency for protected routes.
    """
    token = credentials.credentials

    token_service = TokenService()
    payload = token_service.verifyToken(token, "access")

    return payload.user_id

async def getDeviceFingerprint(
    x_device_fingerprint: str | None = Header(None)
) -> str:
    """
    Extract device fingerprint from request headers.
    Frontend should send hash of (User-Agent + Screen Resolution + Timezone + etc.)
    """
    if not x_device_fingerprint:
        raise InvalidTokenException("Device fingerprint required")

    return x_device_fingerprint
