"""Модуль получения прямых зависимостей пакетов Rust (Cargo)."""

import json
import urllib.error
import urllib.request

LEN_ONE = 1
LEN_TWO = 2
LEN_THREE = 3
PREFIX_SPLIT = 2
REQUEST_TIMEOUT = 15
USER_AGENT = "dep-visualizer-cli/0.2"


class FetchError(Exception):
    """Исключение при получении или разборе метаданных пакета."""


def build_index_path(package_name: str) -> str:
    """Формирует относительный путь к файлу пакета в индексе Cargo."""
    name = package_name.strip().lower()
    if not name:
        raise FetchError("Имя пакета не может быть пустым.")

    length = len(name)
    if length == LEN_ONE:
        return f"1/{name}"
    if length == LEN_TWO:
        return f"2/{name}"
    if length == LEN_THREE:
        return f"3/{name[0]}/{name}"
    return f"{name[:PREFIX_SPLIT]}/{name[PREFIX_SPLIT:PREFIX_SPLIT * 2]}/{name}"


def build_package_url(repo_url: str, package_name: str) -> str:
    """Строит полный URL файла метаданных пакета в репозитории."""
    base = repo_url.rstrip("/")
    github_prefix = "https://github.com/rust-lang/crates.io-index"
    if base.startswith(github_prefix):
        base = "https://raw.githubusercontent.com/rust-lang/crates.io-index/master"
    rel_path = build_index_path(package_name)
    return f"{base}/{rel_path}"


def fetch_raw_metadata(url: str) -> str:
    """Загружает текстовое содержимое файла метаданных по URL."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        raise FetchError(f"HTTP ошибка {err.code} при запросе {url}") from err
    except urllib.error.URLError as err:
        raise FetchError(f"Ошибка сети при запросе {url}: {err.reason}") from err


def parse_direct_dependencies(raw_lines: str) -> tuple[str, list[dict[str, str]]]:
    """Извлекает версию и список прямых зависимостей из JSON-строк."""
    records = []
    for line in raw_lines.splitlines():
        cleaned = line.strip()
        if cleaned:
            try:
                records.append(json.loads(cleaned))
            except json.JSONDecodeError as err:
                raise FetchError("Некорректный JSON в индексе пакета.") from err

    if not records:
        raise FetchError("Файл метаданных пакета пуст.")

    active = [rec for rec in records if not rec.get("yanked", False)]
    latest = active[-1] if active else records[-1]
    version = str(latest.get("vers", "unknown"))

    deps: list[dict[str, str]] = []
    for dep in latest.get("deps", []):
        kind = dep.get("kind") or "normal"
        if kind == "normal":
            deps.append(
                {
                    "name": str(dep.get("name", "")),
                    "req": str(dep.get("req", "*")),
                }
            )
    return version, deps


def get_direct_dependencies(
    repo_url: str, package_name: str
) -> tuple[str, list[dict[str, str]]]:
    """Получает версию и прямые зависимости пакета из репозитория Cargo."""
    url = build_package_url(repo_url, package_name)
    raw_data = fetch_raw_metadata(url)
    return parse_direct_dependencies(raw_data)
