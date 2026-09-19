"""命令行入口。

用法::

    python main.py -n 10 -r 10                 # 生成 10 道 10 以内的题目
    python main.py -e Exercises.txt -a Answers.txt   # 批改并生成 Grade.txt

生成模式下会在当前目录写出 ``Exercises.txt`` 与 ``Answers.txt``；
批改模式下会写出 ``Grade.txt``。
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from src.expression import Node
from src.fraction_utils import format_fraction
from src.generator import GenerationError, generate_unique_problems
from src.grading import grade, write_grade_file

EXERCISES_FILE = "Exercises.txt"
ANSWERS_FILE = "Answers.txt"
GRADE_FILE = "Grade.txt"


def write_exercises(problems: List[Node], path: str = EXERCISES_FILE) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for problem in problems:
            handle.write(f"{problem.to_string()} =\n")


def write_answers(problems: List[Node], path: str = ANSWERS_FILE) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for problem in problems:
            handle.write(f"{format_fraction(problem.evaluate())}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Myapp",
        description="小学四则运算题目生成 / 批改程序",
    )
    parser.add_argument("-n", type=int, help="生成题目的个数")
    parser.add_argument(
        "-r", type=int,
        help="题目中数值的范围（0 <= 数值 < r，且真分数分母 < r）",
    )
    parser.add_argument("-e", metavar="<exercisefile>.txt", help="题目文件（批改模式）")
    parser.add_argument("-a", metavar="<answerfile>.txt", help="答案文件（批改模式）")
    return parser


def run_generate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.r is None:
        parser.error("生成模式必须提供 -r 参数，例如：Myapp.exe -n 10 -r 10（使用 -h 查看帮助）")
    if args.n is None:
        parser.error("生成模式必须提供 -n 参数，例如：Myapp.exe -n 10 -r 10（使用 -h 查看帮助）")
    if args.n <= 0:
        parser.error("-n 必须为正整数")
    if args.r <= 0:
        parser.error("-r 必须为正整数")

    try:
        problems = generate_unique_problems(args.n, args.r)
    except GenerationError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    write_exercises(problems)
    write_answers(problems)
    print(f"已生成 {len(problems)} 道题目：")
    print(f"  题目文件：{os.path.abspath(EXERCISES_FILE)}")
    print(f"  答案文件：{os.path.abspath(ANSWERS_FILE)}")
    return 0


def run_grade(exercise_path: str, answer_path: str) -> int:
    for path in (exercise_path, answer_path):
        if not os.path.isfile(path):
            print(f"错误：找不到文件 {path}", file=sys.stderr)
            return 1
    correct, wrong = grade(exercise_path, answer_path)
    output = write_grade_file(correct, wrong)
    print(f"批改完成，结果已写入：{output}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.e or args.a:
        if not (args.e and args.a):
            parser.error("批改模式必须同时提供 -e <exercisefile>.txt 和 -a <answerfile>.txt")
        return run_grade(args.e, args.a)
    return run_generate(args, parser)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
