from __future__ import annotations
from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.backend.database.engine import initDb, closeDb
from shared.backend.redis.client import initRedis, closeRedis
from shared.backend.loggingFactory import setupLogging
from shared.backend.exceptions.exceptionHandlers import registerExceptionHandlers
from shared.backend.middleware.corsMiddleware import addCorsMiddleware
from shared.backend.middleware.requestIdMiddleware import RequestIdMiddleware
from infrastructure.http.routers.authRouter import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    setupLogging()
    await initDb()
    await initRedis()
    yield
    # Shutdown
    await closeDb()
    await closeRedis()

app = FastAPI(
    title="KAuthentication API",
    description="DDD-based authentication service with JWT + Cookie auth",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(RequestIdMiddleware)
addCorsMiddleware(app)

# Exception handlers
registerExceptionHandlers(app)

# Routers
app.include_router(auth_router, prefix="/api")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KAuthentication"}
