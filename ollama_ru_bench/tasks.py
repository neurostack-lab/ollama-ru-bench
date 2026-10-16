import re

NEWS = ("Open-weight language models are becoming easier to run locally, "
        "and developers are increasingly testing them for multilingual tasks. "
        "Recent releases focus on efficiency, tool use, and safer deployment. "
        "Benchmarks remain important, but real-world usage often reveals "
        "different strengths and weaknesses.")


def ru_rewrite_prompt():
    return (
        "Rewrite the following English news paragraph as a Russian Telegram post. "
        "Output a headline and exactly 3 sentences. Facts only, no hype.\n\n"
        + NEWS
    )


def code_prompt():
    return (
        "Write a Python function top_words(text, n) that returns the n most frequent words. "
        "Words contain letters only (Latin and Cyrillic), case-insensitive. "
        "Ties broken alphabetically. Return list of (word, count) tuples. "
        "Put code in a fenced python block."
    )


def math_prompt():
    return "What is the sum of the digits of 2026 squared? Answer with the final number."


def format_prompt():
    return ("List exactly 3 benefits of drinking water. "
            "Each line starts with '- ', at most 8 words, no emoji.")


def check_math(text):
    nums = re.findall(r"\d+", text)
    return bool(nums) and int(nums[-1]) == 28


def check_format(text):
    lines = [l for l in text.strip().splitlines() if l.strip()]
    if len(lines) != 3:
        return False
    for line in lines:
        if not line.startswith("- "):
            return False
        words = line[2:].split()
        if len(words) > 8 or len(words) == 0:
            return False
        if any(ord(c) > 0x1F000 for c in line):
            return False
    return True


def judge_prompt(answer):
    return (
        "You are a strict reviewer. Return ONLY JSON: "
        '{"score":1-10,"errors":[...]}. '
        "Score factual accuracy and Russian quality of this Telegram post:\n" + answer
    )
