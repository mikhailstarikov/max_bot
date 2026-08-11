"""Модели данных портфолио-бота.
Связи: у Project может быть много ProjectMedia (one-to-many).
"""

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from max_bot.db.base import Base, TimestampMixin


class UserRole(enum.StrEnum):
    """Роль пользователя MAX в боте."""

    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    BANNED = "banned"


class ProjectStatus(enum.StrEnum):
    """Статус проекта портфолио."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class MediaType(enum.StrEnum):
    """Тип медиафайла проекта."""

    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class User(TimestampMixin, Base):
    """Пользователь мессенджера MAX, который написал боту."""

    __tablename__ = "users"

    # max_user_id — это id из MAX, а не наш внутренний id
    max_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)


class Project(TimestampMixin, Base):
    """Проект портфолио: название, описание, вилка цены и сроки."""

    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    price_from: Mapped[int | None]
    price_to: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    duration: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus),
        default=ProjectStatus.DRAFT,
    )
    sort_order: Mapped[int] = mapped_column(default=0)

    # cascade="all, delete-orphan" удаляет скриншоты вместе с проектом
    media: Mapped[list["ProjectMedia"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMedia.sort_order",
    )


class ProjectMedia(TimestampMixin, Base):
    """Скриншот, видео или файл, прикреплённый к проекту."""

    __tablename__ = "project_media"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(512))
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), default=MediaType.IMAGE)
    caption: Mapped[str | None] = mapped_column(String(512))
    sort_order: Mapped[int] = mapped_column(default=0)

    project: Mapped[Project] = relationship(back_populates="media")


class Skill(TimestampMixin, Base):
    """Навык из резюме (Python, FastAPI и т.д.)."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(120), unique=True)
    note: Mapped[str | None] = mapped_column(String(512))


class Service(TimestampMixin, Base):
    """Услуга с вилкой цены и сроков — то, что бот показывает людям."""

    __tablename__ = "services"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    price_from: Mapped[int | None]
    price_to: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(8), default="RUB")
    duration: Mapped[str | None] = mapped_column(String(120))
