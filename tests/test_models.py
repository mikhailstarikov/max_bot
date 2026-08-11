"""Тесты моделей БД: создание, связи, ограничения уникальности."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from max_bot.db.models import (
    MediaType,
    Project,
    ProjectMedia,
    ProjectStatus,
    Service,
    Skill,
    User,
    UserRole,
)


async def test_user_default_role(session) -> None:
    """Новый пользователь по умолчанию получает роль USER."""
    session.add(User(max_user_id="100001", first_name="Max"))
    await session.commit()

    result = await session.execute(select(User).where(User.max_user_id == "100001"))
    created = result.scalar_one()

    assert created.role == UserRole.USER
    assert created.created_at is not None


async def test_user_max_user_id_unique(session) -> None:
    """Два пользователя с одним max_user_id — ошибка уникальности."""
    session.add(User(max_user_id="1"))
    await session.commit()

    session.add(User(max_user_id="1"))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_project_with_media(session) -> None:
    """Проект создаётся вместе со скриншотами, связь работает в обе стороны."""
    project = Project(
        title="TIX Converter",
        description="Конвертер билетов",
        price_from=50000,
        price_to=90000,
        status=ProjectStatus.PUBLISHED,
    )
    project.media.append(
        ProjectMedia(file_path="media/tix_1.png", media_type=MediaType.IMAGE),
    )
    session.add(project)
    await session.commit()

    created = (await session.execute(select(Project))).scalar_one()

    assert created.status == ProjectStatus.PUBLISHED
    assert len(created.media) == 1
    assert created.media[0].project_id == created.id


async def test_skill_and_service(session) -> None:
    """Навыки и услуги сохраняются и читаются."""
    session.add(Skill(name="Python", note="3+ года"))
    session.add(Service(title="Telegram-бот", price_from=30000, price_to=60000))
    await session.commit()

    skills = (await session.execute(select(Skill))).scalars().all()
    services = (await session.execute(select(Service))).scalars().all()

    assert skills[0].name == "Python"
    assert services[0].currency == "RUB"
