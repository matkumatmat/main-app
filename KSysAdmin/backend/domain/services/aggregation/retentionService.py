from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from KSysAdmin.backend.domain.models.systemHealthSnapshot import SystemHealthSnapshot
from KSysAdmin.backend.domain.models.suspiciousActivity import SuspiciousActivity
from KSysAdmin.backend.domain.models.rateLimitViolation import RateLimitViolation
from KSysAdmin.backend.domain.models.hourlyMetricAggregation import HourlyMetricAggregation
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class RetentionService:
    """
    Domain service for managing data retention and cleanup.
    Removes old monitoring data based on retention policies.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.retention_days = settings.monitoring_retention_days

    async def cleanupMetricSnapshots(self, retention_days: int | None = None) -> int:
        """
        Delete metric snapshots older than retention period.
        Returns count of deleted records.
        """
        days = retention_days or self.retention_days
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)

        try:
            result = await self.session.execute(
                delete(MetricSnapshot)
                .where(MetricSnapshot.timestamp < cutoff_date)
            )

            deleted_count = result.rowcount

            if deleted_count > 0:
                logger.application(
                    "metric_snapshots_cleaned",
                    f"Deleted {deleted_count} metric snapshots older than {days} days",
                    deleted=deleted_count,
                    retention_days=days
                )

            return deleted_count

        except Exception as e:
            logger.error(
                "metric_cleanup_failed",
                f"Failed to cleanup metric snapshots: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def cleanupHealthSnapshots(self, retention_days: int | None = None) -> int:
        """
        Delete health snapshots older than retention period.
        Returns count of deleted records.
        """
        days = retention_days or self.retention_days
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)

        try:
            result = await self.session.execute(
                delete(SystemHealthSnapshot)
                .where(SystemHealthSnapshot.timestamp < cutoff_date)
            )

            deleted_count = result.rowcount

            if deleted_count > 0:
                logger.application(
                    "health_snapshots_cleaned",
                    f"Deleted {deleted_count} health snapshots older than {days} days",
                    deleted=deleted_count,
                    retention_days=days
                )

            return deleted_count

        except Exception as e:
            logger.error(
                "health_cleanup_failed",
                f"Failed to cleanup health snapshots: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def cleanupSuspiciousActivities(self, retention_days: int | None = None) -> int:
        """
        Delete suspicious activities older than retention period.
        Returns count of deleted records.
        """
        days = retention_days or self.retention_days
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)

        try:
            result = await self.session.execute(
                delete(SuspiciousActivity)
                .where(SuspiciousActivity.timestamp < cutoff_date)
            )

            deleted_count = result.rowcount

            if deleted_count > 0:
                logger.application(
                    "suspicious_activities_cleaned",
                    f"Deleted {deleted_count} suspicious activities older than {days} days",
                    deleted=deleted_count,
                    retention_days=days
                )

            return deleted_count

        except Exception as e:
            logger.error(
                "suspicious_cleanup_failed",
                f"Failed to cleanup suspicious activities: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def cleanupRateLimitViolations(self, retention_days: int | None = None) -> int:
        """
        Delete rate limit violations older than retention period.
        Returns count of deleted records.
        """
        days = retention_days or self.retention_days
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)

        try:
            result = await self.session.execute(
                delete(RateLimitViolation)
                .where(RateLimitViolation.timestamp < cutoff_date)
            )

            deleted_count = result.rowcount

            if deleted_count > 0:
                logger.application(
                    "rate_violations_cleaned",
                    f"Deleted {deleted_count} rate limit violations older than {days} days",
                    deleted=deleted_count,
                    retention_days=days
                )

            return deleted_count

        except Exception as e:
            logger.error(
                "violations_cleanup_failed",
                f"Failed to cleanup rate limit violations: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def cleanupHourlyAggregations(self, retention_days: int | None = None) -> int:
        """
        Delete hourly aggregations older than retention period.
        Aggregations typically retained longer than raw metrics.
        """
        days = retention_days or (self.retention_days * 4)  # 4x retention for aggregations
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)

        try:
            result = await self.session.execute(
                delete(HourlyMetricAggregation)
                .where(HourlyMetricAggregation.hour_start < cutoff_date)
            )

            deleted_count = result.rowcount

            if deleted_count > 0:
                logger.application(
                    "aggregations_cleaned",
                    f"Deleted {deleted_count} hourly aggregations older than {days} days",
                    deleted=deleted_count,
                    retention_days=days
                )

            return deleted_count

        except Exception as e:
            logger.error(
                "aggregation_cleanup_failed",
                f"Failed to cleanup hourly aggregations: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def runFullCleanup(self) -> dict[str, int]:
        """
        Run cleanup for all monitoring data tables.
        Returns dict with deletion counts per table.
        """
        try:
            results = {
                'metric_snapshots': await self.cleanupMetricSnapshots(),
                'health_snapshots': await self.cleanupHealthSnapshots(),
                'suspicious_activities': await self.cleanupSuspiciousActivities(),
                'rate_violations': await self.cleanupRateLimitViolations(),
                'hourly_aggregations': await self.cleanupHourlyAggregations()
            }

            total_deleted = sum(results.values())

            logger.application(
                "full_cleanup_completed",
                f"Cleanup completed: {total_deleted} total records deleted",
                total_deleted=total_deleted,
                details=results
            )

            return results

        except Exception as e:
            logger.error(
                "full_cleanup_failed",
                f"Full cleanup failed: {e}",
                error_type=type(e).__name__
            )
            return {}
