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
from KSysAdmin.backend.infrastructure.http.routers.monitoringRouter import router as monitoringRouter
from KSysAdmin.backend.infrastructure.http.routers.healthRouter import router as healthMonitoringRouter
from KSysAdmin.backend.infrastructure.http.routers.securityRouter import router as securityRouter
from KSysAdmin.backend.infrastructure.http.routers.aggregationRouter import router as aggregationRouter

logger = LoggerFactory.getSystemLogger("AdminServer")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.application(
        label="server_startup",
        message="Starting Admin Server (KSysAdmin)",
        environment=settings.environment,
        host=settings.admin_server_host,
        port=settings.admin_server_port
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
            message="Shutting down Admin Server"
        )
        await closeDb()
        await closeRedis()


app = FastAPI(
    title="KSysAdmin - Admin System API",
    description="System administration, monitoring, and analytics service",
    version="1.0.0",
    docs_url="/api/admin/docs" if settings.isDevelopment else None,
    redoc_url="/api/admin/redoc" if settings.isDevelopment else None,
    openapi_url="/api/admin/openapi.json" if settings.isDevelopment else None,
    lifespan=lifespan
)

addCorsMiddleware(app)
app.add_middleware(RequestIdMiddleware)

registerExceptionHandlers(app)

app.include_router(healthRouter)
app.include_router(monitoringRouter, prefix="/api/admin")
app.include_router(healthMonitoringRouter, prefix="/api/admin")
app.include_router(securityRouter, prefix="/api/admin")
app.include_router(aggregationRouter, prefix="/api/admin")


@app.get("/")
async def root():
    return {
        "service": "KSysAdmin",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.environment
    }
