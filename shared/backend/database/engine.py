from __future__ import annotations
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import structlog

from shared.backend.config.settings import settings

logger = structlog.get_logger()

# Global async engine instance
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def createEngine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling.
    100% non-blocking with asyncpg driver.
    """
    logger.info(
        "database_engine_creating",
        url=settings.database_url.split("@")[-1],  # Hide credentials
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow
    )

    engine_kwargs = {
        "url": settings.database_url,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_timeout": settings.database_pool_timeout,
        "pool_recycle": settings.database_pool_recycle,
        "pool_pre_ping": True,
        "echo": settings.debug,
        "echo_pool": settings.debug if settings.debug else False,
        "future": True,
    }

    if settings.debug:
        engine_kwargs["poolclass"] = NullPool

    engine = create_async_engine(**engine_kwargs)

    logger.info("database_engine_created")
    return engine


def createSessionFactory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory for database operations.
    Sessions are lazy-created and automatically managed.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
        autocommit=False,  # Explicit transaction control
        autoflush=False,  # Manual flush control
    )


async def initDb() -> None:
    """
    Initialize database engine and session factory.
    Called on application startup.
    """
    global _engine, _session_factory

    if _engine is not None:
        logger.warning("database_already_initialized")
        return

    try:
        _engine = createEngine()
        _session_factory = createSessionFactory(_engine)

        # Test connection
        async with _engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info(
            "database_initialized",
            environment=settings.environment,
            pool_size=settings.database_pool_size
        )
    except Exception as e:
        logger.error(
            "database_init_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


async def closeDb() -> None:
    """
    Close database engine and cleanup resources.
    Called on application shutdown.
    """
    global _engine, _session_factory

    if _engine is None:
        logger.warning("database_not_initialized")
        return

    try:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("database_closed")
    except Exception as e:
        logger.error(
            "database_close_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


async def getDb() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Provides async session with automatic transaction management.

    Usage:
        @router.get("/users")
        async def getUsers(session: AsyncSession = Depends(getDb)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    if _session_factory is None:
        logger.error("database_not_initialized_on_request")
        raise RuntimeError("Database not initialized. Call initDb() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(
                "database_session_error",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
        finally:
            await session.close()


def getEngine() -> AsyncEngine:
    """
    Get the global async engine instance.
    Useful for raw SQL operations or advanced use cases.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call initDb() first.")
    return _engine


async def checkConnection() -> bool:
    """
    Check if database connection is alive.
    Returns True if healthy, False otherwise.
    """
    try:
        engine = getEngine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(
            "database_health_check_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        return False
