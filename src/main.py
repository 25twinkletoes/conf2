"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys

from src.config_parser import ConfigError, load_config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей (Cargo)."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.csv",
        help="Путь к конфигурационному файлу формата CSV.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Запускает приложение и выводит параметры конфигурации."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        return 1

    for key, value in config.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
