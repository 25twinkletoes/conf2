"""Тесты для построения транзитивного графа зависимостей методом DFS."""

import tempfile
import unittest
from pathlib import Path

from src.graph_builder import (
    GraphError,
    build_dependency_graph,
    parse_test_repository,
)


class TestGraphBuilder(unittest.TestCase):
    """Набор тестов для модуля graph_builder."""

    def _write_repo(self, content: str) -> str:
        """Создает временный файл тестового репозитория."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_parse_valid_test_repo(self) -> None:
        """Проверка разбора корректного тестового репозитория."""
        path = self._write_repo("A: B, C\nB: D\nC:\nD:\n")
        repo = parse_test_repository(path)
        self.assertEqual(repo, {"A": ["B", "C"], "B": ["D"], "C": [], "D": []})

    def test_invalid_package_name_in_repo(self) -> None:
        """Ошибка, если имя пакета не из заглавных латинских букв."""
        path = self._write_repo("a: B\nB:\n")
        with self.assertRaises(GraphError):
            parse_test_repository(path)

    def test_dfs_transitive_and_cycles(self) -> None:
        """Проверка рекурсивного DFS с транзитивностью и циклами."""
        repo = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["B", "A"],
            "D": [],
        }
        graph, cycles = build_dependency_graph("A", lambda p: repo[p])
        self.assertEqual(set(graph.keys()), {"A", "B", "C", "D"})
        self.assertIn(("C", "A"), cycles)
        self.assertNotIn(("C", "B"), cycles)


if __name__ == "__main__":
    unittest.main()
