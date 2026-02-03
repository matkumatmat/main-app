from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from KAuthApp.backend.infrastructure.router import router as auth_router
from KSysPayment.backend.infrastructure.router import router as payment_router
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


app = FastAPI(title='Public Server (Auth & Payment)', lifespan=lifespan)

registerExceptionHandlers(app)

app.add_middleware(RequestIdMiddleware)
addCorsMiddleware(app)

app.include_router(auth_router, prefix='/api/auth', tags=['Authentication'])
app.include_router(payment_router, prefix='/api/payment', tags=['Payment'])


@app.get('/')
async def root():
    return {'server': 'public_server', 'status': 'running'}


@app.get('/health')
async def health():
    return await performHealthCheck()

