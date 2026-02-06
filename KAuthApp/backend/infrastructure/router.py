from __future__ import annotations
from fastapi import APIRouter, Depends, Header
from typing import Annotated

from KAuthApp.backend.application.services.authService import AuthService, getAuthService
from KAuthApp.backend.application.dto.authDTO import (
    SignUpInput, SignInInput, VerifyOtpInput, ResendOtpInput, RefreshTokenInput,
    AuthResponse, AuthData, RefreshTokenData
)

router = APIRouter()

@router.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'KAuthApp', 'message': 'Authentication Service Ready'}

@router.post('/signup', response_model=AuthResponse[AuthData])
async def signUp(
    input: SignUpInput,
    service: AuthService = Depends(getAuthService)
):
    result = await service.signUp(input)
    return AuthResponse(success=True, data=result)

@router.post('/signin', response_model=AuthResponse[AuthData])
async def signIn(
    input: SignInInput,
    service: AuthService = Depends(getAuthService)
):
    result = await service.signIn(input)
    return AuthResponse(success=True, data=result)

@router.post('/verify-otp', response_model=AuthResponse[AuthData])
async def verifyOtp(
    input: VerifyOtpInput,
    service: AuthService = Depends(getAuthService)
):
    result = await service.verifyOtp(input)
    return AuthResponse(success=True, data=result)

@router.post('/resend-otp', response_model=AuthResponse[AuthData])
async def resendOtp(
    input: ResendOtpInput,
    service: AuthService = Depends(getAuthService)
):
    result = await service.resendOtp(input)
    return AuthResponse(success=True, data=result)

@router.post('/refresh', response_model=AuthResponse[RefreshTokenData])
async def refreshToken(
    input: RefreshTokenInput,
    service: AuthService = Depends(getAuthService)
):
    result = await service.refreshToken(input.refreshToken)
    return AuthResponse(success=True, data=result)

@router.post('/signout', response_model=AuthResponse[AuthData])
async def signOut(
    authorization: Annotated[str, Header()],
    service: AuthService = Depends(getAuthService)
):
    token = authorization.replace("Bearer ", "")
    result = await service.signOut(token)
    return AuthResponse(success=True, data=result)
