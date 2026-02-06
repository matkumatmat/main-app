from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'KAuthApp', 'message': 'Authentication Service Ready'}

@router.post('/sign-up')
async def signUp():
    return f"loggin success"

@router.post('/signin')
async def signUp():
    return f"loggin success"