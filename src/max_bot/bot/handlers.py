"""Обработчики команд бота: входящее сообщение -> текст ответа.

Обработчик не знает, откуда пришло сообщение и куда уйдёт ответ:
он принимает update и клиент. Клиент подменяемый (реальный MAX или
фейк) — это и есть паттерн адаптер.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.db.models import User, UserRole
from max_bot.max_api.client import MaxClient
from max_bot.max_api.schemas import MaxUpdate
from max_bot.services.catalog import ServiceService, SkillService
from max_bot.services.project_service import ProjectService

MENU = "Меню:\n/projects — проекты\n/services — услуги и цены\n/skills — навыки"


def _format_price(price_from: int | None, price_to: int | None, currency: str) -> str:
    """Собирает вилку цены: '30000–60000 RUB' или 'цена по запросу'."""
    if price_from is not None and price_to is not None:
        return f"{price_from}–{price_to} {currency}"
    return "цена по запросу"


class BotHandler:
    """Обрабатывает один update: определяет ответ и отправляет его через клиент."""

    def __init__(self, session: AsyncSession, client: MaxClient) -> None:
        self._session = session
        self._client = client

    async def _get_or_create_user(self, update: MaxUpdate) -> User:
        """Ищет пользователя по MAX-id, создаёт при первом сообщении."""
        max_user_id = str(update.message.user.user_id)
        result = await self._session.execute(
            select(User).where(User.max_user_id == max_user_id),
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                max_user_id=max_user_id,
                first_name=update.message.user.first_name or None,
                last_name=update.message.user.last_name or None,
                username=update.message.user.username or None,
            )
            self._session.add(user)
            await self._session.commit()
        return user

    async def process(self, update: MaxUpdate) -> None:
        """Обрабатывает update: отправляет ответ, если пользователь не забанен."""
        user = await self._get_or_create_user(update)
        if user.role == UserRole.BANNED:
            # забаненных молча игнорируем — те самые «долбоебы из чата»
            return

        text = await self._reply_for(update.message.text.strip())
        await self._client.send_message(update.message.chat_id, text)

    async def _reply_for(self, text: str) -> str:
        """Выбирает ответ по команде пользователя."""
        command = text.lower()
        if command in ("/start", "menu", "меню"):
            return MENU
        if command in ("/projects", "projects", "проекты"):
            return await self._projects_text()
        if command in ("/services", "services", "услуги"):
            return await self._services_text()
        if command in ("/skills", "skills", "навыки"):
            return await self._skills_text()
        return f"Не знаю такой команды. {MENU}"

    async def _projects_text(self) -> str:
        projects = await ProjectService(self._session).get_published_projects()
        if not projects:
            return "Портфолио пока наполняется."
        lines = ["Мои проекты:"]
        for project in projects:
            lines.append(f"• {project.title} — {project.description or 'без описания'}")
        return "\n".join(lines)

    async def _services_text(self) -> str:
        services = await ServiceService(self._session).get_services()
        if not services:
            return "Список услуг пока наполняется."
        lines = ["Услуги и цены:"]
        for service in services:
            price = _format_price(service.price_from, service.price_to, service.currency)
            lines.append(f"• {service.title}: {price}")
        return "\n".join(lines)

    async def _skills_text(self) -> str:
        skills = await SkillService(self._session).get_skills()
        if not skills:
            return "Список навыков пока наполняется."
        lines = ["Навыки:"]
        for skill in skills:
            lines.append(f"• {skill.name}")
        return "\n".join(lines)
