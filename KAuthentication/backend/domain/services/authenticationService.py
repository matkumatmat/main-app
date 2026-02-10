from __future__ import annotations
from datetime import datetime, UTC, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import secrets
import hashlib
from domain.services.passwordService import PasswordService
from domain.services.tokenService import TokenService
from domain.services.emailService import EmailService
from domain.exceptions.authenticationException import (
    InvalidCredentialsException,
    UserInactiveException,
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    InvalidVerificationTokenException,
    PasswordResetTokenInvalidException
)
from infrastructure.database.repositories.userRepository import UserRepository
from infrastructure.database.repositories.sessionRepository import SessionRepository
from shared.backend.utils.uuid import generateId
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KAuthentication")
user_logger = LoggerFactory.getUserLogger("KAuthentication")

class AuthenticationService:
    """
    Core domain service orchestrating authentication flows.
    Coordinates password, token, email, and repository operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        redis: Redis
    ):
        self.session = session
        self.redis = redis

        # Initialize domain services
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.email_service = EmailService()

        # Initialize repositories
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        fingerprint: str
    ) -> tuple[str, str, UUID]:
        """
        Register new user.
        Returns: (access_token, refresh_token, user_id)
        """
        # Check uniqueness
        if await self.user_repo.existsByEmail(email):
            raise EmailAlreadyExistsException(email)

        if await self.user_repo.existsByUsername(username):
            raise UsernameAlreadyExistsException(username)

        # Hash password
        hashed_password = self.password_service.hashPassword(password)

        # Create user (inactive until email verified)
        user_id = generateId()
        user = await self.user_repo.createUser(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            active=False
        )

        # Generate verification token
        verification_token = self._generateVerificationToken(user_id)
        await self._storeVerificationToken(user_id, verification_token)

        # Send verification email (non-blocking, failures logged but don't block registration)
        try:
            await self.email_service.sendVerificationEmail(
                email, username, verification_token
            )
        except Exception as e:
            logger.error(
                "email_verification_failed",
                user_id=str(user_id),
                email=email,
                error=str(e)
            )

        # Generate tokens
        access_token = self.token_service.generateAccessToken(
            user_id, email, fingerprint
        )
        refresh_token = self.token_service.generateRefreshToken(
            user_id, email, fingerprint
        )

        # Create session
        await self.session_repo.createSession(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            fingerprint=fingerprint,
            metadata={}  # Add user agent, IP, etc. from request context
        )

        user_logger.audit(
            action="register",
            user_id=str(user_id),
            resource=f"user:{user_id}",
            email=email
        )

        return access_token, refresh_token, user_id

    async def login(
        self,
        email: str,
        password: str,
        fingerprint: str
    ) -> tuple[str, str, UUID]:
        """
        Authenticate user and return tokens.
        Returns: (access_token, refresh_token, user_id)
        """
        user = await self.user_repo.getByEmail(email)

        if not user:
            logger.security(
                "login_failed_invalid_email",
                f"Login attempt with invalid email: {email}",
                email=email
            )
            raise InvalidCredentialsException()

        # Verify password
        if not self.password_service.verifyPassword(password, user.password):
            logger.security(
                "login_failed_invalid_password",
                f"Invalid password for user: {user.username}",
                user_id=str(user.sid),
                email=email
            )
            raise InvalidCredentialsException()

        # Check if user is active
        if not user.active:
            raise UserInactiveException()

        # Generate tokens
        access_token = self.token_service.generateAccessToken(
            user.sid, email, fingerprint
        )
        refresh_token = self.token_service.generateRefreshToken(
            user.sid, email, fingerprint
        )

        # Create session
        await self.session_repo.createSession(
            user_id=user.sid,
            access_token=access_token,
            refresh_token=refresh_token,
            fingerprint=fingerprint,
            metadata={}
        )

        user_logger.audit(
            action="login",
            user_id=str(user.sid),
            resource=f"user:{user.sid}",
            email=email
        )

        return access_token, refresh_token, user.sid

    async def verifyEmail(self, token: str) -> None:
        """Verify user email with token"""
        user_id = await self._validateVerificationToken(token)

        if not user_id:
            raise InvalidVerificationTokenException()

        # Activate user
        await self.user_repo.activateUser(user_id)

        # Delete verification token
        await self.redis.delete(f"kauth:email_verify:{token}")

        user_logger.audit(
            action="email_verified",
            user_id=str(user_id),
            resource=f"user:{user_id}"
        )

    async def refreshToken(
        self,
        refresh_token: str,
        fingerprint: str
    ) -> tuple[str, str]:
        """
        Refresh access token using refresh token.
        Returns: (new_access_token, new_refresh_token)
        """
        # Verify refresh token
        payload = self.token_service.verifyToken(refresh_token, "refresh")

        # Validate fingerprint
        if payload.fingerprint != fingerprint:
            logger.security(
                "token_refresh_fingerprint_mismatch",
                "Device fingerprint mismatch during token refresh",
                user_id=str(payload.user_id)
            )
            raise InvalidCredentialsException()

        # Check session exists in database
        session = await self.session_repo.getByRefreshToken(refresh_token)
        if not session or session.deleted:
            raise InvalidCredentialsException()

        # Generate new tokens
        new_access_token = self.token_service.generateAccessToken(
            payload.user_id, payload.email, fingerprint
        )
        new_refresh_token = self.token_service.generateRefreshToken(
            payload.user_id, payload.email, fingerprint
        )

        # Update session
        await self.session_repo.updateSession(
            session.sid,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

        return new_access_token, new_refresh_token

    async def logout(self, refresh_token: str) -> None:
        """Invalidate session and tokens"""
        session = await self.session_repo.getByRefreshToken(refresh_token)

        if session:
            await self.session_repo.invalidateSession(session.sid)

            user_logger.audit(
                action="logout",
                user_id=str(session.user_id),
                resource=f"session:{session.sid}"
            )

    async def requestPasswordReset(self, email: str) -> None:
        """Send password reset email"""
        user = await self.user_repo.getByEmail(email)

        if not user:
            # Don't reveal if email exists (security best practice)
            logger.security(
                "password_reset_unknown_email",
                f"Password reset requested for unknown email: {email}",
                email=email
            )
            return

        # Generate reset token
        reset_token = self._generatePasswordResetToken(user.sid)
        await self._storePasswordResetToken(user.sid, reset_token)

        # Send reset email (non-blocking, failures logged but don't block request)
        try:
            await self.email_service.sendPasswordResetEmail(
                email, user.username, reset_token
            )
        except Exception as e:
            logger.error(
                "password_reset_email_failed",
                user_id=str(user.sid),
                email=email,
                error=str(e)
            )

        user_logger.audit(
            action="password_reset_requested",
            user_id=str(user.sid),
            email=email
        )

    async def resetPassword(
        self,
        token: str,
        new_password: str
    ) -> None:
        """Reset password with token"""
        user_id = await self._validatePasswordResetToken(token)

        if not user_id:
            raise PasswordResetTokenInvalidException()

        # Hash new password
        hashed_password = self.password_service.hashPassword(new_password)

        # Update password
        await self.user_repo.updatePassword(user_id, hashed_password)

        # Invalidate all sessions (force re-login)
        await self.session_repo.invalidateAllUserSessions(user_id)

        # Delete reset token
        await self.redis.delete(f"kauth:password_reset:{token}")

        user_logger.audit(
            action="password_reset",
            user_id=str(user_id),
            resource=f"user:{user_id}"
        )

    async def changePassword(
        self,
        user_id: UUID,
        old_password: str,
        new_password: str
    ) -> None:
        """Change password (requires old password)"""
        user = await self.user_repo.getById(user_id)

        if not user:
            raise InvalidCredentialsException()

        # Verify old password
        if not self.password_service.verifyPassword(old_password, user.password):
            raise InvalidCredentialsException()

        # Hash new password
        hashed_password = self.password_service.hashPassword(new_password)

        # Update password
        await self.user_repo.updatePassword(user_id, hashed_password)

        # Invalidate all sessions (force re-login)
        await self.session_repo.invalidateAllUserSessions(user_id)

        user_logger.audit(
            action="password_changed",
            user_id=str(user_id),
            resource=f"user:{user_id}"
        )

    # Private helper methods

    def _generateVerificationToken(self, user_id: UUID) -> str:
        """Generate secure verification token"""
        random_part = secrets.token_urlsafe(32)
        data = f"{user_id}:{random_part}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def _storeVerificationToken(
        self,
        user_id: UUID,
        token: str
    ) -> None:
        """Store verification token in Redis (24h expiry)"""
        key = f"kauth:email_verify:{token}"
        await self.redis.setex(
            key,
            86400,  # 24 hours
            str(user_id)
        )

    async def _validateVerificationToken(self, token: str) -> UUID | None:
        """Validate and retrieve user_id from verification token"""
        key = f"kauth:email_verify:{token}"
        user_id_str = await self.redis.get(key)

        if not user_id_str:
            return None

        return UUID(user_id_str)

    def _generatePasswordResetToken(self, user_id: UUID) -> str:
        """Generate secure password reset token"""
        random_part = secrets.token_urlsafe(32)
        data = f"{user_id}:{random_part}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def _storePasswordResetToken(
        self,
        user_id: UUID,
        token: str
    ) -> None:
        """Store password reset token in Redis (1h expiry)"""
        key = f"kauth:password_reset:{token}"
        await self.redis.setex(
            key,
            3600,  # 1 hour
            str(user_id)
        )

    async def _validatePasswordResetToken(self, token: str) -> UUID | None:
        """Validate and retrieve user_id from reset token"""
        key = f"kauth:password_reset:{token}"
        user_id_str = await self.redis.get(key)

        if not user_id_str:
            return None

        return UUID(user_id_str)
