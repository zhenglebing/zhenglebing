"""题目生成器。

生成规则（对应作业需求）：

* 每道题目运算符数量在 1~3 个之间；
* 参与运算的数只能是自然数或真分数，取值范围由 ``-r`` 控制；
* 计算过程中不能出现负数（``e1 - e2`` 要求 ``e1 >= e2``）；
* 除法 ``e1 ÷ e2`` 的结果必须是真分数（``0 < e1/e2 < 1``）；
* 同一次运行生成的题目不能重复（按 ``Node.canonical`` 判重）。
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import List, Optional, Set, Tuple

from .expression import ADD, DIV, MUL, SUB, Node


class GenerationError(Exception):
    """无法在当前参数下生成满足条件的题目。"""


class ExpressionGenerator:
    """按照给定数值范围生成满足全部约束的随机表达式。"""

    def __init__(self, r: int, rng: Optional[random.Random] = None,
                 max_operators: int = 3) -> None:
        if r < 1:
            raise ValueError("数值范围 r 必须为不小于 1 的自然数")
        self.r = r
        self.rng = rng if rng is not None else random.Random()
        self.max_operators = max_operators

    def generate(self, operator_count: Optional[int] = None) -> Node:
        """生成一道题目，失败时自动重试。"""
        if operator_count is None:
            operator_count = self.rng.randint(1, self.max_operators)
        node, _ = self._build(operator_count)
        return node

    def _build(self, operator_count: int) -> Tuple[Node, Fraction]:
        """自底向上构造表达式，同时把子树的数值一起返回，避免重复求值。"""
        if operator_count <= 0:
            value = self._random_value()
            return Node.leaf(value), value
        left_operators = self.rng.randint(0, operator_count - 1)
        right_operators = operator_count - 1 - left_operators
        left, left_value = self._build(left_operators)
        right, right_value = self._build(right_operators)
        op = self._choose_operator(left_value, right_value)
        node = Node(op=op, left=left, right=right)
        return node, self._apply(op, left_value, right_value)

    def _random_value(self) -> Fraction:
        """按相同概率生成自然数或真分数，全部满足 0 <= 数值 < r。"""
        r = self.r
        if r <= 1:
            return Fraction(0)
        if r < 3 or self.rng.random() < 0.5:
            return Fraction(self.rng.randint(0, r - 1))
        denominator = self.rng.randint(2, r - 1)
        numerator = self.rng.randint(1, denominator - 1)
        return Fraction(numerator, denominator)

    def _choose_operator(self, left_value: Fraction, right_value: Fraction) -> str:
        """在保证合法性的前提下随机选择运算符。

        ``+`` 和 ``×`` 永远合法；``-`` 需要 ``e1 >= e2``；``÷`` 需要结果
        是真分数，即 ``0 < e1/e2 < 1``。这样构造出的题目天然满足约束，
        不需要“先生成再拒绝重试”。
        """
        candidates: List[str] = [ADD, MUL]
        if left_value >= right_value:
            candidates.append(SUB)
        if right_value > 0 and 0 < left_value < right_value:
            candidates.append(DIV)
        return self.rng.choice(candidates)

    @staticmethod
    def _apply(op: str, left_value: Fraction, right_value: Fraction) -> Fraction:
        if op == ADD:
            return left_value + right_value
        if op == SUB:
            return left_value - right_value
        if op == MUL:
            return left_value * right_value
        return left_value / right_value


def generate_unique_problems(n: int, r: int, seed: Optional[int] = None,
                             max_operators: int = 3) -> List[Node]:
    """生成 ``n`` 道互不重复的题目。"""
    if n <= 0:
        raise GenerationError("题目数量必须为正整数")
    rng = random.Random(seed)
    generator = ExpressionGenerator(r, rng, max_operators)
    problems: List[Node] = []
    seen: Set = set()
    stale_limit = max(50000, n * 20)
    stale = 0
    while len(problems) < n:
        if stale > stale_limit:
            raise GenerationError(
                f"在当前数值范围 r={r} 内无法生成 {n} 道不重复的题目"
                f"（已生成 {len(problems)} 道），请增大 -r"
            )
        try:
            node = generator.generate()
        except GenerationError:
            stale += 1
            continue
        key = node.canonical()
        if key in seen:
            stale += 1
            continue
        seen.add(key)
        problems.append(node)
        stale = 0
    return problems
