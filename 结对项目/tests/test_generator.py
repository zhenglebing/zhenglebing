import unittest
from fractions import Fraction

from src.expression import ADD, DIV, MUL, SUB
from src.generator import ExpressionGenerator, generate_unique_problems


def check_node(test_case, node):
    """递归检查一棵表达式树是否满足全部约束。"""
    if node.is_leaf:
        return node.value
    left_value = check_node(test_case, node.left)
    right_value = check_node(test_case, node.right)
    test_case.assertGreaterEqual(left_value, 0)
    test_case.assertGreaterEqual(right_value, 0)
    if node.op == SUB:
        test_case.assertGreaterEqual(left_value, right_value, "减法不能产生负数")
        return left_value - right_value
    if node.op == DIV:
        test_case.assertGreater(right_value, 0, "除数不能为 0")
        result = left_value / right_value
        test_case.assertGreater(result, 0)
        test_case.assertLess(result, 1, "除法结果必须是真分数")
        return result
    if node.op == ADD:
        return left_value + right_value
    test_case.assertEqual(node.op, MUL)
    return left_value * right_value


class GeneratorTest(unittest.TestCase):
    def test_constraints_hold(self):
        for seed in range(20):
            problems = generate_unique_problems(50, 12, seed=seed)
            for problem in problems:
                check_node(self, problem)
                self.assertLessEqual(problem.operator_count(), 3)
                self.assertGreaterEqual(problem.operator_count(), 1)

    def test_no_duplicates(self):
        problems = generate_unique_problems(200, 15, seed=42)
        keys = [problem.canonical() for problem in problems]
        self.assertEqual(len(keys), len(set(keys)))

    def test_values_within_range(self):
        r = 10
        generator = ExpressionGenerator(r)
        for _ in range(200):
            node = generator.generate()
            for leaf in self._leaves(node):
                self.assertGreaterEqual(leaf.value, 0)
                self.assertLess(leaf.value, r)

    @staticmethod
    def _leaves(node):
        if node.is_leaf:
            return [node]
        return GeneratorTest._leaves(node.left) + GeneratorTest._leaves(node.right)

    def test_deterministic_with_seed(self):
        self.assertEqual(
            [p.to_string() for p in generate_unique_problems(10, 10, seed=7)],
            [p.to_string() for p in generate_unique_problems(10, 10, seed=7)],
        )


if __name__ == "__main__":
    unittest.main()
