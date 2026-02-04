from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from shared.backend.database.engine import getEngine
from shared.backend.loggingFactory import LoggerFactory
from KSysAdmin.backend.domain.services.aggregation.aggregationService import AggregationService
from KSysAdmin.backend.domain.services.aggregation.securityAnalysisService import SecurityAnalysisService
from KSysAdmin.backend.domain.services.aggregation.retentionService import RetentionService

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class AggregationTask:
    """
    Background task orchestrating hourly aggregation, security analysis, and cleanup.
    Runs on scheduled intervals to process collected metrics.
    """

    def __init__(self):
        self.aggregation_interval = 3600  # 1 hour
        self.security_analysis_interval = 1800  # 30 minutes
        self.cleanup_interval = 86400  # 24 hours
        self.is_running = False
        self.aggregation_task: asyncio.Task | None = None
        self.security_task: asyncio.Task | None = None
        self.cleanup_task: asyncio.Task | None = None

        # Tracked services for aggregation
        self.services = ['kauth', 'ksysadmin', 'ksyspayment', 'nginx_gateway']

    async def runHourlyAggregation(self) -> None:
        """
        Aggregate metrics for the previous completed hour.
        Runs for all tracked services.
        """
        engine = getEngine()
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with session_factory() as session:
            try:
                # Get previous hour boundary
                now = datetime.utcnow().replace(tzinfo=None)
                previous_hour = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

                aggregation_service = AggregationService(session)

                # Aggregate for all services
                results = await aggregation_service.aggregateMultipleHours(
                    services=self.services,
                    start_hour=previous_hour,
                    end_hour=previous_hour + timedelta(hours=1)
                )

                await session.commit()

                total_success = sum(results.values())
                logger.application(
                    "hourly_aggregation_completed",
                    f"Aggregated {total_success} service-hours",
                    hour=previous_hour.isoformat(),
                    results=results
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    "hourly_aggregation_failed",
                    f"Hourly aggregation failed: {e}",
                    error_type=type(e).__name__
                )

    async def runSecurityAnalysis(self) -> None:
        """
        Run security analysis to detect suspicious activities.
        """
        engine = getEngine()
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with session_factory() as session:
            try:
                security_service = SecurityAnalysisService(session)
                detected_count = await security_service.runAnalysis()

                await session.commit()

                logger.application(
                    "security_analysis_completed",
                    f"Security analysis detected {detected_count} suspicious activities",
                    detected=detected_count
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    "security_analysis_failed",
                    f"Security analysis failed: {e}",
                    error_type=type(e).__name__
                )

    async def runCleanup(self) -> None:
        """
        Run retention cleanup for old monitoring data.
        """
        engine = getEngine()
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with session_factory() as session:
            try:
                retention_service = RetentionService(session)
                results = await retention_service.runFullCleanup()

                await session.commit()

                total_deleted = sum(results.values())
                logger.application(
                    "cleanup_completed",
                    f"Cleanup deleted {total_deleted} old records",
                    total_deleted=total_deleted,
                    details=results
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    "cleanup_failed",
                    f"Cleanup failed: {e}",
                    error_type=type(e).__name__
                )

    async def _aggregationLoop(self) -> None:
        """
        Background loop running hourly aggregation.
        """
        logger.application(
            "aggregation_loop_started",
            f"Starting aggregation loop (interval: {self.aggregation_interval}s)",
            interval=self.aggregation_interval
        )

        # Wait for first full hour boundary
        now = datetime.utcnow().replace(tzinfo=None)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_seconds = (next_hour - now).total_seconds()

        logger.application(
            "aggregation_waiting_for_hour",
            f"Waiting {wait_seconds:.0f}s until next hour boundary",
            next_run=next_hour.isoformat()
        )

        await asyncio.sleep(wait_seconds)

        while self.is_running:
            try:
                await self.runHourlyAggregation()

                # Wait for next hour
                await asyncio.sleep(self.aggregation_interval)

            except asyncio.CancelledError:
                logger.application(
                    "aggregation_loop_cancelled",
                    "Aggregation loop cancelled"
                )
                break

            except Exception as e:
                logger.error(
                    "aggregation_loop_error",
                    f"Error in aggregation loop: {e}",
                    error_type=type(e).__name__
                )
                await asyncio.sleep(300)  # 5 min retry delay

    async def _securityAnalysisLoop(self) -> None:
        """
        Background loop running security analysis.
        """
        logger.application(
            "security_analysis_loop_started",
            f"Starting security analysis loop (interval: {self.security_analysis_interval}s)",
            interval=self.security_analysis_interval
        )

        while self.is_running:
            try:
                await self.runSecurityAnalysis()

                await asyncio.sleep(self.security_analysis_interval)

            except asyncio.CancelledError:
                logger.application(
                    "security_analysis_loop_cancelled",
                    "Security analysis loop cancelled"
                )
                break

            except Exception as e:
                logger.error(
                    "security_analysis_loop_error",
                    f"Error in security analysis loop: {e}",
                    error_type=type(e).__name__
                )
                await asyncio.sleep(300)

    async def _cleanupLoop(self) -> None:
        """
        Background loop running daily cleanup.
        """
        logger.application(
            "cleanup_loop_started",
            f"Starting cleanup loop (interval: {self.cleanup_interval}s)",
            interval=self.cleanup_interval
        )

        while self.is_running:
            try:
                await self.runCleanup()

                await asyncio.sleep(self.cleanup_interval)

            except asyncio.CancelledError:
                logger.application(
                    "cleanup_loop_cancelled",
                    "Cleanup loop cancelled"
                )
                break

            except Exception as e:
                logger.error(
                    "cleanup_loop_error",
                    f"Error in cleanup loop: {e}",
                    error_type=type(e).__name__
                )
                await asyncio.sleep(3600)  # 1 hour retry delay

    def start(self) -> None:
        """Start all background aggregation tasks"""
        if self.is_running:
            logger.application(
                "aggregation_tasks_already_running",
                "Aggregation tasks already running",
                level="warning"
            )
            return

        self.is_running = True

        # Start all loops
        self.aggregation_task = asyncio.create_task(self._aggregationLoop())
        self.security_task = asyncio.create_task(self._securityAnalysisLoop())
        self.cleanup_task = asyncio.create_task(self._cleanupLoop())

        logger.application(
            "aggregation_tasks_started",
            "All aggregation background tasks started"
        )

    async def stop(self) -> None:
        """Stop all background aggregation tasks"""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel all tasks
        tasks = [self.aggregation_task, self.security_task, self.cleanup_task]

        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.application(
            "aggregation_tasks_stopped",
            "All aggregation background tasks stopped"
        )
