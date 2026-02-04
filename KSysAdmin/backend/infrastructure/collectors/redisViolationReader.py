from __future__ import annotations
from datetime import datetime
from redis.asyncio import Redis
from shared.backend.redis.client import getRedis
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class RedisViolationReader:
    """
    Reads rate limit violation data from Redis.
    Queries rate limit keys and extracts violation statistics.
    """

    def __init__(self, redis: Redis | None = None):
        self.redis = redis

    async def _ensureRedis(self) -> Redis:
        """Ensure Redis connection is available"""
        if self.redis is None:
            self.redis = await getRedis()
        return self.redis

    async def scanRateLimitKeys(self, pattern: str = "rate_limit:*") -> list[str]:
        """Scan Redis for rate limit keys"""
        redis = await self._ensureRedis()
        keys = []

        try:
            async for key in redis.scan_iter(match=pattern, count=100):
                if isinstance(key, bytes):
                    keys.append(key.decode('utf-8'))
                else:
                    keys.append(key)
        except Exception as e:
            logger.error(
                "redis_scan_error",
                f"Failed to scan Redis keys: {e}",
                error_type=type(e).__name__
            )

        return keys

    async def getRateLimitValue(self, key: str) -> int:
        """Get current rate limit counter value"""
        redis = await self._ensureRedis()

        try:
            value = await redis.get(key)
            if value is None:
                return 0
            return int(value)
        except Exception as e:
            logger.error(
                "redis_get_error",
                f"Failed to get Redis key {key}: {e}",
                key=key,
                error_type=type(e).__name__
            )
            return 0

    def parseRateLimitKey(self, key: str) -> dict | None:
        """
        Parse rate limit key format: rate_limit:{service}:{ip}:{endpoint}
        Returns dict with parsed components or None if invalid.
        """
        try:
            parts = key.split(':')
            if len(parts) < 3 or parts[0] != 'rate_limit':
                return None

            # Extract components
            service = parts[1] if len(parts) > 1 else 'unknown'
            ip = parts[2] if len(parts) > 2 else 'unknown'
            endpoint = ':'.join(parts[3:]) if len(parts) > 3 else ''

            return {
                'service': service,
                'remote_ip': ip,
                'endpoint': endpoint
            }
        except Exception as e:
            logger.error(
                "rate_limit_key_parse_error",
                f"Failed to parse key {key}: {e}",
                key=key
            )
            return None

    async def collectViolations(self, threshold: int = 10) -> list[dict]:
        """
        Collect rate limit violations (counters above threshold).
        Returns list of violation data ready for database insertion.
        """
        violations = []

        try:
            # Scan all rate limit keys
            keys = await self.scanRateLimitKeys()

            for key in keys:
                # Get counter value
                count = await self.getRateLimitValue(key)

                # Check if violation (above threshold)
                if count < threshold:
                    continue

                # Parse key components
                parsed = self.parseRateLimitKey(key)
                if not parsed:
                    continue

                violations.append({
                    'timestamp': datetime.utcnow().replace(tzinfo=None),
                    'service': parsed['service'],
                    'remote_ip': parsed['remote_ip'],
                    'violation_count': count,
                    'user_id': None  # Could be extracted if stored in Redis
                })

            if violations:
                logger.application(
                    "rate_limit_violations_collected",
                    f"Collected {len(violations)} rate limit violations",
                    count=len(violations)
                )

        except Exception as e:
            logger.error(
                "violation_collection_error",
                f"Failed to collect violations: {e}",
                error_type=type(e).__name__
            )

        return violations

    async def clearExpiredKeys(self) -> int:
        """
        Clear expired rate limit keys (optional cleanup).
        Returns number of keys cleared.
        """
        redis = await self._ensureRedis()
        cleared = 0

        try:
            keys = await self.scanRateLimitKeys()

            for key in keys:
                # Check TTL
                ttl = await redis.ttl(key)

                # If TTL is -1 (no expiration) or 0 (already expired), handle it
                if ttl == 0:
                    await redis.delete(key)
                    cleared += 1

            if cleared > 0:
                logger.application(
                    "rate_limit_keys_cleared",
                    f"Cleared {cleared} expired rate limit keys",
                    count=cleared
                )

        except Exception as e:
            logger.error(
                "key_cleanup_error",
                f"Failed to clear expired keys: {e}",
                error_type=type(e).__name__
            )

        return cleared
