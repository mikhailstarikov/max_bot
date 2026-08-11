"""Демо-режим: чат с ботом прямо в терминале, без MAX и токена.

Удобен, чтобы показать бота в действии на видео и просто погонять руками.
"""

import asyncio
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from max_bot.bot.handlers import BotHandler
from max_bot.db.session import async_session_factory
from max_bot.max_api.client import FakeMaxClient
from max_bot.max_api.schemas import MaxMessage, MaxUpdate, MaxUser

DEMO_USER_ID = 1


def _make_update(update_id: int, text: str) -> MaxUpdate:
    """Собирает update, как будто он пришёл из MAX (фиксированный демо-пользователь)."""
    return MaxUpdate(
        update_id=update_id,
        message=MaxMessage(
            chat_id=DEMO_USER_ID,
            user=MaxUser(user_id=DEMO_USER_ID, first_name="Demo"),
            text=text,
        ),
    )


async def run_demo_loop(
    lines: Iterable[str],
    session: AsyncSession,
    client: FakeMaxClient | None = None,
    echo: bool = False,
) -> list[str]:
    """Обрабатывает каждую строку как сообщение пользователя и возвращает ответы.

    УДАЛИТЬ: echo=True печатает диалог в консоль (интерактив),
    в тестах echo=False и ответы проверяются через возвращаемый список.
    """
    client = client or FakeMaxClient()
    handler = BotHandler(session, client)
    replies: list[str] = []
    for update_id, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if echo:
            print(f"Ты: {line}")
        await handler.process(_make_update(update_id, line))
        for _, text in client.sent_messages:
            replies.append(text)
            if echo:
                print(f"Бот: {text}")
        client.sent_messages.clear()
    return replies


def start_demo() -> None:
    """Запускает интерактивное демо: читает строки из консоли до 'exit'."""

    def _read_lines() -> Iterable[str]:
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            if line.strip().lower() in ("exit", "выход"):
                break
            yield line

    async def _run() -> None:
        print("Демо-режим Max bot (токен не нужен).")
        print("Команды: /start, /projects, /services, /skills. Выход: 'exit'.")
        async with async_session_factory() as session:
            await run_demo_loop(_read_lines(), session, echo=True)

    asyncio.run(_run())
