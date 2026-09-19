import os
import tempfile
import unittest

from src.grading import format_grade, grade, write_grade_file


class GradingTest(unittest.TestCase):
    def _write(self, directory, name, lines):
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return path

    def test_grade_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            exercise = self._write(directory, "Exercises.txt", [
                "1/6 + 1/8 =",
                "2 + 3 × 4 =",
                "5 - 8 =",
            ])
            answer = self._write(directory, "Answers.txt", [
                "7/24",
                "14",
                "3",
            ])
            correct, wrong = grade(exercise, answer)
            self.assertEqual(correct, [1, 2])
            self.assertEqual(wrong, [3])

    def test_mixed_fraction_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            exercise = self._write(directory, "e.txt", ["2'3/8 + 1/8 ="])
            answer = self._write(directory, "a.txt", ["2'1/2"])
            correct, wrong = grade(exercise, answer)
            self.assertEqual(correct, [1])
            self.assertEqual(wrong, [])

    def test_missing_answer_is_wrong(self):
        with tempfile.TemporaryDirectory() as directory:
            exercise = self._write(directory, "e.txt", ["1 + 1 =", "2 + 2 ="])
            answer = self._write(directory, "a.txt", ["2"])
            correct, wrong = grade(exercise, answer)
            self.assertEqual(correct, [1])
            self.assertEqual(wrong, [2])

    def test_format_and_write(self):
        self.assertEqual(
            format_grade([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]),
            "Correct: 5 (1, 3, 5, 7, 9)\nWrong: 5 (2, 4, 6, 8, 10)\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "Grade.txt")
            write_grade_file([1], [2], path)
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("Correct: 1 (1)", content)
            self.assertIn("Wrong: 1 (2)", content)


if __name__ == "__main__":
    unittest.main()
