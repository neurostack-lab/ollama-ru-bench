import ast
import resource
import subprocess
import sys
import tempfile

ALLOWED_IMPORTS = {"re", "collections", "math", "itertools", "functools", "typing", "string", "unicodedata"}
BANNED_NAMES = {"open", "exec", "eval", "__import__"}


def extract_code(text):
    import re
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S | re.I)
    if m:
        return m.group(1).strip()
    # fallback: first def/class block
    lines = text.splitlines()
    out = []
    started = False
    for line in lines:
        if line.startswith("def ") or line.startswith("class "):
            started = True
        if started:
            out.append(line)
    return "\n".join(out).strip()


def validate_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"syntax error: {e}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name.split(".")[0] for a in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for n in names:
                if n not in ALLOWED_IMPORTS:
                    return False, f"disallowed import: {n}"
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in BANNED_NAMES:
                return False, f"banned call: {name}"
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            return False, f"banned name: {node.id}"
    return True, "ok"


UNIT_TESTS = r'''
import sys
sys.path.insert(0, {dir!r})
from solution import top_words

cases = [
    ("Hello world hello", 2, [("hello", 2), ("world", 1)]),
    ("a b a c b a", 2, [("a", 3), ("b", 2)]),
    ("Привет мир привет", 2, [("привет", 2), ("мир", 1)]),
    ("", 3, []),
    ("one two three", 5, [("one",1),("three",1),("two",1)]),
]
for text, n, expected in cases:
    got = top_words(text, n)
    if got != expected:
        print("FAIL", repr(text), got, expected)
        sys.exit(1)
print("PASS")
'''


def run_code(code):
    ok, msg = validate_code(code)
    if not ok:
        return False, msg
    with tempfile.TemporaryDirectory() as d:
        with open(d + "/solution.py", "w", encoding="utf-8") as f:
            f.write(code + "\n")
        test_code = UNIT_TESTS.format(dir=d)
        with open(d + "/test_runner.py", "w", encoding="utf-8") as f:
            f.write(test_code)

        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))

        try:
            proc = subprocess.run(
                [sys.executable, "-I", d + "/test_runner.py"],
                capture_output=True,
                text=True,
                timeout=15,
                preexec_fn=limits,
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout).strip()[:500]
        return True, "pass"
