"""Сервис проектов: бизнес-логика портфолио.

Сервисы отделяют логику работы с данными от бота и API:
одни и те же методы будут использовать и бот MAX, и админка.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from max_bot.db.models import Project, ProjectStatus


class ProjectService:
    """Операции с проектами портфолио.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_published_projects(self) -> list[Project]:
        """Возвращает опубликованные проекты в порядке показа, сразу со скринами."""
        result = await self._session.execute(
            select(Project)
            .where(Project.status == ProjectStatus.PUBLISHED)
            .order_by(Project.sort_order, Project.id)
            .options(selectinload(Project.media))
        )
        return list(result.scalars().unique().all())

    async def get_project_by_id(self, project_id: int) -> Project | None:
        """Возвращает проект со скринами по id или None, если не найден."""
        result = await self._session.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.media))
        )
        return result.unique().scalar_one_or_none()