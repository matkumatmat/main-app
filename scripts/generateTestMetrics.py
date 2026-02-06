#!/usr/bin/env python3
"""
Generate realistic test metrics data spread over time for dashboard testing.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shared.backend.config.settings import settings
from KSysAdmin.backend.domain.models.metricSnapshot import MetricSnapshot
from shared.backend.utils.uuid import generateId

async def generateTestMetrics(days: int = 7, requestsPerHour: int = 50):
    """Generate test metrics spread over multiple days"""

    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    services = ['kauth', 'ksysadmin', 'ksyspayment']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    urls = [
        '/api/auth/login', '/api/auth/register', '/api/auth/health',
        '/api/payment/create', '/api/payment/status',
        '/api/admin/metrics', '/api/admin/users'
    ]

    now = datetime.utcnow()
    start = now - timedelta(days=days)

    metrics = []
    totalHours = days * 24

    print(f"Generating {totalHours} hours of metrics ({requestsPerHour} req/hour)...")

    async with async_session() as session:
        for hourOffset in range(totalHours):
            baseTime = start + timedelta(hours=hourOffset)

            # Vary requests per hour (more during daytime)
            hour = baseTime.hour
            multiplier = 1.5 if 8 <= hour <= 20 else 0.7
            numRequests = int(requestsPerHour * multiplier)

            for i in range(numRequests):
                # Spread requests within the hour
                timestamp = baseTime + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59))

                # Realistic status codes (mostly 200, some errors)
                statusRand = random.random()
                if statusRand < 0.95:
                    status = 200
                elif statusRand < 0.98:
                    status = random.choice([400, 404, 422])
                else:
                    status = random.choice([500, 502, 503])

                metric = MetricSnapshot(
                    id=generateId(),
                    timestamp=timestamp,
                    service=random.choice(services),
                    remote_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    request_id=f"req_{generateId()}",
                    method=random.choice(methods),
                    url=random.choice(urls),
                    status=status,
                    rate_limited=random.random() < 0.02,  # 2% rate limited
                    user_agent="TestDataGenerator/1.0",
                    nginx_latency_ms=round(random.uniform(0.5, 5.0), 2),
                    backend_latency_ms=round(random.uniform(10.0, 150.0), 2) if status < 500 else None,
                    user_id=f"user_{random.randint(1, 1000)}" if random.random() < 0.7 else None
                )
                metrics.append(metric)

            # Batch insert every 100 metrics
            if len(metrics) >= 100:
                session.add_all(metrics)
                await session.commit()
                print(f"  Inserted {len(metrics)} metrics (hour {hourOffset+1}/{totalHours})")
                metrics = []

        # Insert remaining
        if metrics:
            session.add_all(metrics)
            await session.commit()
            print(f"  Inserted final {len(metrics)} metrics")

    await engine.dispose()
    print(f"\n✓ Generated test data for {days} days successfully!")

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    requestsPerHour = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    asyncio.run(generateTestMetrics(days, requestsPerHour))
