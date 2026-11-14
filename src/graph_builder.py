"""Модуль построения транзитивного графа зависимостей методом DFS."""

from collections.abc import Callable


class GraphError(Exception):
    """Исключение при разборе тестового репозитория или построении графа."""


def _validate_test_pkg_name(name: str) -> None:
    """Проверяет, что имя пакета состоит из заглавных латинских букв."""
    if not name or not name.isalpha() or not name.isupper() or not name.isascii():
        raise GraphError(
            f"Имя пакета в тестовом репозитории должно состоять из "
            f"заглавных латинских букв: '{name}'"
        )


def parse_test_repository(file_path: str) -> dict[str, list[str]]:
    """Читает граф зависимостей из файла тестового репозитория."""
    graph: dict[str, list[str]] = {}
    with open(file_path, mode="r", encoding="utf-8") as repo_file:
        for line_num, raw_line in enumerate(repo_file, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise GraphError(
                    f"Ошибка синтаксиса в строке {line_num}: отсутствует ':'"
                )
            pkg_part, deps_part = line.split(":", maxsplit=1)
            pkg = pkg_part.strip()
            _validate_test_pkg_name(pkg)

            deps: list[str] = []
            for raw_dep in deps_part.split(","):
                dep = raw_dep.strip()
                if dep:
                    _validate_test_pkg_name(dep)
                    deps.append(dep)
            graph[pkg] = deps
    return graph


def build_dependency_graph(
    root_package: str,
    get_deps: Callable[[str], list[str]],
) -> tuple[dict[str, list[str]], set[tuple[str, str]]]:
    """Строит транзитивный граф зависимостей алгоритмом DFS с рекурсией."""
    graph: dict[str, list[str]] = {}
    cyclic_edges: set[tuple[str, str]] = set()
    visited: set[str] = set()
    active_path: set[str] = set()

    def dfs(current: str) -> None:
        visited.add(current)
        active_path.add(current)
        deps = get_deps(current)
        graph[current] = deps

        for dep in deps:
            if dep in active_path:
                cyclic_edges.add((current, dep))
            elif dep not in visited:
                dfs(dep)

        active_path.remove(current)

    dfs(root_package)
    return graph, cyclic_edges
