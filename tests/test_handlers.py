"""Тесты обработчиков бота: пришёл update -> ожидаемый ответ."""

from sqlalchemy import select

from max_bot.bot.handlers import BotHandler
from max_bot.db.models import Project, ProjectStatus, Service, Skill, User, UserRole
from max_bot.max_api.client import FakeMaxClient
from max_bot.max_api.schemas import MaxMessage, MaxUpdate, MaxUser


def _update(text: str, user_id: int = 1) -> MaxUpdate:
    """Собирает update для тестов."""
    return MaxUpdate(
        update_id=1,
        message=MaxMessage(chat_id=10, user=MaxUser(user_id=user_id), text=text),
    )


async def test_start_shows_menu(session) -> None:
    """Команда /start показывает меню со списком команд."""
    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/start"))

    assert len(client.sent_messages) == 1
    assert "/projects" in client.sent_messages[0][1]


async def test_projects_command(session) -> None:
    """Команда /projects показывает опубликованные проекты."""
    session.add(Project(title="TIX Converter", status=ProjectStatus.PUBLISHED))
    await session.commit()

    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/projects"))

    assert "TIX Converter" in client.sent_messages[0][1]


async def test_services_command(session) -> None:
    """Команда /services показывает услуги с вилкой цен."""
    session.add(Service(title="Telegram-бот", price_from=30000, price_to=60000))
    await session.commit()

    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/services"))

    assert "30000–60000 RUB" in client.sent_messages[0][1]


async def test_skills_command(session) -> None:
    """Команда /skills показывает навыки."""
    session.add(Skill(name="Python"))
    await session.commit()

    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/skills"))

    assert "Python" in client.sent_messages[0][1]


async def test_unknown_command(session) -> None:
    """На неизвестную команду бот отвечает вежливо и показывает меню."""
    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("блабла"))

    assert "Не знаю такой команды" in client.sent_messages[0][1]


async def test_banned_user_ignored(session) -> None:
    """Забаненный пользователь не получает ответов."""
    session.add(User(max_user_id="7", role=UserRole.BANNED))
    await session.commit()

    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/start", user_id=7))

    assert client.sent_messages == []


async def test_new_user_created(session) -> None:
    """При первом сообщении бот создаёт пользователя в БД."""
    client = FakeMaxClient()
    await BotHandler(session, client).process(_update("/start", user_id=42))

    result = await session.execute(select(User).where(User.max_user_id == "42"))
    assert result.scalar_one() is not None
