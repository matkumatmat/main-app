from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from KSysAdmin.backend.domain.models.hourlyMetricAggregation import HourlyMetricAggregation
from KSysAdmin.backend.infrastructure.database.repositories.hourlyMetricAggregationRepository import HourlyMetricAggregationRepository
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class AggregationService:
    """
    Domain service for aggregating raw metrics into hourly summaries.
    Calculates statistics per service per hour.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = HourlyMetricAggregationRepository(session)

    def _getHourBoundaries(self, hour_start: datetime) -> tuple[datetime, datetime]:
        """
        Get start and end boundaries for an hour.
        Returns (hour_start, hour_end)
        """
        # Ensure naive UTC datetime
        if hour_start.tzinfo is not None:
            hour_start = hour_start.replace(tzinfo=None)

        # Truncate to hour
        hour_start = hour_start.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        return (hour_start, hour_end)

    def _calculatePercentile(self, values: list[float], percentile: int) -> float:
        """Calculate percentile from list of values"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        index = min(index, len(sorted_values) - 1)

        return sorted_values[index]

    async def aggregateHour(self, service: str, hour_start: datetime) -> HourlyMetricAggregation | None:
        """
        Aggregate metrics for a specific service and hour.
        Returns aggregated data or None if no metrics found.
        """
        hour_start, hour_end = self._getHourBoundaries(hour_start)

        try:
            # Query metrics for this hour and service
            result = await self.session.execute(
                select(MetricSnapshot)
                .where(MetricSnapshot.service == service)
                .where(MetricSnapshot.timestamp >= hour_start)
                .where(MetricSnapshot.timestamp < hour_end)
            )
            metrics = list(result.scalars().all())

            if not metrics:
                logger.application(
                    "aggregation_no_data",
                    f"No metrics found for {service} at {hour_start}",
                    service=service,
                    hour=hour_start.isoformat(),
                    level="debug"
                )
                return None

            # Calculate aggregations
            total_requests = len(metrics)
            successful_requests = sum(1 for m in metrics if 200 <= m.status < 400)
            client_errors = sum(1 for m in metrics if 400 <= m.status < 500)
            server_errors = sum(1 for m in metrics if m.status >= 500)
            rate_limited_requests = sum(1 for m in metrics if m.rate_limited)

            # Calculate latency statistics
            nginx_latencies = [m.nginx_latency_ms for m in metrics]
            backend_latencies = [m.backend_latency_ms for m in metrics if m.backend_latency_ms is not None]

            avg_nginx_latency = sum(nginx_latencies) / len(nginx_latencies) if nginx_latencies else 0.0
            avg_backend_latency = sum(backend_latencies) / len(backend_latencies) if backend_latencies else 0.0

            p95_nginx_latency = self._calculatePercentile(nginx_latencies, 95)
            p95_backend_latency = self._calculatePercentile(backend_latencies, 95) if backend_latencies else 0.0

            # Count unique IPs
            unique_ips = len(set(m.remote_ip for m in metrics))

            # Create aggregation record
            aggregation = HourlyMetricAggregation(
                hour_start=hour_start,
                service=service,
                total_requests=total_requests,
                successful_requests=successful_requests,
                client_errors=client_errors,
                server_errors=server_errors,
                rate_limited_requests=rate_limited_requests,
                avg_nginx_latency_ms=round(avg_nginx_latency, 2),
                avg_backend_latency_ms=round(avg_backend_latency, 2),
                p95_nginx_latency_ms=round(p95_nginx_latency, 2),
                p95_backend_latency_ms=round(p95_backend_latency, 2),
                unique_ips=unique_ips
            )

            logger.application(
                "aggregation_calculated",
                f"Aggregated {total_requests} metrics for {service} at {hour_start}",
                service=service,
                hour=hour_start.isoformat(),
                total_requests=total_requests,
                unique_ips=unique_ips
            )

            return aggregation

        except Exception as e:
            logger.error(
                "aggregation_failed",
                f"Failed to aggregate metrics: {e}",
                service=service,
                hour=hour_start.isoformat(),
                error_type=type(e).__name__
            )
            return None

    async def aggregateAndPersist(self, service: str, hour_start: datetime) -> bool:
        """
        Aggregate metrics and persist to database.
        Checks if aggregation already exists (idempotent).
        Returns True if successful.
        """
        hour_start, _ = self._getHourBoundaries(hour_start)

        try:
            # Check if aggregation already exists
            result = await self.session.execute(
                select(HourlyMetricAggregation)
                .where(HourlyMetricAggregation.service == service)
                .where(HourlyMetricAggregation.hour_start == hour_start)
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.application(
                    "aggregation_already_exists",
                    f"Aggregation already exists for {service} at {hour_start}",
                    service=service,
                    hour=hour_start.isoformat(),
                    level="debug"
                )
                return True

            # Calculate aggregation
            aggregation = await self.aggregateHour(service, hour_start)

            if not aggregation:
                return False

            # Persist
            self.session.add(aggregation)
            await self.session.flush()

            logger.application(
                "aggregation_persisted",
                f"Persisted aggregation for {service} at {hour_start}",
                service=service,
                hour=hour_start.isoformat(),
                total_requests=aggregation.total_requests
            )

            return True

        except Exception as e:
            logger.error(
                "aggregation_persist_failed",
                f"Failed to persist aggregation: {e}",
                service=service,
                hour=hour_start.isoformat(),
                error_type=type(e).__name__
            )
            return False

    async def aggregateMultipleHours(
        self,
        services: list[str],
        start_hour: datetime,
        end_hour: datetime
    ) -> dict[str, int]:
        """
        Aggregate metrics for multiple services across multiple hours.
        Returns dict with success counts per service.
        """
        start_hour, _ = self._getHourBoundaries(start_hour)
        end_hour, _ = self._getHourBoundaries(end_hour)

        results = {service: 0 for service in services}

        current_hour = start_hour
        while current_hour < end_hour:
            for service in services:
                success = await self.aggregateAndPersist(service, current_hour)
                if success:
                    results[service] += 1

            current_hour += timedelta(hours=1)

        logger.application(
            "multiple_aggregations_completed",
            f"Completed aggregations from {start_hour} to {end_hour}",
            start=start_hour.isoformat(),
            end=end_hour.isoformat(),
            results=results
        )

        return results
