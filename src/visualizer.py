"""Модуль генерации Graphviz DOT и сохранения изображения в PNG."""

import shutil
import subprocess
import urllib.error
import urllib.request

KROKI_GRAPHVIZ_PNG_URL = "https://kroki.io/graphviz/png"
RENDER_TIMEOUT = 20
USER_AGENT = "dep-visualizer-cli/0.5"


class VisualizationError(Exception):
    """Исключение при формировании или рендеринге диаграммы Graphviz."""


def generate_graphviz_dot(
    root_package: str,
    graph: dict[str, list[str]],
    cycles: set[tuple[str, str]],
) -> str:
    """Формирует текстовое представление графа на языке Graphviz (DOT)."""
    lines = [
        "digraph dependencies {",
        "    rankdir=TB;",
        '    node [shape=box, style=rounded, fontname="Arial"];',
        f'    "{root_package}" [style="rounded,filled", fillcolor="#E3F2FD"];',
    ]

    for pkg, deps in graph.items():
        if not deps and pkg != root_package:
            lines.append(f'    "{pkg}";')
        for dep in deps:
            if (pkg, dep) in cycles:
                lines.append(
                    f'    "{pkg}" -> "{dep}" '
                    f'[color="red", style="dashed", label="cycle"];'
                )
            else:
                lines.append(f'    "{pkg}" -> "{dep}";')

    lines.append("}")
    return "\n".join(lines) + "\n"


def _render_via_local_dot(dot_bin: str, dot_source: str, output_path: str) -> None:
    """Рендерит PNG-изображение с помощью локальной утилиты dot."""
    proc = subprocess.run(
        [dot_bin, "-Tpng", "-o", output_path],
        input=dot_source.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        err_msg = proc.stderr.decode("utf-8", errors="replace").strip()
        raise VisualizationError(f"Ошибка Graphviz dot: {err_msg}")


def _render_via_kroki(dot_source: str, output_path: str) -> None:
    """Рендерит PNG-изображение через публичный API Kroki (резервный метод)."""
    req = urllib.request.Request(
        KROKI_GRAPHVIZ_PNG_URL,
        data=dot_source.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=RENDER_TIMEOUT) as resp:
            png_bytes = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        raise VisualizationError(
            "Не удалось сгенерировать PNG: утилита 'dot' (Graphviz) не "
            f"установлена, а онлайн-рендеринг недоступен ({err})."
        ) from err

    with open(output_path, mode="wb") as out_file:
        out_file.write(png_bytes)


def render_dot_to_png(dot_source: str, output_path: str) -> None:
    """Сохраняет диаграмму Graphviz в файл формата PNG."""
    dot_bin = shutil.which("dot")
    if dot_bin:
        _render_via_local_dot(dot_bin, dot_source, output_path)
    else:
        _render_via_kroki(dot_source, output_path)
