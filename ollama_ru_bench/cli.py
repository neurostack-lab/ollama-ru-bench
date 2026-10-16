import argparse
import json
import os
import statistics

from .client import chat_stream, OllamaError
from .tasks import (ru_rewrite_prompt, code_prompt, math_prompt, format_prompt,
                    check_math, check_format, judge_prompt, NEWS)
from .sandbox import extract_code, run_code
from .report import render_table


def run_one(host, model, judge=None):
    res = {"model": model, "tok_s": [], "ttft": [], "ru_score": None,
           "code_pass": 0, "math": False, "format": False}
    # ru_rewrite
    try:
        r = chat_stream(host, model, [{"role": "user", "content": ru_rewrite_prompt()}])
        res["tok_s"].append(r["tok_s"]); 
        if r["ttft"] is not None: res["ttft"].append(r["ttft"])
        if judge:
            jr = chat_stream(host, judge, [{"role": "user", "content": judge_prompt(r["text"])}])
            try:
                j = json.loads(jr["text"].strip())
                res["ru_score"] = j.get("score")
            except Exception:
                res["ru_score"] = None
    except OllamaError as e:
        print(f"[{model}] ru_rewrite error: {e}")
    # code
    try:
        r = chat_stream(host, model, [{"role": "user", "content": code_prompt()}])
        res["tok_s"].append(r["tok_s"])
        if r["ttft"] is not None: res["ttft"].append(r["ttft"])
        code = extract_code(r["text"])
        ok, _ = run_code(code)
        res["code_pass"] = 3 if ok else 0
    except OllamaError as e:
        print(f"[{model}] code error: {e}")
    # math
    try:
        r = chat_stream(host, model, [{"role": "user", "content": math_prompt()}])
        res["tok_s"].append(r["tok_s"])
        if r["ttft"] is not None: res["ttft"].append(r["ttft"])
        res["math"] = check_math(r["text"])
    except OllamaError as e:
        print(f"[{model}] math error: {e}")
    # format
    try:
        r = chat_stream(host, model, [{"role": "user", "content": format_prompt()}])
        res["tok_s"].append(r["tok_s"])
        if r["ttft"] is not None: res["ttft"].append(r["ttft"])
        res["format"] = check_format(r["text"])
    except OllamaError as e:
        print(f"[{model}] format error: {e}")

    res["tok_s"] = statistics.median(res["tok_s"]) if res["tok_s"] else 0.0
    res["ttft"] = statistics.median(res["ttft"]) if res["ttft"] else None
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("models", nargs="+")
    p.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--json", dest="json_out")
    p.add_argument("--judge")
    args = p.parse_args()

    results = {}
    for m in args.models:
        results[m] = run_one(args.host, m, args.judge)

    print(render_table(args.models, results))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
