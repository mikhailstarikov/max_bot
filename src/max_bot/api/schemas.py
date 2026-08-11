"""Pydantic-схемы для API: описывают форму JSON-ответов.

Схемы нужны для:
- валидации входных данных (когда позже добавим POST/PUT);
- сериализации моделей БД в JSON;
- автогенерации документации OpenAPI.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectMediaResponse(BaseModel):
    """Схема одного скриншота/файла проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    media_type: str
    caption: str | None
    sort_order: int


class ProjectResponse(BaseModel):
    """Схема проекта для API-ответа."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    price_from: int | None
    price_to: int | None
    currency: str
    duration: str | None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    media: list[ProjectMediaResponse]


class SkillResponse(BaseModel):
    """Схема навыка для API-ответа."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    note: str | None


class ServiceResponse(BaseModel):
    """Схема услуги для API-ответа."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    price_from: int | None
    price_to: int | None
    currency: str
    duration: str | None
