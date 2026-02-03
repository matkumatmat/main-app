from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from KSysAdmin.backend.infrastructure.router import router as admin_router
from shared.backend.loggingFactory import setupLogging
from shared.backend.database.engine import initDb, closeDb
from shared.backend.redis.client import initRedis, closeRedis
from shared.backend.exceptions import registerExceptionHandlers
from shared.backend.middleware import RequestIdMiddleware, addCorsMiddleware
from shared.backend.health import performHealthCheck


@asynccontextmanager
async def lifespan(app: FastAPI):
    setupLogging()
    await initDb()
    await initRedis()
    yield
    await closeDb()
    await closeRedis()


app = FastAPI(title='Admin Server', lifespan=lifespan)

registerExceptionHandlers(app)

app.add_middleware(RequestIdMiddleware)
addCorsMiddleware(app)

app.include_router(admin_router, prefix='/api/admin', tags=['Admin'])


@app.get('/')
async def root():
    return {'server': 'admin_server', 'status': 'running'}


@app.get('/health')
async def health():
    return await performHealthCheck()

