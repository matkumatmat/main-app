from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.backend.config.settings import settings
from shared.backend.database.engine import initDb, closeDb
from shared.backend.redis.client import initRedis, closeRedis
from shared.backend.middleware.corsMiddleware import addCorsMiddleware
from shared.backend.middleware.requestIdMiddleware import RequestIdMiddleware
from shared.backend.exceptions.exceptionHandlers import registerExceptionHandlers
from shared.backend.loggingFactory import LoggerFactory
from shared.backend.health.healthCheck import router as healthRouter
from KAuthApp.backend.infrastructure.router import router as authRouter
from KSysPayment.backend.infrastructure.router import router as paymentRouter

logger = LoggerFactory.getSystemLogger("PublicServer")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.application(
        label="server_startup",
        message="Starting Public Server (KAuthApp + KSysPayment)",
        environment=settings.environment,
        host=settings.public_server_host,
        port=settings.public_server_port
    )

    try:
        await initDb()
        await initRedis()
        logger.application(
            label="infrastructure_ready",
            message="Database and Redis connections established"
        )
        yield
    except Exception as e:
        logger.error(
            label="startup_failed",
            exception=e,
            message="Failed to initialize infrastructure"
        )
        raise
    finally:
        logger.application(
            label="server_shutdown",
            message="Shutting down Public Server"
        )
        await closeDb()
        await closeRedis()


app = FastAPI(
    title="KServices Public API",
    description="Authentication and Payment services combined server",
    version="1.0.0",
    docs_url="/api/docs" if settings.isDevelopment else None,
    redoc_url="/api/redoc" if settings.isDevelopment else None,
    openapi_url="/api/openapi.json" if settings.isDevelopment else None,
    lifespan=lifespan
)

addCorsMiddleware(app)
app.add_middleware(RequestIdMiddleware)

registerExceptionHandlers(app)

app.include_router(healthRouter)
app.include_router(authRouter, prefix="/api/auth", tags=["Authentication"])
app.include_router(paymentRouter, prefix="/api/payment", tags=["Payment"])


@app.get("/")
async def root():
    return {
        "services": ["KAuthApp", "KSysPayment"],
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.environment
    }
