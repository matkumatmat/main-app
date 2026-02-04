from __future__ import annotations
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getDb
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey
from KSysAdmin.backend.domain.services.aggregation.aggregationService import AggregationService
from KSysAdmin.backend.domain.services.aggregation.securityAnalysisService import SecurityAnalysisService
from KSysAdmin.backend.domain.services.aggregation.retentionService import RetentionService

router = APIRouter(prefix='/aggregation', tags=['Aggregation'], dependencies=[Depends(verifyAdminHashKey)])


@router.post('/trigger/hourly')
async def triggerHourlyAggregation(
    hour: datetime | None = Query(None, description="Hour to aggregate (default: previous hour)"),
    session: AsyncSession = Depends(getDb)
):
    """Manually trigger hourly aggregation for specific hour"""
    aggregation_service = AggregationService(session)

    # Default to previous hour if not specified
    if not hour:
        now = datetime.utcnow().replace(tzinfo=None)
        hour = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

    services = ['kauth', 'ksysadmin', 'ksyspayment', 'nginx_gateway']

    results = await aggregation_service.aggregateMultipleHours(
        services=services,
        start_hour=hour,
        end_hour=hour + timedelta(hours=1)
    )

    await session.commit()

    return {
        "status": "success",
        "hour": hour.isoformat(),
        "services_aggregated": sum(results.values()),
        "details": results
    }


@router.post('/trigger/security-analysis')
async def triggerSecurityAnalysis(
    session: AsyncSession = Depends(getDb)
):
    """Manually trigger security analysis"""
    security_service = SecurityAnalysisService(session)
    detected_count = await security_service.runAnalysis()

    await session.commit()

    return {
        "status": "success",
        "suspicious_activities_detected": detected_count
    }


@router.post('/trigger/cleanup')
async def triggerCleanup(
    retention_days: int | None = Query(None, description="Override retention days"),
    session: AsyncSession = Depends(getDb)
):
    """Manually trigger retention cleanup"""
    retention_service = RetentionService(session)

    if retention_days:
        results = {
            'metric_snapshots': await retention_service.cleanupMetricSnapshots(retention_days),
            'health_snapshots': await retention_service.cleanupHealthSnapshots(retention_days),
            'suspicious_activities': await retention_service.cleanupSuspiciousActivities(retention_days),
            'rate_violations': await retention_service.cleanupRateLimitViolations(retention_days),
            'hourly_aggregations': await retention_service.cleanupHourlyAggregations(retention_days)
        }
    else:
        results = await retention_service.runFullCleanup()

    await session.commit()

    return {
        "status": "success",
        "total_deleted": sum(results.values()),
        "details": results
    }
