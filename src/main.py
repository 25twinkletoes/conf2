"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys

from src.cargo_fetcher import FetchError, get_direct_dependencies
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
    """Запускает приложение и выводит прямые зависимости пакета."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        pkg_name = str(config["package_name"])
        repo_url = str(config["repo_url"])
        version, deps = get_direct_dependencies(repo_url, pkg_name)
    except (ConfigError, FetchError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1

    print(f"Прямые зависимости пакета '{pkg_name}' (версия {version}):")
    if not deps:
        print("Прямые зависимости отсутствуют.")
        return 0

    for dep in deps:
        print(f"- {dep['name']} ({dep['req']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
