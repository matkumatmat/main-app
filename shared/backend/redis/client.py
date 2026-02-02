from __future__ import annotations
from redis.asyncio import Redis, ConnectionPool
import structlog

from shared.backend.config.settings import settings

logger = structlog.get_logger()

# Global Redis client and pool
_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None


def createRedisPool() -> ConnectionPool:
    """Create async Redis connection pool"""
    logger.info(
        "redis_pool_creating",
        url=settings.redis_url,
        max_connections=settings.redis_max_connections
    )

    pool = ConnectionPool.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,  # Auto-decode to strings
        encoding="utf-8",
        socket_connect_timeout=5,
        socket_keepalive=True,
    )

    logger.info("redis_pool_created")
    return pool


async def initRedis() -> None:
    """Initialize Redis client and test connection"""
    global _redis_pool, _redis_client

    if _redis_client is not None:
        logger.warning("redis_already_initialized")
        return

    try:
        _redis_pool = createRedisPool()
        _redis_client = Redis(connection_pool=_redis_pool)

        # Test connection
        await _redis_client.ping()

        logger.info(
            "redis_initialized",
            environment=settings.environment
        )
    except Exception as e:
        logger.error(
            "redis_init_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


async def closeRedis() -> None:
    """Close Redis connection"""
    global _redis_pool, _redis_client

    if _redis_client is None:
        logger.warning("redis_not_initialized")
        return

    try:
        await _redis_client.close()
        await _redis_pool.disconnect()
        _redis_client = None
        _redis_pool = None
        logger.info("redis_closed")
    except Exception as e:
        logger.error(
            "redis_close_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


async def getRedis() -> Redis:
    """Get Redis client instance for FastAPI dependency"""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call initRedis() first.")
    return _redis_client


async def checkConnection() -> bool:
    """Check Redis connection health"""
    try:
        client = await getRedis()
        await client.ping()
        return True
    except Exception as e:
        logger.error(
            "redis_health_check_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        return False
