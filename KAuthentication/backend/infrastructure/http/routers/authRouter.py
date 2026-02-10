from __future__ import annotations
from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from uuid import UUID
from shared.backend.database.engine import getDb
from shared.backend.redis.client import getRedis
from application.input.authInput import (
    RegisterInput,
    LoginInput,
    TokenRefreshInput,
    PasswordResetRequestInput,
    PasswordResetInput,
    PasswordChangeInput,
    EmailVerifyInput
)
from application.output.authOutput import (
    AuthOutput,
    UserProfileOutput,
    MessageOutput
)
from domain.services.authenticationService import AuthenticationService
from infrastructure.http.dependencies.authDependency import (
    getCurrentUser,
    getDeviceFingerprint
)
from infrastructure.database.repositories.userRepository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthOutput, status_code=201)
async def register(
    data: RegisterInput,
    response: Response,
    fingerprint: str = Depends(getDeviceFingerprint),
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Register new user account.
    Returns access + refresh tokens.
    User account inactive until email verified.
    """
    auth_service = AuthenticationService(session, redis)

    access_token, refresh_token, user_id = await auth_service.register(
        username=data.username,
        email=data.email,
        password=data.password,
        fingerprint=fingerprint
    )

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax",
        max_age=604800  # 7 days
    )

    return AuthOutput(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user_id),
        email=data.email,
        username=data.username
    )


@router.post("/login", response_model=AuthOutput)
async def login(
    data: LoginInput,
    response: Response,
    fingerprint: str = Depends(getDeviceFingerprint),
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Authenticate user with email + password.
    Returns access + refresh tokens.
    """
    auth_service = AuthenticationService(session, redis)

    access_token, refresh_token, user_id = await auth_service.login(
        email=data.email,
        password=data.password,
        fingerprint=fingerprint
    )

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800
    )

    # Get user details
    user_repo = UserRepository(session)
    user = await user_repo.getById(user_id)

    return AuthOutput(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user_id),
        email=user.email,
        username=user.username
    )


@router.post("/logout", response_model=MessageOutput)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Logout user by invalidating session.
    Clears refresh token cookie.
    """
    if refresh_token:
        auth_service = AuthenticationService(session, redis)
        await auth_service.logout(refresh_token)

    # Clear refresh token cookie
    response.delete_cookie("refresh_token")

    return MessageOutput(message="Logged out successfully")


@router.post("/refresh", response_model=AuthOutput)
async def refreshToken(
    response: Response,
    fingerprint: str = Depends(getDeviceFingerprint),
    refresh_token: str | None = Cookie(None),
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Refresh access token using refresh token.
    Returns new access + refresh tokens.
    """
    if not refresh_token:
        from domain.exceptions.authenticationException import InvalidTokenException
        raise InvalidTokenException("Refresh token required")

    auth_service = AuthenticationService(session, redis)

    new_access_token, new_refresh_token = await auth_service.refreshToken(
        refresh_token=refresh_token,
        fingerprint=fingerprint
    )

    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800
    )

    # Get user details from token
    from domain.services.tokenService import TokenService
    token_service = TokenService()
    payload = token_service.verifyToken(new_access_token, "access")

    user_repo = UserRepository(session)
    user = await user_repo.getById(payload.user_id)

    return AuthOutput(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user_id=str(payload.user_id),
        email=user.email,
        username=user.username
    )


@router.post("/verify-email", response_model=MessageOutput)
async def verifyEmail(
    data: EmailVerifyInput,
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Verify user email with token.
    Activates user account.
    """
    auth_service = AuthenticationService(session, redis)
    await auth_service.verifyEmail(data.token)

    return MessageOutput(message="Email verified successfully. Account activated.")


@router.post("/password-reset-request", response_model=MessageOutput)
async def requestPasswordReset(
    data: PasswordResetRequestInput,
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Request password reset link via email.
    Always returns success (don't reveal if email exists).
    """
    auth_service = AuthenticationService(session, redis)
    await auth_service.requestPasswordReset(data.email)

    return MessageOutput(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/password-reset", response_model=MessageOutput)
async def resetPassword(
    data: PasswordResetInput,
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Reset password using token from email.
    Invalidates all existing sessions.
    """
    auth_service = AuthenticationService(session, redis)
    await auth_service.resetPassword(
        token=data.token,
        new_password=data.new_password
    )

    return MessageOutput(message="Password reset successfully. Please login again.")


@router.post("/password-change", response_model=MessageOutput)
async def changePassword(
    data: PasswordChangeInput,
    user_id: UUID = Depends(getCurrentUser),
    session: AsyncSession = Depends(getDb),
    redis: Redis = Depends(getRedis)
):
    """
    Change password for authenticated user.
    Requires old password verification.
    Invalidates all existing sessions.
    """
    auth_service = AuthenticationService(session, redis)
    await auth_service.changePassword(
        user_id=user_id,
        old_password=data.old_password,
        new_password=data.new_password
    )

    return MessageOutput(message="Password changed successfully. Please login again.")


@router.get("/me", response_model=UserProfileOutput)
async def getCurrentUserProfile(
    user_id: UUID = Depends(getCurrentUser),
    session: AsyncSession = Depends(getDb)
):
    """
    Get current authenticated user profile.
    """
    user_repo = UserRepository(session)
    user = await user_repo.getById(user_id)

    return UserProfileOutput(
        user_id=str(user.sid),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        active=user.active,
        created_at=user.created_at
    )
