"""Настройки приложения: читаются из переменных окружения и файла .env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Все настройки в одном месте; значения можно переопределить через .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "max-bot"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'max_bot.db'}"

    max_mode: str = "fake"

    bot_token: str = ""

    max_api_base: str = "https://botapi.max.ru"

    data_dir: Path = BASE_DIR / "data"
    media_dir: Path = BASE_DIR / "media"
    log_dir: Path = BASE_DIR / "logs"


@lru_cache
def get_settings() -> Settings:
    """Отдаёт настройки одним экземпляром на всё приложение."""
    return Settings()
