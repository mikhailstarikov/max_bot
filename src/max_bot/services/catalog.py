"""Сервисы каталога: навыки и услуги (справочные данные).

Навыки и услуги — небольшие справочники, поэтому оба сервиса
живут в одном модуле, без потери читаемости.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.db.models import Service, Skill


class SkillService:
    """Операции с навыками."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_skills(self) -> list[Skill]:
        """Возвращает все навыки, отсортированные по имени."""
        result = await self._session.execute(select(Skill).order_by(Skill.name))
        return list(result.scalars().all())


class ServiceService:
    """Операции с услугами."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_services(self) -> list[Service]:
        """Возвращает все услуги, отсортированные по названию."""
        result = await self._session.execute(select(Service).order_by(Service.title))
        return list(result.scalars().all())
