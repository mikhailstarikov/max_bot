import sys

from loguru import logger

from max_bot.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    logger.remove()

    logger.add(
        sys.stderr,
        level="DEBUG" if settings.debug else "INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        settings.log_dir / "app.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
    )
