"""对比“随机生成后拒绝重试”的朴素算法与“按合法运算符构造”的优化算法。

运行::

    py tools/benchmark.py

用于博客中的效能分析章节，给出可复现的耗时对比。
"""

from __future__ import annotations

import random
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.expression import ADD, DIV, MUL, SUB, Node  # noqa: E402
from src.generator import generate_unique_problems  # noqa: E402


def random_value(rng: random.Random, r: int) -> Fraction:
    if r <= 1:
        return Fraction(0)
    if r < 3 or rng.random() < 0.5:
        return Fraction(rng.randint(0, r - 1))
    denominator = rng.randint(2, r - 1)
    return Fraction(rng.randint(1, denominator - 1), denominator)


def build_random(rng: random.Random, r: int, operator_count: int) -> Node:
    """不做合法性判断，随机拼出一棵表达式树。"""
    if operator_count <= 0:
        return Node.leaf(random_value(rng, r))
    left_count = rng.randint(0, operator_count - 1)
    right_count = operator_count - 1 - left_count
    left = build_random(rng, r, left_count)
    right = build_random(rng, r, right_count)
    op = rng.choice([ADD, SUB, MUL, DIV])
    return Node(op=op, left=left, right=right)


def is_valid(node: Node) -> Optional[Fraction]:
    """校验整棵树，非法时返回 None。"""
    if node.is_leaf:
        return node.value
    left_value = is_valid(node.left)
    right_value = is_valid(node.right)
    if left_value is None or right_value is None:
        return None
    if node.op == SUB:
        if left_value < right_value:
            return None
        return left_value - right_value
    if node.op == DIV:
        if right_value <= 0 or not (0 < left_value < right_value):
            return None
        return left_value / right_value
    if node.op == ADD:
        return left_value + right_value
    return left_value * right_value


def generate_naive(n: int, r: int, seed: int) -> List[Node]:
    rng = random.Random(seed)
    problems: List[Node] = []
    seen = set()
    while len(problems) < n:
        operator_count = rng.randint(1, 3)
        node = build_random(rng, r, operator_count)
        if is_valid(node) is None:
            continue
        key = node.canonical()
        if key in seen:
            continue
        seen.add(key)
        problems.append(node)
    return problems


def timeit(func, rounds: int = 5) -> float:
    start = time.perf_counter()
    for _ in range(rounds):
        func()
    return (time.perf_counter() - start) / rounds


def main() -> None:
    n, r, seed = 10000, 50, 1
    rounds = 5
    naive = timeit(lambda: generate_naive(n, r, seed), rounds)
    optimized = timeit(lambda: generate_unique_problems(n, r, seed=seed), rounds)
    print(f"n={n}, r={r}（平均 {rounds} 轮）")
    print(f"朴素拒绝采样：{naive:.4f} s")
    print(f"优化构造算法：{optimized:.4f} s")
    if optimized > 0:
        print(f"提升倍数：{naive / optimized:.2f}x")


if __name__ == "__main__":
    main()
