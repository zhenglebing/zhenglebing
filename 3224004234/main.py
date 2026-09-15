import sys
import re
from collections import Counter
import math

# 预编译正则表达式：只保留中文、英文字母、数字，提前编译避免重复开销
_NORMALIZE_PATTERN = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9]")


def read_file(path: str) -> str:
    """读取文件，utf-8编码；文件不存在时抛出FileNotFoundError"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在：{path}")


def normalize(text: str) -> str:
    """文本预处理：去除标点、空格、换行，英文转小写"""
    # 去掉所有非文字字符（使用预编译正则）
    text = _NORMALIZE_PATTERN.sub("", text)
    text = text.lower()
    return text


def ngram_counter(text: str, n: int) -> Counter:
    """切分字符n-gram，统计频次；n<=0抛异常"""
    if n <= 0:
        raise ValueError("n必须大于0")
    if len(text) < n:
        return Counter()
    # 二元组是默认场景，用zip一次配对，避免循环切片产生大量临时字符串，速度更快
    if n == 2:
        return Counter(zip(text, text[1:]))
    counter = Counter()
    for i in range(len(text) - n + 1):
        gram = text[i:i+n]
        counter[gram] += 1
    return counter


def cosine_similarity(text_a: str, text_b: str, n: int = 2) -> float:
    """余弦相似度计算，返回0~1浮点数"""
    # 先做文本预处理，去除标点、空格并统一大小写
    clean_a = normalize(text_a)
    clean_b = normalize(text_b)
    # 任一文本清洗后为空，直接返回0，避免向量模长为0导致除零
    if not clean_a or not clean_b:
        return 0.0
    # 文本长度小于n时，把n缩小到能切出至少一个片段，保证极短文本可比较
    n = min(n, len(clean_a), len(clean_b))

    vec1 = ngram_counter(clean_a, n)
    vec2 = ngram_counter(clean_b, n)
    # 合并所有key
    all_keys = set(vec1.keys()) | set(vec2.keys())
    dot = 0
    mag1 = 0
    mag2 = 0
    for k in all_keys:
        v1 = vec1.get(k, 0)
        v2 = vec2.get(k, 0)
        dot += v1 * v2
        mag1 += v1 * v1
        mag2 += v2 * v2
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (math.sqrt(mag1) * math.sqrt(mag2))


def main():
    # 命令行参数校验
    if len(sys.argv) != 4:
        print("用法：python main.py <原文路径> <抄袭路径> <输出文件路径>")
        return
    orig_path = sys.argv[1]
    copy_path = sys.argv[2]
    out_path = sys.argv[3]

    # 文件读取失败时不让程序崩溃，输出0.00继续完成评测
    try:
        text1 = read_file(orig_path)
        text2 = read_file(copy_path)
        score = cosine_similarity(text1, text2, n=2)
    except OSError as e:
        print(f"读取文件失败：{e}")
        score = 0.0

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{score:.2f}")
    print(f"相似度：{score:.2f}，结果已写入{out_path}")


if __name__ == "__main__":
    main()
