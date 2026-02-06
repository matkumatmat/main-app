from __future__ import annotations
import uuid
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Tuple
from argon2 import PasswordHasher
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from shared.backend.database.engine import getDb
from shared.backend.redis.client import getRedis
from shared.backend.config.settings import settings
from shared.backend.utils.uuid import generateId

from KAuthApp.backend.domain.models.user import User
from KAuthApp.backend.domain.models.refreshToken import RefreshToken
from KAuthApp.backend.domain.exceptions.authExceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotVerifiedException,
    InvalidOtpException,
    InvalidTokenException,
    RateLimitException
)
from KAuthApp.backend.infrastructure.repositories.userRepository import UserRepository
from KAuthApp.backend.infrastructure.repositories.refreshTokenRepository import RefreshTokenRepository
from KAuthApp.backend.infrastructure.email.mockEmailService import MockEmailService
from KAuthApp.backend.application.dto.authDTO import (
    SignUpInput, SignInInput, VerifyOtpInput, ResendOtpInput,
    UserDTO, TokenDTO, AuthData, RefreshTokenData
)

ph = PasswordHasher()

class AuthService:
    def __init__(
        self,
        userRepo: UserRepository,
        tokenRepo: RefreshTokenRepository,
        redis: Redis
    ):
        self.userRepo = userRepo
        self.tokenRepo = tokenRepo
        self.redis = redis

    async def signUp(self, input: SignUpInput) -> AuthData:
        if await self.userRepo.existsByEmail(input.email):
            raise UserAlreadyExistsException(input.email)

        # Hash password
        password_hash = ph.hash(input.password)

        # Create user
        user = User(
            id=generateId(),
            email=input.email,
            full_name=input.fullName,
            password_hash=password_hash,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.userRepo.create(user)

        # Generate and send OTP
        await self._generateAndSendOtp(user.email)

        return AuthData(
            user=self._mapUserToDTO(user),
            message="Account created successfully. Please verify your email."
        )

    async def signIn(self, input: SignInInput) -> AuthData:
        user = await self.userRepo.getByEmail(input.email)
        if not user:
            raise InvalidCredentialsException()

        try:
            ph.verify(user.password_hash, input.password)
        except:
            raise InvalidCredentialsException()

        if not user.is_verified:
             raise UserNotVerifiedException()

        tokens = await self._generateTokens(user.id)

        return AuthData(
            user=self._mapUserToDTO(user),
            tokens=tokens
        )

    async def verifyOtp(self, input: VerifyOtpInput) -> AuthData:
        otpKey = f"kauth:otp:{input.email}"
        storedOtp = await self.redis.get(otpKey)

        if not storedOtp or storedOtp.decode() != input.otp:
            raise InvalidOtpException()

        # Clear OTP
        await self.redis.delete(otpKey)

        user = await self.userRepo.getByEmail(input.email)
        if not user:
            raise InvalidCredentialsException()

        if not user.is_verified:
            user.is_verified = True
            await self.userRepo.update(user.id, {"is_verified": True})

        tokens = await self._generateTokens(user.id)

        return AuthData(
            user=self._mapUserToDTO(user),
            tokens=tokens,
            message="Email verified successfully"
        )

    async def resendOtp(self, input: ResendOtpInput) -> AuthData:
        user = await self.userRepo.getByEmail(input.email)
        # We process even if user not found to prevent enumeration, or if strictly required check exists.

        limitKey = f"rate_limit:otp_resend:{input.email}"

        if await self.redis.exists(limitKey):
            raise RateLimitException()

        await self._generateAndSendOtp(input.email)
        await self.redis.setex(limitKey, 60, "1")

        return AuthData(message="OTP sent successfully")

    async def refreshToken(self, refreshToken: str) -> RefreshTokenData:
        try:
            payload = jwt.decode(refreshToken, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            token_type = payload.get("type")
            if token_type != "refresh":
                raise InvalidTokenException()

            tokenHash = self._hashToken(refreshToken)
            storedToken = await self.tokenRepo.getByTokenHash(tokenHash)

            if not storedToken or storedToken.revoked:
                raise InvalidTokenException()

            userId = uuid.UUID(payload.get("sub"))

            newAccessToken = self._createAccessToken(userId)

            return RefreshTokenData(
                accessToken=newAccessToken,
                expiresIn=settings.jwt_access_token_expire_minutes * 60
            )

        except jwt.PyJWTError:
            raise InvalidTokenException()

    async def signOut(self, token: str) -> AuthData:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            exp = payload.get("exp")
            if exp:
                now = datetime.utcnow().timestamp()
                ttl = int(exp - now)
                if ttl > 0:
                    await self.redis.setex(f"kauth:blacklist:{token}", ttl, "1")
        except Exception:
            # We don't want to fail signout even if token is invalid
            pass

        return AuthData(message="Signed out successfully")

    async def _generateAndSendOtp(self, email: str):
        otp = "".join([secrets.choice("0123456789") for _ in range(6)])
        await self.redis.setex(f"kauth:otp:{email}", 600, otp)
        await MockEmailService.sendOtpEmail(email, otp)

    async def _generateTokens(self, userId: uuid.UUID) -> TokenDTO:
        accessToken = self._createAccessToken(userId)
        refreshToken = self._createRefreshToken(userId)

        tokenHash = self._hashToken(refreshToken)
        dbToken = RefreshToken(
            id=generateId(),
            user_id=userId,
            token_hash=tokenHash,
            expires_at=datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days),
            revoked=False,
            created_at=datetime.utcnow()
        )
        await self.tokenRepo.create(dbToken)

        return TokenDTO(
            accessToken=accessToken,
            refreshToken=refreshToken,
            expiresIn=settings.jwt_access_token_expire_minutes * 60
        )

    def _createAccessToken(self, userId: uuid.UUID) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        to_encode = {"sub": str(userId), "type": "access", "exp": expire}
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def _createRefreshToken(self, userId: uuid.UUID) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        to_encode = {"sub": str(userId), "type": "refresh", "exp": expire, "jti": str(uuid.uuid4())}
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def _hashToken(self, token: str) -> str:
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    def _mapUserToDTO(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            isVerified=user.is_verified,
            createdAt=user.created_at
        )

def getAuthService(
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
) -> AuthService:
    userRepo = UserRepository(session)
    tokenRepo = RefreshTokenRepository(session)
    return AuthService(userRepo, tokenRepo, redis)
