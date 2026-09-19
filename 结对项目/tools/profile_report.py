"""性能分析脚本。

直接运行::

    py tools/profile_report.py

默认对生成 10000 道 50 以内题目进行 cProfile 采样，输出耗时最高的函数，
并生成无需第三方依赖的性能柱状图 ``docs/performance_analysis.svg``
（可直接用浏览器打开并截图）。若安装了 matplotlib，还会额外生成 PNG。
可以通过环境变量 ``N``、``R`` 调整题目数量与数值范围。
"""

from __future__ import annotations

import cProfile
import html
import io
import os
import pstats
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.generator import generate_unique_problems  # noqa: E402


def run_profile(n: int, r: int) -> cProfile.Profile:
    profiler = cProfile.Profile()
    profiler.enable()
    generate_unique_problems(n, r, seed=1)
    profiler.disable()
    profiler.dump_stats(str(PROJECT_ROOT / "profile.stats"))
    return profiler


def print_stats(profiler: cProfile.Profile, top: int = 15) -> None:
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("tottime")
    stats.print_stats(top)
    print(stream.getvalue())


def collect_stats(profiler: cProfile.Profile, top: int = 10) -> List[Tuple[str, float]]:
    stats = pstats.Stats(profiler)
    entries: List[Tuple[str, float]] = []
    for (filename, lineno, funcname), (_cc, _nc, tt, _ct, _callers) in stats.stats.items():
        label = f"{Path(filename).name}:{lineno} {funcname}"
        entries.append((label, tt))
    entries.sort(key=lambda item: item[1], reverse=True)
    return entries[:top]


def plot_svg(entries: List[Tuple[str, float]], output: Path) -> None:
    """不依赖任何第三方库，绘制横向柱状图并保存为 SVG。"""
    width = 980
    row_height = 34
    top_margin = 60
    left_margin = 430
    right_margin = 120
    bar_max_width = width - left_margin - right_margin
    height = top_margin + row_height * len(entries) + 40
    max_time = max((time for _, time in entries), default=1.0) or 1.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="32" text-anchor="middle" '
        'font-family="Microsoft YaHei, SimHei, sans-serif" font-size="20">'
        '生成 10000 道题目时各函数累计耗时 Top 10</text>',
    ]
    for index, (label, time_value) in enumerate(entries):
        y = top_margin + index * row_height
        bar_width = max(1.0, bar_max_width * time_value / max_time)
        parts.append(
            f'<text x="{left_margin - 10}" y="{y + 20}" text-anchor="end" '
            f'font-family="Consolas, monospace" font-size="13">'
            f'{html.escape(label)}</text>'
        )
        parts.append(
            f'<rect x="{left_margin}" y="{y + 4}" width="{bar_width:.1f}" '
            f'height="{row_height - 12}" fill="#4c72b0"/>'
        )
        parts.append(
            f'<text x="{left_margin + bar_width + 6}" y="{y + 20}" '
            f'font-family="Consolas, monospace" font-size="13">'
            f'{time_value:.4f}s</text>'
        )
    parts.append("</svg>")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")
    print(f"性能分析图（SVG）已保存到 {output}")


def plot_mpl(entries: List[Tuple[str, float]], output: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    labels = [label for label, _ in entries][::-1]
    values = [time for _, time in entries][::-1]
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color="#4c72b0")
    plt.xlabel("total time (s)")
    plt.title("生成 10000 道题目时各函数累计耗时 Top 10")
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"性能分析图（PNG）已保存到 {output}")


def main() -> None:
    n = int(os.environ.get("N", "10000"))
    r = int(os.environ.get("R", "50"))
    print(f"开始分析：n={n}, r={r}")
    profiler = run_profile(n, r)
    print_stats(profiler)
    entries = collect_stats(profiler)
    plot_svg(entries, PROJECT_ROOT / "docs" / "performance_analysis.svg")
    plot_mpl(entries, PROJECT_ROOT / "docs" / "performance_analysis.png")


if __name__ == "__main__":
    main()
