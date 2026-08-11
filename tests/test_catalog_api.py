"""Тесты API-эндпоинтов каталога: навыки и услуги."""

from max_bot.db.models import Service, Skill


async def test_skills_empty(client) -> None:
    """Если навыков нет, API возвращает пустой список."""
    response = await client.get("/skills")

    assert response.status_code == 200
    assert response.json() == []


async def test_skills_sorted_by_name(client, session) -> None:
    """Навыки приходят отсортированными по имени."""
    session.add(Skill(name="Python"))
    session.add(Skill(name="FastAPI", note="асинхронные веб-приложения"))
    await session.commit()

    response = await client.get("/skills")

    assert response.status_code == 200
    data = response.json()
    assert [s["name"] for s in data] == ["FastAPI", "Python"]


async def test_services_list(client, session) -> None:
    """Эндпоинт услуг возвращает услуги с ценами."""
    session.add(Service(title="Telegram-бот", price_from=30000, price_to=60000))
    await session.commit()

    response = await client.get("/services")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Telegram-бот"
    assert data[0]["price_from"] == 30000
