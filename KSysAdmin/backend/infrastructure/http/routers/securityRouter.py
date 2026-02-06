from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getDb
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey
from KSysAdmin.backend.domain.services.securityService import SecurityService

router = APIRouter(prefix='/security', tags=['Security'], dependencies=[Depends(verifyAdminHashKey)])


@router.get('/suspicious-activities/recent')
async def getRecentSuspiciousActivities(
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve recent suspicious activities"""
    security_service = SecurityService(session)
    activities = await security_service.getRecentSuspiciousActivities(limit)

    return {
        "count": len(activities),
        "activities": [
            {
                "id": str(a.id),
                "timestamp": a.timestamp,
                "remote_ip": a.remote_ip,
                "activity_type": a.activity_type,
                "severity": a.severity,
                "details": a.details
            }
            for a in activities
        ]
    }


@router.get('/suspicious-activities/by-ip/{remote_ip}')
async def getSuspiciousActivitiesByIp(
    remote_ip: str,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve suspicious activities for a specific IP"""
    security_service = SecurityService(session)
    activities = await security_service.getSuspiciousActivitiesByIp(remote_ip, limit)

    return {
        "remote_ip": remote_ip,
        "count": len(activities),
        "activities": [
            {
                "id": str(a.id),
                "timestamp": a.timestamp,
                "activity_type": a.activity_type,
                "severity": a.severity,
                "details": a.details
            }
            for a in activities
        ]
    }


@router.get('/suspicious-activities/by-severity/{severity}')
async def getSuspiciousActivitiesBySeverity(
    severity: str,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve suspicious activities by severity (low, medium, high, critical)"""
    security_service = SecurityService(session)
    activities = await security_service.getSuspiciousActivitiesBySeverity(severity, limit)

    return {
        "severity": severity,
        "count": len(activities),
        "activities": [
            {
                "id": str(a.id),
                "timestamp": a.timestamp,
                "remote_ip": a.remote_ip,
                "activity_type": a.activity_type,
                "details": a.details
            }
            for a in activities
        ]
    }


@router.get('/suspicious-activities/threat-assessment')
async def assessThreatLevel(
    start: datetime | None = Query(None, description="Start time (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(getDb)
):
    """Analyze suspicious activities and assess overall threat level"""
    # Strip timezone info to match database TIMESTAMP WITHOUT TIME ZONE
    if start:
        start = start.replace(tzinfo=None)

    security_service = SecurityService(session)
    activities = await security_service.getRecentSuspiciousActivities(limit)
    assessment = security_service.assessThreatLevel(activities)

    return {
        "assessment": assessment,
        "analyzed_activities": len(activities)
    }


@router.get('/rate-limit-violations/recent')
async def getRecentRateLimitViolations(
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve recent rate limit violations"""
    security_service = SecurityService(session)
    violations = await security_service.getRecentRateLimitViolations(limit)

    return {
        "count": len(violations),
        "violations": [
            {
                "id": str(v.id),
                "timestamp": v.timestamp,
                "service": v.service,
                "remote_ip": v.remote_ip,
                "violation_count": v.violation_count,
                "user_id": v.user_id
            }
            for v in violations
        ]
    }


@router.get('/rate-limit-violations/by-ip/{remote_ip}')
async def getRateLimitViolationsByIp(
    remote_ip: str,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve rate limit violations for a specific IP"""
    security_service = SecurityService(session)
    violations = await security_service.getRateLimitViolationsByIp(remote_ip, limit)

    return {
        "remote_ip": remote_ip,
        "count": len(violations),
        "violations": [
            {
                "id": str(v.id),
                "timestamp": v.timestamp,
                "service": v.service,
                "violation_count": v.violation_count,
                "user_id": v.user_id
            }
            for v in violations
        ]
    }


@router.get('/rate-limit-violations/by-service/{service}')
async def getRateLimitViolationsByService(
    service: str,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(getDb)
):
    """Retrieve rate limit violations for a specific service"""
    security_service = SecurityService(session)
    violations = await security_service.getRateLimitViolationsByService(service, limit)

    return {
        "service": service,
        "count": len(violations),
        "violations": [
            {
                "id": str(v.id),
                "timestamp": v.timestamp,
                "remote_ip": v.remote_ip,
                "violation_count": v.violation_count,
                "user_id": v.user_id
            }
            for v in violations
        ]
    }
