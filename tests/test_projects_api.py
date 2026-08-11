"""Тесты API-эндпоинтов проектов."""

from max_bot.db.models import Project, ProjectMedia, ProjectStatus


async def test_empty_list(client) -> None:
    """Если проектов нет, API возвращает пустой список."""
    response = await client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == []


async def test_returns_published_projects(client, session) -> None:
    """API отдаёт только опубликованные проекты с медиа."""
    published = Project(
        title="TIX Converter",
        description="Конвертер",
        price_from=50000,
        price_to=90000,
        status=ProjectStatus.PUBLISHED,
    )
    published.media.append(ProjectMedia(file_path="media/tix.png"))
    session.add(published)
    session.add(Project(title="Draft", status=ProjectStatus.DRAFT))
    await session.commit()

    response = await client.get("/projects/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "TIX Converter"
    assert len(data[0]["media"]) == 1


async def test_get_project_by_id(client, session) -> None:
    """Эндпоинт проекта возвращает проект со скриншотами."""
    project = Project(title="TIX Converter", status=ProjectStatus.PUBLISHED)
    project.media.append(ProjectMedia(file_path="media/tix.png"))
    session.add(project)
    await session.commit()

    response = await client.get(f"/projects/{project.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "TIX Converter"
    assert len(data["media"]) == 1


async def test_get_project_not_found(client) -> None:
    """Несуществующий проект возвращает 404 с понятным сообщением."""
    response = await client.get("/projects/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
