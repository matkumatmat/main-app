from __future__ import annotations
import time
from typing import Any
from datetime import datetime, UTC
from fastapi import APIRouter
from shared.backend.database.engine import checkConnection as checkDbConnection
from shared.backend.redis.client import checkConnection as checkRedisConnection
from shared.backend.cryptoFactory import crypto

router = APIRouter(tags=["Health"])


async def checkDatabase() -> dict[str, Any]:
    start_time = time.perf_counter()

    try:
        is_healthy = await checkDbConnection()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "status": "up" if is_healthy else "down",
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "down",
            "latency_ms": latency_ms,
            "error": str(e)
        }


async def checkRedis() -> dict[str, Any]:
    start_time = time.perf_counter()

    try:
        is_healthy = await checkRedisConnection()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "status": "up" if is_healthy else "down",
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "down",
            "latency_ms": latency_ms,
            "error": str(e)
        }


def checkCrypto() -> dict[str, Any]:
    try:
        test_data = "health_check_test"
        context = "health:check"

        encrypted = crypto.encryptSensitive(test_data, context)
        decrypted = crypto.decryptSensitive(encrypted, context)

        is_valid = decrypted == test_data

        return {
            "status": "up" if is_valid else "down"
        }
    except Exception as e:
        return {
            "status": "down",
            "error": str(e)
        }


async def performHealthCheck() -> dict[str, Any]:
    db_health = await checkDatabase()
    redis_health = await checkRedis()
    crypto_health = checkCrypto()

    all_healthy = (
        db_health["status"] == "up" and
        redis_health["status"] == "up" and
        crypto_health["status"] == "up"
    )

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": {
            "database": db_health,
            "redis": redis_health,
            "crypto": crypto_health
        },
        "timestamp": datetime.now(UTC).isoformat()
    }


@router.get("/health")
async def healthCheck():
    return await performHealthCheck()
