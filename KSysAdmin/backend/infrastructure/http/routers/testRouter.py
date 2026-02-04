from __future__ import annotations
from fastapi import APIRouter, Depends
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey

router = APIRouter(prefix='/test', tags=['Test'])

@router.get('/', dependencies=[Depends(verifyAdminHashKey)])
async def testAuth() -> dict:
    return {
        'status': 'success',
        'message': 'Admin authentication successful',
        'authenticated': True
    }
