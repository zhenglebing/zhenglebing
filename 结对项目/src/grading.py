"""批改模块：读取题目文件与答案文件，统计对错并写出 Grade.txt。"""

from __future__ import annotations

import os
from typing import List, Tuple

from .expression import parse_expression
from .fraction_utils import parse_fraction


def read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return [line.strip() for line in handle if line.strip()]


def grade(exercise_path: str, answer_path: str) -> Tuple[List[int], List[int]]:
    """逐题比较标准答案与文件中的答案，返回 (正确编号, 错误编号)。"""
    exercises = read_lines(exercise_path)
    answers = read_lines(answer_path)

    correct: List[int] = []
    wrong: List[int] = []
    for index in range(len(exercises)):
        number = index + 1
        try:
            expected = parse_expression(exercises[index]).evaluate()
            if index >= len(answers):
                raise ValueError("缺少对应答案")
            actual = parse_fraction(answers[index])
        except (ValueError, ZeroDivisionError):
            wrong.append(number)
            continue
        if expected == actual:
            correct.append(number)
        else:
            wrong.append(number)
    return correct, wrong


def format_grade(correct: List[int], wrong: List[int]) -> str:
    def join(numbers: List[int]) -> str:
        return ", ".join(str(number) for number in numbers)

    return (f"Correct: {len(correct)} ({join(correct)})\n"
            f"Wrong: {len(wrong)} ({join(wrong)})\n")


def write_grade_file(correct: List[int], wrong: List[int], path: str = "Grade.txt") -> str:
    content = format_grade(correct, wrong)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return os.path.abspath(path)
