"""Тесты клиентов MAX: фабрика выбора и фейковый клиент."""

from max_bot.core.config import Settings
from max_bot.max_api.client import FakeMaxClient, RealMaxClient, build_max_client


async def test_fake_client_stores_messages() -> None:
    """FakeMaxClient копит сообщения вместо отправки в сеть."""
    client = FakeMaxClient()
    await client.send_message(1, "привет")

    assert client.sent_messages == [(1, "привет")]


def test_build_client_default_is_fake() -> None:
    """Без токена фабрика возвращает фейковый клиент."""
    client = build_max_client(Settings(max_mode="fake"))

    assert isinstance(client, FakeMaxClient)


def test_build_client_real_when_token_set() -> None:
    """С режимом real и токеном фабрика возвращает реальный клиент."""
    settings = Settings(max_mode="real", bot_token="test-token")

    assert isinstance(build_max_client(settings), RealMaxClient)
