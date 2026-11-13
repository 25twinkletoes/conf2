"""Тесты для проверки парсинга и валидации CSV-конфигурации."""

import tempfile
import unittest
from pathlib import Path

from src.config_parser import ConfigError, load_config


class TestConfigParser(unittest.TestCase):
    """Набор тестов для модуля config_parser."""

    def _write_csv(self, content: str) -> str:
        """Создает временный CSV-файл и возвращает путь к нему."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_valid_config(self) -> None:
        """Проверка корректного чтения валидной конфигурации."""
        csv_data = (
            "key,value\n"
            "package_name,tokio\n"
            "repo_url,https://github.com/rust-lang/crates.io-index\n"
            "test_mode,false\n"
            "output_file,deps.png\n"
        )
        path = self._write_csv(csv_data)
        cfg = load_config(path)
        self.assertEqual(cfg["package_name"], "tokio")
        self.assertFalse(cfg["test_mode"])

    def test_invalid_package_name(self) -> None:
        """Ошибка при пустом или содержащем пробелы имени пакета."""
        csv_data = (
            "key,value\n"
            "package_name,bad name\n"
            "repo_url,https://example.com\n"
            "test_mode,false\n"
            "output_file,graph.png\n"
        )
        path = self._write_csv(csv_data)
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_repo_url(self) -> None:
        """Ошибка при некорректном URL в обычном режиме."""
        csv_data = (
            "key,value\n"
            "package_name,serde\n"
            "repo_url,not_a_valid_url\n"
            "test_mode,false\n"
            "output_file,graph.png\n"
        )
        path = self._write_csv(csv_data)
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_missing_test_repo_file(self) -> None:
        """Ошибка при отсутствии тестового файла в режиме test_mode."""
        csv_data = (
            "key,value\n"
            "package_name,A\n"
            "repo_url,non_existent_repo.txt\n"
            "test_mode,true\n"
            "output_file,graph.png\n"
        )
        path = self._write_csv(csv_data)
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_test_mode(self) -> None:
        """Ошибка при некорректном булевом значении test_mode."""
        csv_data = (
            "key,value\n"
            "package_name,serde\n"
            "repo_url,https://example.com\n"
            "test_mode,maybe\n"
            "output_file,graph.png\n"
        )
        path = self._write_csv(csv_data)
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_invalid_output_file(self) -> None:
        """Ошибка при неподдерживаемом расширении выходного файла."""
        csv_data = (
            "key,value\n"
            "package_name,serde\n"
            "repo_url,https://example.com\n"
            "test_mode,false\n"
            "output_file,graph.exe\n"
        )
        path = self._write_csv(csv_data)
        with self.assertRaises(ConfigError):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
