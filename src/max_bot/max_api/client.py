"""Клиенты MAX: реальный и фейковый, плюс фабрика выбора.

MaxClient — общий интерфейс, чтобы логика бота не зависела от того,
куда уходят сообщения. В тестах и демо работает FakeMaxClient,
в продакшене — RealMaxClient; переключение одной настройкой max_mode.
"""

from typing import Protocol

import httpx

from max_bot.core.config import Settings
from max_bot.max_api.schemas import MaxUpdate


class MaxClient(Protocol):
    """Интерфейс клиента: боту достаточно уметь отправлять сообщения."""

    async def send_message(self, chat_id: int, text: str) -> None:
        """Отправить текстовое сообщение в чат."""
        ...


class FakeMaxClient:
    """Фейковый клиент MAX для тестов и демо-режима.

    Не ходит в сеть: складывает отправленные сообщения в список,
    который потом можно проверить в тестах или показать в консоли.
    """

    def __init__(self) -> None:
        self.sent_messages: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str) -> None:
        """Сохранить сообщение в память вместо отправки в сеть."""
        self.sent_messages.append((chat_id, text))


class RealMaxClient:
    """Реальный клиент MAX: HTTP-запросы к Bot API."""

    def __init__(self, settings: Settings) -> None:
        self._base = settings.max_api_base.rstrip("/")
        self._token = settings.bot_token

    async def send_message(self, chat_id: int, text: str) -> None:
        """POST /messages — отправка сообщения в чат."""
        async with httpx.AsyncClient(base_url=self._base) as client:
            await client.post(
                "/messages",
                headers={"Authorization": f"Bearer {self._token}"},
                json={"chat_id": chat_id, "text": text},
            )

    async def get_updates(self, marker: str = "") -> tuple[list[MaxUpdate], str]:
        """GET /updates — long polling: события плюс новый marker для следующего запроса."""
        async with httpx.AsyncClient(base_url=self._base) as client:
            response = await client.get(
                "/updates",
                headers={"Authorization": f"Bearer {self._token}"},
                params={"marker": marker},
            )
        payload = response.json()
        updates = [MaxUpdate(**u) for u in payload.get("updates", [])]
        return updates, payload.get("marker", "")


def build_max_client(settings: Settings) -> MaxClient:
    """Выбирает клиента по настройкам: реальный только при mode=real и токене."""
    if settings.max_mode == "real" and settings.bot_token:
        return RealMaxClient(settings)
    return FakeMaxClient()
