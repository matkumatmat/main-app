from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from KSysAdmin.backend.domain.models.suspiciousActivity import SuspiciousActivity
from KSysAdmin.backend.infrastructure.database.repositories.suspiciousActivityRepository import SuspiciousActivityRepository
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class SecurityAnalysisService:
    """
    Domain service for analyzing metrics and detecting suspicious activities.
    Identifies patterns indicating potential security threats.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SuspiciousActivityRepository(session)

    async def detectHighErrorRate(self, time_window_minutes: int = 60) -> list[SuspiciousActivity]:
        """
        Detect IPs with high error rates (>50% errors in time window).
        Creates suspicious activity records.
        """
        cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=time_window_minutes)

        try:
            # Query metrics grouped by IP
            result = await self.session.execute(
                select(
                    MetricSnapshot.remote_ip,
                    func.count(MetricSnapshot.id).label('total'),
                    func.sum(func.cast((MetricSnapshot.status >= 400), func.Integer())).label('errors')
                )
                .where(MetricSnapshot.timestamp >= cutoff_time)
                .group_by(MetricSnapshot.remote_ip)
                .having(func.count(MetricSnapshot.id) >= 10)  # Minimum 10 requests
            )

            suspicious = []

            for row in result:
                ip, total, errors = row.remote_ip, row.total, row.errors or 0
                error_rate = (errors / total) * 100

                # Flag if error rate > 50%
                if error_rate > 50:
                    activity = SuspiciousActivity(
                        timestamp=datetime.utcnow().replace(tzinfo=None),
                        remote_ip=ip,
                        activity_type='high_error_rate',
                        severity='medium',
                        details={
                            'error_rate': round(error_rate, 2),
                            'total_requests': total,
                            'error_count': errors,
                            'time_window_minutes': time_window_minutes
                        }
                    )
                    suspicious.append(activity)

            if suspicious:
                logger.security(
                    "high_error_rate_detected",
                    f"Detected {len(suspicious)} IPs with high error rates",
                    count=len(suspicious)
                )

            return suspicious

        except Exception as e:
            logger.error(
                "error_rate_detection_failed",
                f"Failed to detect high error rates: {e}",
                error_type=type(e).__name__
            )
            return []

    async def detectRapidRequests(self, time_window_seconds: int = 10, threshold: int = 50) -> list[SuspiciousActivity]:
        """
        Detect IPs making rapid requests (>threshold requests in time window).
        Potential DoS or scraping attempts.
        """
        cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(seconds=time_window_seconds)

        try:
            # Query metrics grouped by IP in short time window
            result = await self.session.execute(
                select(
                    MetricSnapshot.remote_ip,
                    func.count(MetricSnapshot.id).label('request_count')
                )
                .where(MetricSnapshot.timestamp >= cutoff_time)
                .group_by(MetricSnapshot.remote_ip)
                .having(func.count(MetricSnapshot.id) > threshold)
            )

            suspicious = []

            for row in result:
                ip, count = row.remote_ip, row.request_count

                activity = SuspiciousActivity(
                    timestamp=datetime.utcnow().replace(tzinfo=None),
                    remote_ip=ip,
                    activity_type='rapid_requests',
                    severity='high',
                    details={
                        'request_count': count,
                        'time_window_seconds': time_window_seconds,
                        'threshold': threshold,
                        'requests_per_second': round(count / time_window_seconds, 2)
                    }
                )
                suspicious.append(activity)

            if suspicious:
                logger.security(
                    "rapid_requests_detected",
                    f"Detected {len(suspicious)} IPs with rapid request patterns",
                    count=len(suspicious)
                )

            return suspicious

        except Exception as e:
            logger.error(
                "rapid_request_detection_failed",
                f"Failed to detect rapid requests: {e}",
                error_type=type(e).__name__
            )
            return []

    async def detectFailedAuthAttempts(self, time_window_minutes: int = 15, threshold: int = 5) -> list[SuspiciousActivity]:
        """
        Detect IPs with multiple failed authentication attempts.
        Potential brute force attacks.
        """
        cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=time_window_minutes)

        try:
            # Query auth endpoints with 401 status
            result = await self.session.execute(
                select(
                    MetricSnapshot.remote_ip,
                    func.count(MetricSnapshot.id).label('failed_attempts')
                )
                .where(MetricSnapshot.timestamp >= cutoff_time)
                .where(MetricSnapshot.url.like('%/auth/%'))
                .where(MetricSnapshot.status == 401)
                .group_by(MetricSnapshot.remote_ip)
                .having(func.count(MetricSnapshot.id) >= threshold)
            )

            suspicious = []

            for row in result:
                ip, attempts = row.remote_ip, row.failed_attempts

                # Escalate severity based on attempts
                severity = 'low'
                if attempts >= 20:
                    severity = 'critical'
                elif attempts >= 10:
                    severity = 'high'
                elif attempts >= 5:
                    severity = 'medium'

                activity = SuspiciousActivity(
                    timestamp=datetime.utcnow().replace(tzinfo=None),
                    remote_ip=ip,
                    activity_type='failed_auth_attempts',
                    severity=severity,
                    details={
                        'failed_attempts': attempts,
                        'time_window_minutes': time_window_minutes,
                        'threshold': threshold
                    }
                )
                suspicious.append(activity)

            if suspicious:
                logger.security(
                    "failed_auth_detected",
                    f"Detected {len(suspicious)} IPs with failed auth attempts",
                    count=len(suspicious)
                )

            return suspicious

        except Exception as e:
            logger.error(
                "failed_auth_detection_failed",
                f"Failed to detect auth attempts: {e}",
                error_type=type(e).__name__
            )
            return []

    async def runAnalysis(self) -> int:
        """
        Run all security analysis checks and persist results.
        Returns total count of suspicious activities detected.
        """
        try:
            # Run all detection methods
            high_error = await self.detectHighErrorRate()
            rapid = await self.detectRapidRequests()
            failed_auth = await self.detectFailedAuthAttempts()

            # Combine all suspicious activities
            all_suspicious = high_error + rapid + failed_auth

            if not all_suspicious:
                logger.application(
                    "security_analysis_clean",
                    "No suspicious activities detected",
                    level="debug"
                )
                return 0

            # Persist to database
            self.session.add_all(all_suspicious)
            await self.session.flush()

            logger.security(
                "security_analysis_completed",
                f"Detected and recorded {len(all_suspicious)} suspicious activities",
                total=len(all_suspicious),
                high_error=len(high_error),
                rapid_requests=len(rapid),
                failed_auth=len(failed_auth)
            )

            return len(all_suspicious)

        except Exception as e:
            logger.error(
                "security_analysis_failed",
                f"Security analysis failed: {e}",
                error_type=type(e).__name__
            )
            return 0
