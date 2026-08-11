"""Alembic-окружение для async SQLAlchemy.

Стандартный env.py синхронный, а мы используем aiosqlite,
поэтому здесь async-движок и запуск миграций через asyncio.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from max_bot.core.config import get_settings
from max_bot.db import models  # noqa: F401
from max_bot.db.base import Base

settings = get_settings()

# SQLite не создаёт папки сам, поэтому создаём её до подключения
settings.data_dir.mkdir(parents=True, exist_ok=True)

config = context.config

# URL базы всегда берём из настроек приложения
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Описание всех таблиц: Alembic сравнивает metadata с реальной БД
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме, без подключения к БД."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # batch-режим: обход ограничений ALTER TABLE в SQLite
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Применяет миграции на переданном подключении."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # batch-режим: обход ограничений ALTER TABLE в SQLite
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаёт async-движок и прогоняет миграции."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
