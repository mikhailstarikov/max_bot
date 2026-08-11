"""Async-движок и сессии SQLAlchemy.

async-сессии нужны, потому что FastAPI работает в event loop
и не должен блокироваться на запросах к БД.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from max_bot.core.config import get_settings
from max_bot.db.base import Base

settings = get_settings()

# SQLite файл должен лежать в существующей папке, создаём её заранее
if settings.database_url.startswith("sqlite"):
    settings.data_dir.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(settings.database_url, echo=False)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-зависимость: отдаёт сессию БД на один HTTP-запрос."""
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    """Создаёт все таблицы (для разработки; позже заменим на Alembic)."""
    import max_bot.db.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
