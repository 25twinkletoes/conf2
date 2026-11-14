"""Модуль для чтения и валидации CSV-конфигурации."""

import csv
import os
from urllib.parse import urlparse

REQUIRED_KEYS = {
    "package_name",
    "repo_url",
    "test_mode",
    "output_file",
}
VALID_EXTENSIONS = (".png",)


class ConfigError(Exception):
    """Исключение для ошибок конфигурации."""


def _parse_bool(value: str) -> bool:
    """Преобразует строковое значение в логический тип."""
    lowered = value.strip().lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no"):
        return False
    raise ConfigError(
        f"Некорректное булево значение для test_mode: '{value}'"
    )


def _validate_url_or_path(repo_url: str, test_mode: bool) -> None:
    """Проверяет URL репозитория"""
    if not repo_url:
        raise ConfigError("Параметр repo_url не может быть пустым.")

    if test_mode:
        if not os.path.isfile(repo_url):
            raise ConfigError(
                f"Файл тестового репозитория не найден: '{repo_url}'"
            )
        return

    parsed = urlparse(repo_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigError(
            f"Некорректный URL репозитория: '{repo_url}'"
        )


def _validate_params(raw_config: dict[str, str]) -> dict[str, object]:
    """обязательных параметров."""
    missing = REQUIRED_KEYS - raw_config.keys()
    if missing:
        raise ConfigError(f"Отсутствуют обязательные параметры: {missing}")

    pkg = raw_config["package_name"].strip()
    if not pkg or " " in pkg:
        raise ConfigError(f"Некорректное имя пакета: '{pkg}'")

    test_mode = _parse_bool(raw_config["test_mode"])
    repo_url = raw_config["repo_url"].strip()
    _validate_url_or_path(repo_url, test_mode)

    out_file = raw_config["output_file"].strip()
    if not out_file or not out_file.lower().endswith(VALID_EXTENSIONS):
        raise ConfigError(
            f"Имя выходного файла должно иметь расширение .png: '{out_file}'"
        )

    return {
        "package_name": pkg,
        "repo_url": repo_url,
        "test_mode": test_mode,
        "output_file": out_file,
    }


def load_config(file_path: str) -> dict[str, object]:
    """Загружает конфигурацию из CSV-файла и возвращает словарь."""
    if not os.path.isfile(file_path):
        raise ConfigError(f"Файл конфигурации не найден: '{file_path}'")

    raw_config: dict[str, str] = {}
    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames or set(reader.fieldnames) != {"key", "value"}:
            raise ConfigError(
                "CSV должен содержать заголовки 'key,value'."
            )
        for row in reader:
            if row["key"] is None or row["value"] is None:
                raise ConfigError("Обнаружена некорректная строка в CSV.")
            raw_config[row["key"].strip()] = row["value"]

    return _validate_params(raw_config)
