"""Тест демо-режима: цикл обрабатывает строки и бот отвечает."""

from max_bot.bot.demo import run_demo_loop
from max_bot.db.models import Project, ProjectStatus


async def test_demo_loop_replies(session) -> None:
    """Демо-цикл отвечает на /start и /projects, используя реальную логику."""
    session.add(Project(title="TIX Converter", status=ProjectStatus.PUBLISHED))
    await session.commit()

    replies = await run_demo_loop(["/start", "/projects"], session)

    assert any("/projects" in reply for reply in replies)
    assert any("TIX Converter" in reply for reply in replies)
