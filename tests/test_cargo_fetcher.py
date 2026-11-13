"""Тесты для модуля получения зависимостей Cargo."""

import unittest

from src.cargo_fetcher import (
    FetchError,
    build_index_path,
    build_package_url,
    parse_direct_dependencies,
)


class TestCargoFetcher(unittest.TestCase):
    """Набор тестов для проверки парсинга метаданных Cargo."""

    def test_index_paths(self) -> None:
        """Проверка формирования путей индекса для разной длины имён."""
        self.assertEqual(build_index_path("a"), "1/a")
        self.assertEqual(build_index_path("io"), "2/io")
        self.assertEqual(build_index_path("syn"), "3/s/syn")
        self.assertEqual(build_index_path("serde"), "se/rd/serde")

    def test_build_package_url(self) -> None:
        """Проверка генерации URL для sparse и github репозиториев."""
        url_sparse = build_package_url("https://index.crates.io/", "serde")
        self.assertEqual(
            url_sparse, "https://index.crates.io/se/rd/serde"
        )
        url_gh = build_package_url(
            "https://github.com/rust-lang/crates.io-index", "syn"
        )
        self.assertTrue(url_gh.endswith("/master/3/s/syn"))

    def test_parse_direct_dependencies(self) -> None:
        """Проверка извлечения прямых normal-зависимостей последней версии."""
        sample_ndjson = (
            '{"name":"demo","vers":"0.1.0","deps":['
            '{"name":"old_dep","req":"^0.1","kind":"normal"}],'
            '"yanked":false}\n'
            '{"name":"demo","vers":"0.2.0","deps":['
            '{"name":"serde","req":"^1.0","kind":"normal"},'
            '{"name":"cc","req":"^1.0","kind":"build"},'
            '{"name":"tokio","req":"^1.0","kind":"dev"}],'
            '"yanked":false}\n'
            '{"name":"demo","vers":"0.3.0","deps":[],'
            '"yanked":true}\n'
        )
        version, deps = parse_direct_dependencies(sample_ndjson)
        self.assertEqual(version, "0.2.0")
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]["name"], "serde")
        self.assertEqual(deps[0]["req"], "^1.0")

    def test_empty_metadata_error(self) -> None:
        """Проверка ошибки при пустых метаданных."""
        with self.assertRaises(FetchError):
            parse_direct_dependencies("   \n  ")


if __name__ == "__main__":
    unittest.main()
