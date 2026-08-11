"""Общие фикстуры тестов: изолированная in-memory БД и HTTP-клиент."""

from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from max_bot.db import models  # noqa: F401  # импорт регистрирует таблицы в metadata
from max_bot.db.base import Base
from max_bot.db.session import get_db
from max_bot.main import app


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Создаёт чистую in-memory БД и сессию для одного теста."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(session) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP-клиент приложения, у которого БД подменена на тестовую."""

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db] = _get_test_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
