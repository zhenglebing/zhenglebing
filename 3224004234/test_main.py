import os
import sys
import tempfile
import unittest
from unittest import mock

from main import read_file, normalize, ngram_counter, cosine_similarity, main


class TestPaperCheck(unittest.TestCase):
    # 1 完全相同文本
    def test_identical_text(self):
        score = cosine_similarity("今天是星期天", "今天是星期天")
        self.assertAlmostEqual(score, 1.0)

    # 2 略有改动
    def test_slight_change(self):
        s1 = "今天天气很好"
        s2 = "今天天气非常好"
        score = cosine_similarity(s1, s2)
        self.assertTrue(0 < score < 1)

    # 3 原文空文本
    def test_empty_original(self):
        score = cosine_similarity("", "任意文本")
        self.assertEqual(score, 0.0)

    # 4 抄袭文本为空
    def test_empty_copy(self):
        score = cosine_similarity("任意文本", "")
        self.assertEqual(score, 0.0)

    # 5 完全不同文本
    def test_diff_text(self):
        score = cosine_similarity("苹果", "香蕉")
        self.assertEqual(score, 0.0)

    # 6 纯标点符号
    def test_punct_only(self):
        score = cosine_similarity("！，。？", "!!!")
        self.assertEqual(score, 0.0)

    # 7 大小写英文
    def test_upper_lower(self):
        score = cosine_similarity("Hello", "hello")
        self.assertAlmostEqual(score, 1.0)

    # 8 极短文本
    def test_short_text(self):
        score = cosine_similarity("a", "a")
        self.assertAlmostEqual(score, 1.0)

    # 9 读取不存在文件
    def test_file_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            read_file("notexist.txt")

    # 10 非法n值
    def test_invalid_n(self):
        with self.assertRaises(ValueError):
            ngram_counter("abc", 0)

    # 11 格式化空格换行干扰
    def test_whitespace(self):
        s1 = "今天 天气 晴！"
        s2 = "今天天气晴"
        score = cosine_similarity(s1, s2)
        self.assertAlmostEqual(score, 1.0)

    # 12 长文本集成测试
    def test_long_text_sample(self):
        original_text = read_file("samples/orig.txt")
        copied_text = read_file("samples/orig_0.8_add.txt")
        score = cosine_similarity(original_text, copied_text, n=2)
        self.assertGreater(score, 0.7)
        self.assertLess(score, 0.99)


    # 13 正常读取存在的文件
    def test_read_file_success(self):
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("测试内容")
            self.assertEqual(read_file(path), "测试内容")
        finally:
            os.remove(path)

    # 14 文本预处理：去标点、去空格、英文小写
    def test_normalize(self):
        self.assertEqual(normalize("Hello, 世界！ 123"), "hello世界123")

    # 15 命令行参数不足时只打印用法，不抛异常
    def test_main_missing_args(self):
        with mock.patch.object(sys, "argv", ["main.py"]):
            main()

    # 16 命令行正常运行，结果写入文件且格式为两位小数
    def test_main_normal_run(self):
        fd, orig = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        fd, copy = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        fd, out = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(orig, "w", encoding="utf-8") as f:
                f.write("今天是星期天，天气晴")
            with open(copy, "w", encoding="utf-8") as f:
                f.write("今天是星期天，天气晴")
            with mock.patch.object(sys, "argv", ["main.py", orig, copy, out]):
                main()
            with open(out, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "1.00")
        finally:
            for p in (orig, copy, out):
                os.remove(p)

    # 17 输入文件不存在时输出0.00，程序不崩溃
    def test_main_file_not_exist(self):
        fd, out = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with mock.patch.object(
                sys, "argv", ["main.py", "no_a.txt", "no_b.txt", out]
            ):
                main()
            with open(out, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "0.00")
        finally:
            os.remove(out)


if __name__ == '__main__':
    unittest.main()
