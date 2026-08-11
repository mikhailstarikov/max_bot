"""API-роутер каталога: навыки и услуги."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.api.schemas import ServiceResponse, SkillResponse
from max_bot.db.session import get_db
from max_bot.services.catalog import ServiceService, SkillService

router = APIRouter(tags=["catalog"])


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[SkillResponse]:
    """Возвращает все навыки, отсортированные по имени."""
    return await SkillService(session).get_skills()


@router.get("/services", response_model=list[ServiceResponse])
async def list_services(
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[ServiceResponse]:
    """Возвращает все услуги, отсортированные по названию."""
    return await ServiceService(session).get_services()
