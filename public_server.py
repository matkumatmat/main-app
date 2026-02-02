from fastapi import FastAPI
from KAuthApp.backend.infrastructure.router import router as auth_router
from KSysPayment.backend.infrastructure.router import router as payment_router

app = FastAPI(title='Public Server (Auth & Payment)')

# Mounting Router
app.include_router(auth_router, prefix='/api/auth', tags=['Authentication'])
app.include_router(payment_router, prefix='/api/payment', tags=['Payment'])

@app.get('/')
async def root():
    return {'server': 'public_server', 'status': 'running'}

