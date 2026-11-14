"""Тесты для генерации Graphviz DOT и рендеринга PNG."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.visualizer import generate_graphviz_dot, render_dot_to_png


class TestVisualizer(unittest.TestCase):
    """Набор тестов для модуля visualizer."""

    def test_generate_dot_with_cycle(self) -> None:
        """Проверка формирования DOT-описания с выделением циклов."""
        graph = {"A": ["B"], "B": ["A"]}
        cycles = {("B", "A")}
        dot = generate_graphviz_dot("A", graph, cycles)
        self.assertIn("digraph dependencies {", dot)
        self.assertIn('"A" -> "B";', dot)
        self.assertIn('"B" -> "A" [color="red", style="dashed", label="cycle"];', dot)

    def test_render_dot_fallback_kroki(self) -> None:
        """Проверка сохранения PNG через резервный API при отсутствии dot."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            out_path = tmp.name
        self.addCleanup(lambda: Path(out_path).unlink(missing_ok=True))

        fake_png = b"\x89PNG\r\n\x1a\nFAKE"

        class FakeResponse:
            def read(self) -> bytes:
                return fake_png

            def __enter__(self):
                return self

            def __exit__(self, *args) -> None:
                pass

        with (
            patch("shutil.which", return_value=None),
            patch("urllib.request.urlopen", return_value=FakeResponse()),
        ):
            render_dot_to_png("digraph dependencies {}", out_path)

        self.assertEqual(Path(out_path).read_bytes(), fake_png)


if __name__ == "__main__":
    unittest.main()
