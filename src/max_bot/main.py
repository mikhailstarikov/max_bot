"""Точка входа приложения: сборка FastAPI и запуск сервера."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from max_bot.api.catalog import router as catalog_router
from max_bot.api.projects import router as projects_router
from max_bot.core.config import get_settings
from max_bot.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: настройка при старте и остановке."""
    setup_logging()
    logger.info("Max bot started")
    yield
    logger.info("Max bot stopped")


def create_app() -> FastAPI:
    """Собирает и возвращает готовое FastAPI-приложение."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.include_router(projects_router)
    app.include_router(catalog_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Простая проверка, что сервер жив."""
        return {"status": "ok", "name": settings.app_name}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "max_bot.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
