"""Тесты сервиса проектов: фильтрация, сортировка, подгрузка медиа."""

from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.db.models import Project, ProjectMedia, ProjectStatus
from max_bot.services.project_service import ProjectService


async def _add_project(
    session: AsyncSession,
    title: str,
    status: ProjectStatus,
    sort_order: int = 0,
    with_media: bool = False,
) -> Project:
    """Помощник: создаёт и сохраняет проект, чтобы не дублировать код в тестах."""
    project = Project(title=title, status=status, sort_order=sort_order)
    if with_media:
        project.media.append(ProjectMedia(file_path=f"media/{title}.png"))
    session.add(project)
    await session.commit()
    return project


async def test_returns_only_published(session: AsyncSession) -> None:
    """Сервис отдаёт только опубликованные проекты, черновики и архив не лезут."""
    await _add_project(session, "Draft", ProjectStatus.DRAFT)
    await _add_project(session, "Published", ProjectStatus.PUBLISHED)
    await _add_project(session, "Archived", ProjectStatus.ARCHIVED)

    projects = await ProjectService(session).get_published_projects()

    assert [p.title for p in projects] == ["Published"]


async def test_sorted_by_sort_order(session: AsyncSession) -> None:
    """Проекты приходят в порядке sort_order, а не как записались в БД."""
    await _add_project(session, "Second", ProjectStatus.PUBLISHED, sort_order=2)
    await _add_project(session, "First", ProjectStatus.PUBLISHED, sort_order=1)

    projects = await ProjectService(session).get_published_projects()

    assert [p.title for p in projects] == ["First", "Second"]


async def test_media_loaded_with_project(session: AsyncSession) -> None:
    """Скрины подгружаются вместе с проектом (selectinload работает)."""
    await _add_project(session, "TIX", ProjectStatus.PUBLISHED, with_media=True)

    projects = await ProjectService(session).get_published_projects()

    assert len(projects[0].media) == 1
    assert projects[0].media[0].file_path == "media/TIX.png"


async def test_get_project_by_id_missing(session: AsyncSession) -> None:
    """Несуществующий проект возвращает None, а не исключение."""
    assert await ProjectService(session).get_project_by_id(999) is None