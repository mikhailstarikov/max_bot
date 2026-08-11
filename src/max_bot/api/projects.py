"""API-роутер проектов: список проектов и детали одного проекта."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.api.schemas import ProjectResponse
from max_bot.db.session import get_db
from max_bot.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[ProjectResponse]:
    """Возвращает список опубликованных проектов в порядке показа."""
    return await ProjectService(session).get_published_projects()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> ProjectResponse:
    """Возвращает один проект со скриншотами. 404, если не найден."""
    project = await ProjectService(session).get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
