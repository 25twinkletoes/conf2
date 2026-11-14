"""Точка входа CLI-приложения визуализации графа зависимостей."""

import argparse
import sys

from src.cargo_fetcher import FetchError, get_direct_dependencies
from src.config_parser import ConfigError, load_config
from src.graph_builder import (
    GraphError,
    build_dependency_graph,
    compute_load_order,
    parse_test_repository,
)


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
    parser.add_argument(
        "--load-order",
        action="store_true",
        help="Вывести порядок загрузки зависимостей для заданного пакета.",
    )
    return parser.parse_args(argv)


def _create_provider(repo_url: str, test_mode: bool):
    """Создает функцию получения прямых зависимостей для режима работы."""
    if test_mode:
        test_repo = parse_test_repository(repo_url)

        def fetch_from_test(pkg: str) -> list[str]:
            if pkg not in test_repo:
                raise GraphError(
                    f"Пакет '{pkg}' не найден в тестовом репозитории."
                )
            return test_repo[pkg]

        return fetch_from_test

    cache: dict[str, list[str]] = {}

    def fetch_from_cargo(pkg: str) -> list[str]:
        if pkg not in cache:
            _, deps = get_direct_dependencies(repo_url, pkg)
            cache[pkg] = [item["name"] for item in deps]
        return cache[pkg]

    return fetch_from_cargo


def _print_graph(
    root: str,
    graph: dict[str, list[str]],
    cycles: set[tuple[str, str]],
) -> None:
    """Выводит построенный транзитивный граф зависимостей на экран."""
    print(f"Граф зависимостей для пакета '{root}':")
    for pkg, deps in graph.items():
        if not deps:
            print(f"{pkg} -> (нет зависимостей)")
            continue
        formatted = [
            f"{dep} [цикл]" if (pkg, dep) in cycles else dep
            for dep in deps
        ]
        print(f"{pkg} -> {', '.join(formatted)}")


def _print_load_order(root: str, order: list[str]) -> None:
    """Выводит порядок загрузки зависимостей на экран."""
    print(f"Порядок загрузки зависимостей для пакета '{root}':")
    for idx, pkg in enumerate(order, start=1):
        print(f"{idx}. {pkg}")


def main(argv: list[str] | None = None) -> int:
    """Запускает приложение и выполняет анализ зависимостей."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        pkg_name = str(config["package_name"])
        repo_url = str(config["repo_url"])
        test_mode = bool(config["test_mode"])
        provider = _create_provider(repo_url, test_mode)
        graph, cycles = build_dependency_graph(pkg_name, provider)
    except (ConfigError, FetchError, GraphError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1

    if args.load_order:
        order = compute_load_order(pkg_name, graph)
        _print_load_order(pkg_name, order)
    else:
        _print_graph(pkg_name, graph, cycles)
    return 0


if __name__ == "__main__":
    sys.exit(main())
