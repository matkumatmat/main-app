from __future__ import annotations
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getEngine
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory
from KSysAdmin.backend.infrastructure.collectors.nginxLogParser import NginxLogParser
from KSysAdmin.backend.infrastructure.collectors.redisViolationReader import RedisViolationReader
from KSysAdmin.backend.infrastructure.collectors.healthCheckPoller import HealthCheckPoller
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from KSysAdmin.backend.domain.models.rateLimitViolation import RateLimitViolation
from KSysAdmin.backend.domain.models.systemHealthSnapshot import SystemHealthSnapshot
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class MetricCollectionTask:
    """
    Background task orchestrating metric collection from multiple sources.
    Runs periodically to collect and persist monitoring data.
    """

    def __init__(self):
        self.nginx_parser = NginxLogParser()
        self.redis_reader = RedisViolationReader()
        self.health_poller = HealthCheckPoller()
        self.collection_interval = settings.monitoring_collection_interval
        self.is_running = False
        self.task: asyncio.Task | None = None

    async def collectNginxMetrics(self, session: AsyncSession) -> int:
        """
        Parse nginx logs and persist metrics to database.
        Returns count of metrics collected.
        """
        try:
            # Parse new log entries
            log_entries = self.nginx_parser.parseNewLogs()

            if not log_entries:
                return 0

            # Convert to MetricSnapshot models
            metrics = []
            for entry in log_entries:
                metric = MetricSnapshot(**entry)
                metrics.append(metric)

            # Bulk insert
            session.add_all(metrics)
            await session.flush()

            logger.application(
                "nginx_metrics_collected",
                f"Collected {len(metrics)} nginx metrics",
                count=len(metrics)
            )

            return len(metrics)

        except Exception as e:
            logger.error(
                "nginx_metric_collection_failed",
                f"Failed to collect nginx metrics: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def collectRateLimitViolations(self, session: AsyncSession) -> int:
        """
        Read rate limit violations from Redis and persist to database.
        Returns count of violations collected.
        """
        try:
            # Collect violations
            violations_data = await self.redis_reader.collectViolations(threshold=5)

            if not violations_data:
                return 0

            # Convert to RateLimitViolation models
            violations = []
            for data in violations_data:
                violation = RateLimitViolation(**data)
                violations.append(violation)

            # Bulk insert
            session.add_all(violations)
            await session.flush()

            logger.application(
                "rate_limit_violations_collected",
                f"Collected {len(violations)} rate limit violations",
                count=len(violations)
            )

            return len(violations)

        except Exception as e:
            logger.error(
                "violation_collection_failed",
                f"Failed to collect rate limit violations: {e}",
                error_type=type(e).__name__
            )
            return 0

    async def collectHealthSnapshot(self, session: AsyncSession) -> bool:
        """
        Poll system health and persist snapshot to database.
        Returns True if successful.
        """
        try:
            # Poll health
            health_data = await self.health_poller.pollHealth()

            # Create health snapshot
            snapshot = SystemHealthSnapshot(**health_data)

            # Insert
            session.add(snapshot)
            await session.flush()

            logger.application(
                "health_snapshot_collected",
                f"Health snapshot collected: DB={health_data['db_status']}, Redis={health_data['redis_status']}"
            )

            return True

        except Exception as e:
            logger.error(
                "health_snapshot_collection_failed",
                f"Failed to collect health snapshot: {e}",
                error_type=type(e).__name__
            )
            return False

    async def runCollection(self) -> None:
        """
        Run single collection cycle for all metric sources.
        Persists all data in a single database transaction.
        """
        engine = getEngine()
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with session_factory() as session:
            try:
                # Collect from all sources
                nginx_count = await self.collectNginxMetrics(session)
                violation_count = await self.collectRateLimitViolations(session)
                health_collected = await self.collectHealthSnapshot(session)

                # Commit transaction
                await session.commit()

                logger.application(
                    "metric_collection_completed",
                    f"Collection completed: {nginx_count} metrics, {violation_count} violations, health={health_collected}",
                    nginx_metrics=nginx_count,
                    violations=violation_count,
                    health=health_collected
                )

            except Exception as e:
                await session.rollback()
                logger.error(
                    "metric_collection_transaction_failed",
                    f"Collection transaction failed: {e}",
                    error_type=type(e).__name__
                )

    async def _collectionLoop(self) -> None:
        """
        Background loop running collection cycles at configured interval.
        """
        logger.application(
            "metric_collection_started",
            f"Starting metric collection loop (interval: {self.collection_interval}s)",
            interval=self.collection_interval
        )

        while self.is_running:
            try:
                # Run collection
                await self.runCollection()

                # Wait for next interval
                await asyncio.sleep(self.collection_interval)

            except asyncio.CancelledError:
                logger.application(
                    "metric_collection_cancelled",
                    "Collection loop cancelled"
                )
                break

            except Exception as e:
                logger.error(
                    "metric_collection_loop_error",
                    f"Error in collection loop: {e}",
                    error_type=type(e).__name__
                )
                # Wait before retry
                await asyncio.sleep(60)

    def start(self) -> None:
        """Start background collection task"""
        if self.is_running:
            logger.application(
                "metric_collection_already_running",
                "Collection task already running",
                level="warning"
            )
            return

        self.is_running = True
        self.task = asyncio.create_task(self._collectionLoop())

        logger.application(
            "metric_collection_task_started",
            "Background metric collection task started"
        )

    async def stop(self) -> None:
        """Stop background collection task"""
        if not self.is_running:
            return

        self.is_running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.application(
            "metric_collection_task_stopped",
            "Background metric collection task stopped"
        )
