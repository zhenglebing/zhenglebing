"""算术表达式的数据结构、求值、字符串化、规范化与解析。

表达式用二叉树表示：叶子节点保存一个 ``Fraction`` 数值，内部节点保存
运算符与左右子树。这样做既方便逐步检查“中间结果不能为负、除法结果必须
是真分数”等约束，也方便生成唯一的字符串表示。
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Tuple

from .fraction_utils import format_fraction, parse_fraction

ADD = "+"
SUB = "-"
MUL = "×"
DIV = "÷"

PRECEDENCE = {ADD: 1, SUB: 1, MUL: 2, DIV: 2}

_OPERATOR_CHARS = {"+", "-", "−", "×", "÷", "*", "/", "(", ")"}


class Node:
    """表达式二叉树节点。"""

    __slots__ = ("value", "op", "left", "right")

    def __init__(self, value: Optional[Fraction] = None, op: Optional[str] = None,
                 left: Optional["Node"] = None, right: Optional["Node"] = None) -> None:
        self.value = value
        self.op = op
        self.left = left
        self.right = right

    @property
    def is_leaf(self) -> bool:
        return self.op is None

    @staticmethod
    def leaf(value) -> "Node":
        return Node(value=Fraction(value))

    def evaluate(self) -> Fraction:
        """递归求值。"""
        if self.is_leaf:
            return self.value
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()
        if self.op == ADD:
            return left_value + right_value
        if self.op == SUB:
            return left_value - right_value
        if self.op == MUL:
            return left_value * right_value
        if self.op == DIV:
            return left_value / right_value
        raise ValueError(f"未知运算符: {self.op!r}")

    def to_string(self) -> str:
        """转换成题目要求的字符串，必要时补括号以保持原有计算顺序。"""
        text, _ = self._render()
        return text

    def _render(self) -> Tuple[str, int]:
        if self.is_leaf:
            return format_fraction(self.value), 3
        precedence = PRECEDENCE[self.op]
        left_text, left_precedence = self.left._render()
        right_text, right_precedence = self.right._render()
        if left_precedence < precedence:
            left_text = f"({left_text})"
        if right_precedence < precedence or (
            right_precedence == precedence and self.op in (SUB, DIV)
        ):
            right_text = f"({right_text})"
        return f"{left_text} {self.op} {right_text}", precedence

    def canonical(self):
        """返回用于判重的规范形式。

        题目规定只能交换 ``+`` 和 ``×`` 左右的表达式，因此对这两种运算符
        的左右子树按规范形式排序；``-`` 和 ``÷`` 的左右顺序有意义，保持
        不变。规范形式相同的两道题即为重复题目。
        """
        if self.is_leaf:
            return ("num", str(self.value))
        left_key = self.left.canonical()
        right_key = self.right.canonical()
        if self.op in (ADD, MUL) and right_key < left_key:
            left_key, right_key = right_key, left_key
        return (self.op, left_key, right_key)

    def operator_count(self) -> int:
        if self.is_leaf:
            return 0
        return 1 + self.left.operator_count() + self.right.operator_count()


class Parser:
    """简单的递归下降解析器，支持四则运算、括号以及真分数。"""

    def __init__(self, text: str) -> None:
        self.tokens: List[str] = self._tokenize(text)
        self.pos = 0

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        tokens: List[str] = []
        index = 0
        length = len(text)
        while index < length:
            char = text[index]
            if char.isspace():
                index += 1
            elif char.isdigit():
                end = index
                while end < length and (text[end].isdigit() or text[end] in "'/"):
                    end += 1
                tokens.append(text[index:end])
                index = end
            elif char in _OPERATOR_CHARS:
                if char == "−":
                    char = SUB
                elif char == "*":
                    char = MUL
                elif char == "/":
                    char = DIV
                tokens.append(char)
                index += 1
            else:
                raise ValueError(f"非法字符: {char!r}")
        return tokens

    def parse(self) -> Node:
        node = self._parse_expression()
        if self.pos != len(self.tokens):
            raise ValueError("表达式存在多余字符")
        return node

    def _peek(self) -> Optional[str]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _next(self) -> Optional[str]:
        token = self._peek()
        self.pos += 1
        return token

    def _parse_expression(self) -> Node:
        node = self._parse_term()
        while self._peek() in (ADD, SUB):
            op = self._next()
            right = self._parse_term()
            node = Node(op=op, left=node, right=right)
        return node

    def _parse_term(self) -> Node:
        node = self._parse_factor()
        while self._peek() in (MUL, DIV):
            op = self._next()
            right = self._parse_factor()
            node = Node(op=op, left=node, right=right)
        return node

    def _parse_factor(self) -> Node:
        token = self._peek()
        if token is None:
            raise ValueError("表达式不完整")
        if token == "(":
            self._next()
            node = self._parse_expression()
            if self._peek() != ")":
                raise ValueError("括号不匹配")
            self._next()
            return node
        self._next()
        return Node.leaf(parse_fraction(token))


def parse_expression(text: str) -> Node:
    """解析一行题目字符串，自动忽略结尾的等号。"""
    text = text.strip()
    if text.endswith("="):
        text = text[:-1]
    return Parser(text).parse()
