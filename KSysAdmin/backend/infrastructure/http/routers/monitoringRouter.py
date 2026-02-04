from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getDb
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey
from KSysAdmin.backend.domain.services.monitoringService import MonitoringService

router = APIRouter(prefix='/monitoring', tags=['Monitoring'], dependencies=[Depends(verifyAdminHashKey)])


@router.get('/metrics')
async def getMetrics(
    service: str = Query(..., description="Service name (kauth, ksysadmin, ksyspayment)"),
    start: datetime | None = Query(None, description="Start time (ISO format)"),
    end: datetime | None = Query(None, description="End time (ISO format)"),
    limit: int = Query(1000, ge=1, le=10000),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve metrics for a service, optionally within time range"""
    monitoring = MonitoringService(session)
    metrics = await monitoring.getServiceMetrics(service, start, end, limit)

    return {
        "service": service,
        "count": len(metrics),
        "start": start,
        "end": end,
        "metrics": [
            {
                "id": str(m.id),
                "timestamp": m.timestamp,
                "remote_ip": m.remote_ip,
                "request_id": m.request_id,
                "method": m.method,
                "url": m.url,
                "status": m.status,
                "rate_limited": m.rate_limited,
                "nginx_latency_ms": m.nginx_latency_ms,
                "backend_latency_ms": m.backend_latency_ms,
                "user_id": m.user_id
            }
            for m in metrics
        ]
    }


@router.get('/metrics/hourly')
async def getHourlyAggregation(
    service: str = Query(..., description="Service name"),
    start: datetime | None = Query(None, description="Start time (ISO format)"),
    end: datetime | None = Query(None, description="End time (ISO format)"),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve hourly aggregated metrics for a service"""
    monitoring = MonitoringService(session)
    aggregations = await monitoring.getHourlyAggregation(service, start, end)

    return {
        "service": service,
        "count": len(aggregations),
        "aggregations": [
            {
                "id": str(a.id),
                "hour_start": a.hour_start,
                "service": a.service,
                "total_requests": a.total_requests,
                "successful_requests": a.successful_requests,
                "client_errors": a.client_errors,
                "server_errors": a.server_errors,
                "rate_limited_requests": a.rate_limited_requests,
                "avg_nginx_latency_ms": a.avg_nginx_latency_ms,
                "avg_backend_latency_ms": a.avg_backend_latency_ms,
                "p95_nginx_latency_ms": a.p95_nginx_latency_ms,
                "p95_backend_latency_ms": a.p95_backend_latency_ms,
                "unique_ips": a.unique_ips
            }
            for a in aggregations
        ]
    }


@router.get('/metrics/rate-limited')
async def getRateLimitedRequests(
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve requests that were rate limited"""
    monitoring = MonitoringService(session)
    metrics = await monitoring.getRateLimitedRequests(limit)

    return {
        "count": len(metrics),
        "rate_limited_requests": [
            {
                "id": str(m.id),
                "timestamp": m.timestamp,
                "service": m.service,
                "remote_ip": m.remote_ip,
                "url": m.url,
                "user_id": m.user_id
            }
            for m in metrics
        ]
    }


@router.get('/metrics/errors')
async def getErrorRequests(
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve requests with error status codes (4xx, 5xx)"""
    monitoring = MonitoringService(session)
    metrics = await monitoring.getErrorRequests(limit)

    return {
        "count": len(metrics),
        "error_requests": [
            {
                "id": str(m.id),
                "timestamp": m.timestamp,
                "service": m.service,
                "remote_ip": m.remote_ip,
                "method": m.method,
                "url": m.url,
                "status": m.status,
                "backend_latency_ms": m.backend_latency_ms
            }
            for m in metrics
        ]
    }


@router.get('/metrics/by-ip/{remote_ip}')
async def getMetricsByIp(
    remote_ip: str,
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve all metrics for a specific IP address"""
    monitoring = MonitoringService(session)
    metrics = await monitoring.getMetricsByIp(remote_ip, limit)

    return {
        "remote_ip": remote_ip,
        "count": len(metrics),
        "metrics": [
            {
                "id": str(m.id),
                "timestamp": m.timestamp,
                "service": m.service,
                "method": m.method,
                "url": m.url,
                "status": m.status,
                "rate_limited": m.rate_limited
            }
            for m in metrics
        ]
    }
