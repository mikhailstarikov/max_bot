"""Схемы данных MAX Bot API.

Форматы описаны по общей логике MAX Bot API; когда появится токен,
сверь точные имена полей с официальной документацией и поправь при
необходимости. Логика бота от этих схем не зависит.
"""

from pydantic import BaseModel


class MaxUser(BaseModel):
    """Пользователь MAX, написавший боту."""

    user_id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""


class MaxMessage(BaseModel):
    """Одно входящее сообщение из MAX."""

    chat_id: int
    user: MaxUser
    text: str = ""


class MaxUpdate(BaseModel):
    """Входящее событие из MAX (новое сообщение)."""

    update_id: int
    message: MaxMessage
