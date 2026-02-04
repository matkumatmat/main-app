from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from KSysAdmin.backend.infrastructure.router import router as admin_router
from KSysAdmin.backend.infrastructure.http.routers.testRouter import router as test_router
from KSysAdmin.backend.infrastructure.http.routers.monitoringRouter import router as monitoring_router
from KSysAdmin.backend.infrastructure.http.routers.healthRouter import router as health_router
from KSysAdmin.backend.infrastructure.http.routers.securityRouter import router as security_router
from KSysAdmin.backend.infrastructure.http.routers.aggregationRouter import router as aggregation_router
from KSysAdmin.backend.infrastructure.collectors.metricCollectionTask import MetricCollectionTask
from KSysAdmin.backend.infrastructure.tasks.aggregationTask import AggregationTask
from shared.backend.loggingFactory import setupLogging
from shared.backend.database.engine import initDb, closeDb
from shared.backend.redis.client import initRedis, closeRedis
from shared.backend.exceptions import registerExceptionHandlers
from shared.backend.middleware import RequestIdMiddleware, addCorsMiddleware
from shared.backend.health import performHealthCheck

# Global task instances
collection_task: MetricCollectionTask | None = None
aggregation_task: AggregationTask | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global collection_task, aggregation_task

    # Startup
    setupLogging()
    await initDb()
    await initRedis()

    # Start metric collection task
    collection_task = MetricCollectionTask()
    collection_task.start()

    # Start aggregation tasks
    aggregation_task = AggregationTask()
    aggregation_task.start()

    yield

    # Shutdown
    if aggregation_task:
        await aggregation_task.stop()
    if collection_task:
        await collection_task.stop()
    await closeDb()
    await closeRedis()


app = FastAPI(title='Admin Server', lifespan=lifespan)

registerExceptionHandlers(app)

app.add_middleware(RequestIdMiddleware)
addCorsMiddleware(app)

app.include_router(admin_router, prefix='/api/admin', tags=['Admin'])
app.include_router(test_router, prefix='/api/admin', tags=['Test'])
app.include_router(monitoring_router, prefix='/api/admin', tags=['Monitoring'])
app.include_router(health_router, prefix='/api/admin', tags=['Health'])
app.include_router(security_router, prefix='/api/admin', tags=['Security'])
app.include_router(aggregation_router, prefix='/api/admin', tags=['Aggregation'])


@app.get('/')
async def root():
    return {'server': 'admin_server', 'status': 'running'}


@app.get('/health')
async def health():
    return await performHealthCheck()

