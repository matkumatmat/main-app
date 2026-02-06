from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getDb
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey
from KSysAdmin.backend.domain.services.healthCheckService import HealthCheckService

router = APIRouter(prefix='/health-monitoring', tags=['Health'], dependencies=[Depends(verifyAdminHashKey)])


@router.get('/snapshots/latest')
async def getLatestHealthSnapshots(
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve latest system health snapshots"""
    health_service = HealthCheckService(session)
    snapshots = await health_service.getLatestHealth(limit)

    return {
        "count": len(snapshots),
        "snapshots": [
            {
                "id": str(s.id),
                "timestamp": s.timestamp,
                "db_status": s.db_status,
                "db_latency_ms": s.db_latency_ms,
                "redis_status": s.redis_status,
                "redis_latency_ms": s.redis_latency_ms,
                "crypto_status": s.crypto_status
            }
            for s in snapshots
        ]
    }


@router.get('/snapshots/history')
async def getHealthHistory(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve health snapshots within time range"""
    # Strip timezone info to match database TIMESTAMP WITHOUT TIME ZONE
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    health_service = HealthCheckService(session)
    snapshots = await health_service.getHealthHistory(start, end, limit)

    return {
        "start": start,
        "end": end,
        "count": len(snapshots),
        "snapshots": [
            {
                "id": str(s.id),
                "timestamp": s.timestamp,
                "db_status": s.db_status,
                "db_latency_ms": s.db_latency_ms,
                "redis_status": s.redis_status,
                "redis_latency_ms": s.redis_latency_ms,
                "crypto_status": s.crypto_status
            }
            for s in snapshots
        ]
    }


@router.get('/analysis')
async def analyzeHealthStatus(
    start: datetime = Query(..., description="Start time for analysis"),
    end: datetime = Query(..., description="End time for analysis"),
    session: AsyncSession = Depends(getDb)
):
    """Analyze health snapshots and return summary statistics"""
    # Strip timezone info to match database TIMESTAMP WITHOUT TIME ZONE
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    health_service = HealthCheckService(session)
    snapshots = await health_service.getHealthHistory(start, end, 10000)
    analysis = health_service.analyzeHealth(snapshots)

    return {
        "time_range": {"start": start, "end": end},
        "analysis": analysis
    }
