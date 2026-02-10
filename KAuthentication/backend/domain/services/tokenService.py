from __future__ import annotations
from datetime import datetime, timedelta, UTC
from uuid import UUID
import jwt
from shared.backend.config.settings import settings
from domain.exceptions.authenticationException import (
    InvalidTokenException,
    TokenExpiredException
)

class TokenPayload:
    """Value object for JWT payload data"""
    def __init__(
        self,
        user_id: UUID,
        email: str,
        fingerprint: str,
        token_type: str,
        exp: datetime
    ):
        self.user_id = user_id
        self.email = email
        self.fingerprint = fingerprint
        self.token_type = token_type
        self.exp = exp

class TokenService:
    """
    Domain service for JWT token operations.
    Generates and validates access + refresh tokens.
    """

    def generateAccessToken(
        self,
        user_id: UUID,
        email: str,
        fingerprint: str
    ) -> str:
        """Generate short-lived access token (15-30 min)"""
        now = datetime.now(UTC)
        expiry = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

        payload = {
            "user_id": str(user_id),
            "email": email,
            "fingerprint": fingerprint,
            "token_type": "access",
            "iat": now,
            "exp": expiry
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

    def generateRefreshToken(
        self,
        user_id: UUID,
        email: str,
        fingerprint: str
    ) -> str:
        """Generate long-lived refresh token (7 days)"""
        now = datetime.now(UTC)
        expiry = now + timedelta(days=settings.jwt_refresh_token_expire_days)

        payload = {
            "user_id": str(user_id),
            "email": email,
            "fingerprint": fingerprint,
            "token_type": "refresh",
            "iat": now,
            "exp": expiry
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

    def verifyToken(self, token: str, expected_type: str) -> TokenPayload:
        """
        Verify JWT token and return payload.
        Raises InvalidTokenException or TokenExpiredException on failure.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            if payload.get("token_type") != expected_type:
                raise InvalidTokenException("Invalid token type")

            return TokenPayload(
                user_id=UUID(payload["user_id"]),
                email=payload["email"],
                fingerprint=payload["fingerprint"],
                token_type=payload["token_type"],
                exp=datetime.fromtimestamp(payload["exp"], tz=UTC)
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except (jwt.InvalidTokenError, KeyError, ValueError) as e:
            raise InvalidTokenException(str(e))
