from __future__ import annotations
import time
from datetime import datetime
from shared.backend.database.engine import checkConnection as checkDbConnection
from shared.backend.redis.client import checkConnection as checkRedisConnection
from shared.backend.cryptoFactory import crypto
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class HealthCheckPoller:
    """
    Polls system component health (Database, Redis, Crypto).
    Measures latency and status for monitoring.
    """

    async def checkDatabaseHealth(self) -> tuple[str, float]:
        """
        Check database connection health and measure latency.
        Returns (status, latency_ms)
        """
        start = time.perf_counter()

        try:
            is_healthy = await checkDbConnection()
            latency_ms = (time.perf_counter() - start) * 1000

            status = "healthy" if is_healthy else "unhealthy"

            return (status, round(latency_ms, 2))

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "db_health_check_failed",
                f"Database health check failed: {e}",
                error_type=type(e).__name__
            )
            return ("unhealthy", round(latency_ms, 2))

    async def checkRedisHealth(self) -> tuple[str, float]:
        """
        Check Redis connection health and measure latency.
        Returns (status, latency_ms)
        """
        start = time.perf_counter()

        try:
            is_healthy = await checkRedisConnection()
            latency_ms = (time.perf_counter() - start) * 1000

            status = "healthy" if is_healthy else "unhealthy"

            return (status, round(latency_ms, 2))

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "redis_health_check_failed",
                f"Redis health check failed: {e}",
                error_type=type(e).__name__
            )
            return ("unhealthy", round(latency_ms, 2))

    def checkCryptoHealth(self) -> str:
        """
        Check crypto module availability.
        Returns status string.
        """
        try:
            # Test encryption/decryption
            test_data = "health_check_test"
            encrypted = crypto.encryptSensitive(test_data, context="health_check")
            decrypted = crypto.decryptSensitive(encrypted, context="health_check")

            if decrypted == test_data:
                return "healthy"
            else:
                logger.error(
                    "crypto_health_check_failed",
                    "Crypto module returned incorrect decryption"
                )
                return "unhealthy"

        except Exception as e:
            logger.error(
                "crypto_health_check_error",
                f"Crypto health check failed: {e}",
                error_type=type(e).__name__
            )
            return "unhealthy"

    async def pollHealth(self) -> dict:
        """
        Poll all system components and return health snapshot data.
        Returns dict ready for database insertion.
        """
        try:
            # Check all components
            db_status, db_latency = await self.checkDatabaseHealth()
            redis_status, redis_latency = await self.checkRedisHealth()
            crypto_status = self.checkCryptoHealth()

            health_data = {
                'timestamp': datetime.utcnow().replace(tzinfo=None),
                'db_status': db_status,
                'db_latency_ms': db_latency,
                'redis_status': redis_status,
                'redis_latency_ms': redis_latency,
                'crypto_status': crypto_status
            }

            logger.application(
                "health_poll_completed",
                f"Health check completed: DB={db_status}, Redis={redis_status}, Crypto={crypto_status}",
                db_latency=db_latency,
                redis_latency=redis_latency
            )

            return health_data

        except Exception as e:
            logger.error(
                "health_poll_error",
                f"Failed to poll health: {e}",
                error_type=type(e).__name__
            )

            # Return degraded health data
            return {
                'timestamp': datetime.utcnow().replace(tzinfo=None),
                'db_status': 'unknown',
                'db_latency_ms': 0.0,
                'redis_status': 'unknown',
                'redis_latency_ms': 0.0,
                'crypto_status': 'unknown'
            }
