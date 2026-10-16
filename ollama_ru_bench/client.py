import json
import os
import time
import urllib.error
import urllib.request


class OllamaError(Exception):
    pass


def _headers(host):
    headers = {"Content-Type": "application/json"}
    if "ollama.com" in host and os.environ.get("OLLAMA_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["OLLAMA_API_KEY"]
    return headers


def chat_stream(host, model, messages, think=False):
    url = host.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": True, "think": think}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(host))
    start = time.perf_counter()  # before the request: TTFT includes network and queueing
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise OllamaError(f"HTTP {e.code}: {body}") from e
    except Exception as e:
        raise OllamaError(str(e)) from e

    first_token_time = None
    text_parts = []
    eval_count = 0
    prompt_eval_count = 0
    for raw in resp:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "error" in obj:
            raise OllamaError(obj["error"])
        msg = obj.get("message", {})
        content = msg.get("content", "")
        if content:
            if first_token_time is None:
                first_token_time = time.perf_counter()
            text_parts.append(content)
        if obj.get("done"):
            eval_count = obj.get("eval_count", eval_count)
            prompt_eval_count = obj.get("prompt_eval_count", prompt_eval_count)
    elapsed = time.perf_counter() - start
    ttft = (first_token_time - start) if first_token_time is not None else None
    text = "".join(text_parts)
    tok_s = (eval_count / elapsed) if elapsed > 0 and eval_count else 0.0
    return {
        "text": text,
        "ttft": ttft,
        "elapsed": elapsed,
        "eval_count": eval_count,
        "prompt_eval_count": prompt_eval_count,
        "tok_s": tok_s,
    }
