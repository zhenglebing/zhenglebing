# 小学四则运算题目生成 / 批改程序（结对项目）

一个纯 Python 标准库实现的命令行程序，可以批量生成不重复的小学四则运算题目、
自动计算答案，并对已有题目与答案文件进行批改统计。

## 环境要求

- Python 3.8 及以上（本项目在 Python 3.14 上开发与测试）
- 无第三方运行时依赖

## 运行说明

在 `结对项目` 目录下执行：

### 1. 生成题目

```bash
# 生成 10 道 10 以内的题目（结果写入当前目录 Exercises.txt 与 Answers.txt）
python main.py -n 10 -r 10
```

- `-n`：生成题目的个数；
- `-r`：题目中数值（自然数、真分数及其分母）的范围，要求 `0 <= 数值 < r`；
- `-r`、`-n` 在生成模式下都必须提供，否则程序会报错并打印帮助信息。

生成的 `Exercises.txt` 每行一道题，`Answers.txt` 每行对应一道题的答案。

### 2. 批改

```bash
python main.py -e Exercises.txt -a Answers.txt
```

批改结果写入当前目录的 `Grade.txt`，格式如下：

```
Correct: 5 (1, 3, 5, 7, 9)
Wrong: 5 (2, 4, 6, 8, 10)
```

### 3. 查看帮助

```bash
python main.py -h
```

## 功能与需求对应

| 需求 | 实现说明 |
| --- | --- |
| `-n` 控制题目数量 | `main.py` / `argparse` |
| `-r` 控制数值范围 | 自然数与真分数分子分母均小于 `r` |
| 计算过程不出现负数 | 只有 `e1 >= e2` 时才允许生成 `e1 - e2` |
| 除法结果必须是真分数 | 只有 `0 < e1/e2 < 1` 时才允许生成 `e1 ÷ e2` |
| 每题运算符不超过 3 个 | `ExpressionGenerator.max_operators = 3` |
| 题目不重复 | `Node.canonical()` 生成规范形式判重 |
| 输出 `Exercises.txt` / `Answers.txt` | `main.py` |
| 支持一万道题目 | 实测 10000 道约 0.7 秒 |
| 批改输出 `Grade.txt` | `src/grading.py` |
| 真分数格式 | `3/5`、`2'3/8`，见 `src/fraction_utils.py` |

## 目录结构

```
结对项目/
├── main.py                  # 命令行入口
├── src/
│   ├── fraction_utils.py    # 真分数的格式化 / 解析
│   ├── expression.py        # 表达式树、求值、字符串化、判重、解析器
│   ├── generator.py         # 题目生成器
│   └── grading.py           # 批改与 Grade.txt 输出
├── tests/                   # 单元测试（标准库 unittest）
├── tools/
│   └── profile_report.py    # 性能分析脚本
└── docs/
    └── performance_analysis.svg   # 性能分析图
```

## 运行测试

```bash
python -m unittest discover -s tests -v
```

共 22 个测试用例，覆盖分数格式化与解析、表达式求值与优先级、判重规范形式、
生成约束、批改统计等。

## 性能分析

```bash
python tools/profile_report.py
```

脚本会打印耗时最高的函数，并生成 `docs/performance_analysis.svg`
（浏览器打开后可直接截图）。如安装了 matplotlib 还会生成 PNG。
