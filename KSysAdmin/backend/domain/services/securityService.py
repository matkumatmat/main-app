from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.infrastructure.database.repositories.suspiciousActivityRepository import SuspiciousActivityRepository
from KSysAdmin.backend.infrastructure.database.repositories.rateLimitViolationRepository import RateLimitViolationRepository
from KSysAdmin.backend.domain.models.suspiciousActivity import SuspiciousActivity
from KSysAdmin.backend.domain.models.rateLimitViolation import RateLimitViolation


class SecurityService:
    """
    Domain service for security monitoring.
    Handles suspicious activity and rate limit violation tracking.
    """

    def __init__(self, session: AsyncSession):
        self.suspiciousRepo = SuspiciousActivityRepository(session)
        self.rateLimitRepo = RateLimitViolationRepository(session)

    async def recordSuspiciousActivity(
        self,
        remote_ip: str,
        activity_type: str,
        severity: str,
        details: dict
    ) -> SuspiciousActivity:
        """Record a new suspicious activity"""
        activity = SuspiciousActivity(
            timestamp=datetime.utcnow(),
            remote_ip=remote_ip,
            activity_type=activity_type,
            severity=severity,
            details=details
        )
        return await self.suspiciousRepo.create(activity)

    async def recordRateLimitViolation(
        self,
        service: str,
        remote_ip: str,
        violation_count: int = 1,
        user_id: str | None = None
    ) -> RateLimitViolation:
        """Record a rate limit violation"""
        violation = RateLimitViolation(
            timestamp=datetime.utcnow(),
            service=service,
            remote_ip=remote_ip,
            violation_count=violation_count,
            user_id=user_id
        )
        return await self.rateLimitRepo.create(violation)

    async def getSuspiciousActivitiesByIp(
        self,
        remote_ip: str,
        limit: int = 100
    ) -> list[SuspiciousActivity]:
        """Retrieve suspicious activities for an IP"""
        return await self.suspiciousRepo.getByIp(remote_ip, limit)

    async def getSuspiciousActivitiesBySeverity(
        self,
        severity: str,
        limit: int = 100
    ) -> list[SuspiciousActivity]:
        """Retrieve activities by severity level (low, medium, high, critical)"""
        return await self.suspiciousRepo.getBySeverity(severity, limit)

    async def getRecentSuspiciousActivities(self, limit: int = 50) -> list[SuspiciousActivity]:
        """Retrieve recent suspicious activities"""
        return await self.suspiciousRepo.getRecent(limit)

    async def getRateLimitViolationsByIp(
        self,
        remote_ip: str,
        limit: int = 100
    ) -> list[RateLimitViolation]:
        """Retrieve rate limit violations for an IP"""
        return await self.rateLimitRepo.getByIp(remote_ip, limit)

    async def getRateLimitViolationsByService(
        self,
        service: str,
        limit: int = 100
    ) -> list[RateLimitViolation]:
        """Retrieve rate limit violations for a service"""
        return await self.rateLimitRepo.getByService(service, limit)

    async def getRecentRateLimitViolations(self, limit: int = 50) -> list[RateLimitViolation]:
        """Retrieve recent rate limit violations"""
        return await self.rateLimitRepo.getRecent(limit)

    def assessThreatLevel(self, activities: list[SuspiciousActivity]) -> dict:
        """
        Analyze suspicious activities and assess threat level.
        Business logic for security threat evaluation.
        """
        if not activities:
            return {"threat_level": "none", "critical_count": 0, "high_count": 0}

        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for activity in activities:
            severity = activity.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        threat_level = "low"
        if severity_counts["critical"] > 0:
            threat_level = "critical"
        elif severity_counts["high"] >= 5:
            threat_level = "high"
        elif severity_counts["medium"] >= 10:
            threat_level = "medium"

        return {
            "threat_level": threat_level,
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "low_count": severity_counts["low"],
            "total_activities": len(activities)
        }
