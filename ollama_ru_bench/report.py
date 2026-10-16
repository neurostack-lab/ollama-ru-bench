def render_table(models, results):
    headers = ["Model", "tok/s", "TTFT", "RU", "Code", "Math", "Format"]
    rows = []
    for m in models:
        r = results[m]
        ru = r.get("ru_score")
        ru_s = "-" if ru is None else f"{ru}/10"
        code = f"{r.get('code_pass',0)}/3" if "code_pass" in r else "-"
        math = "✓" if r.get("math") else "✗"
        fmt = "✓" if r.get("format") else "✗"
        ttft = r.get("ttft")
        ttft_s = "-" if ttft is None else f"{ttft:.2f}s"
        rows.append([m, f"{r.get('tok_s',0):.1f}", ttft_s, ru_s, code, math, fmt])
    widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    def fmt_row(row):
        return " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers)))
    out = [fmt_row(headers), "-+-".join("-" * w for w in widths)]
    for row in rows:
        out.append(fmt_row(row))
    return "\n".join(out)
