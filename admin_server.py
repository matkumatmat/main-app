from fastapi import FastAPI
from KSysAdmin.backend.infrastructure.router import router as admin_router

app = FastAPI(title='Admin Server')

# Mounting Router
app.include_router(admin_router, prefix='/api/admin', tags=['Admin'])

@app.get('/')
async def root():
    return {'server': 'admin_server', 'status': 'running'}

