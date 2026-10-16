import unittest
from ollama_ru_bench.sandbox import extract_code, validate_code, run_code

class TestSandbox(unittest.TestCase):
    def test_extract(self):
        self.assertIn("def f", extract_code("```python\ndef f():\n    pass\n```"))
    def test_validate_import(self):
        ok, _ = validate_code("import os\n")
        self.assertFalse(ok)
    def test_validate_banned(self):
        ok, _ = validate_code("open('x')\n")
        self.assertFalse(ok)
    def test_run_good(self):
        code = "def top_words(text, n):\n    import re, collections\n    words=re.findall(r'[A-Za-zА-Яа-яЁё]+', text.lower())\n    c=collections.Counter(words)\n    return sorted(c.items(), key=lambda x:(-x[1], x[0]))[:n]\n"
        ok, msg = run_code(code)
        self.assertTrue(ok, msg)

if __name__ == "__main__":
    unittest.main()
