from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'KAuthApp', 'message': 'Authentication Service Ready'}

