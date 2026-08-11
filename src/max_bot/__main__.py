"""Командная строка пакета: python -m max_bot <команда>."""

import click

from max_bot.bot.demo import start_demo


@click.group()
def cli() -> None:
    """Команды Max bot."""


@cli.command()
def demo() -> None:
    """Запустить демо-чат с ботом в терминале (без токена)."""
    start_demo()


if __name__ == "__main__":
    cli()
