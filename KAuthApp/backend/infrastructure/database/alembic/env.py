from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
from pathlib import Path

# Add project root to path (5 levels up from env.py to k-services root)
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

# Import SQLModel metadata
from sqlmodel import SQLModel

# Import KAuthApp models
from KAuthApp.backend.domain.models.user import User
from KAuthApp.backend.domain.models.refreshToken import RefreshToken

# Import settings
from shared.backend.config.settings import settings

# Alembic Config object
config = context.config

# Set database URL from settings (use async URL)
config.set_main_option('sqlalchemy.url', settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for autogenerate support
target_metadata = SQLModel.metadata


def runMigrationsOffline() -> None:
    """
    Run migrations in 'offline' mode.
    No database connection required - generates SQL scripts.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_version_kauth"
    )

    with context.begin_transaction():
        context.run_migrations()


def doRunMigrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table="alembic_version_kauth"
    )

    with context.begin_transaction():
        context.run_migrations()


async def runAsyncMigrations() -> None:
    """
    Run migrations using async engine with asyncpg.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(doRunMigrations)

    await connectable.dispose()


def runMigrationsOnline() -> None:
    """
    Run migrations in 'online' mode with async support.
    """
    asyncio.run(runAsyncMigrations())


if context.is_offline_mode():
    runMigrationsOffline()
else:
    runMigrationsOnline()
