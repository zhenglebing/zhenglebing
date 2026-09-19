"""真分数的格式化与解析工具。

本项目内部统一使用 ``fractions.Fraction`` 表示数值，只有在读写文件时
才转换为题目要求的字符串形式：

* 自然数直接输出，例如 ``3``；
* 真分数输出为 ``分子/分母``，例如 ``3/5``；
* 假分数（带分数）输出为 ``整数'分子/分母``，例如 ``2'3/8``。
"""

from __future__ import annotations

from fractions import Fraction


def format_fraction(value: Fraction) -> str:
    """把 ``Fraction`` 转换为题目要求的字符串。"""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    if value > 1:
        whole = value.numerator // value.denominator
        remainder = value.numerator % value.denominator
        return f"{whole}'{remainder}/{value.denominator}"
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(text: str) -> Fraction:
    """把 ``3``、``3/5``、``2'3/8`` 这类字符串解析为 ``Fraction``。"""
    text = text.strip()
    if not text:
        raise ValueError("空字符串无法解析为分数")
    if "'" in text:
        whole_text, fraction_text = text.split("'", 1)
        numerator_text, denominator_text = fraction_text.split("/", 1)
        whole = int(whole_text)
        numerator = int(numerator_text)
        denominator = int(denominator_text)
        return Fraction(whole * denominator + numerator, denominator)
    if "/" in text:
        numerator_text, denominator_text = text.split("/", 1)
        return Fraction(int(numerator_text), int(denominator_text))
    return Fraction(int(text))
