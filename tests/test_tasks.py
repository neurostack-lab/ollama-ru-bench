import unittest
from ollama_ru_bench.tasks import check_math, check_format

class TestTasks(unittest.TestCase):
    def test_math(self):
        self.assertTrue(check_math("answer 28"))
        self.assertFalse(check_math("answer 27"))
    def test_format(self):
        self.assertTrue(check_format("- one two\n- three four\n- five six"))
        self.assertFalse(check_format("- one two\n- three four"))

if __name__ == "__main__":
    unittest.main()
