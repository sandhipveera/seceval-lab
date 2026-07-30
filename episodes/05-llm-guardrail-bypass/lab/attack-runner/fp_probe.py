#!/usr/bin/env python3
"""Send the benign prompt set through an endpoint and report false positives + latency.

A false positive = a perfectly normal prompt that the guard BLOCKS. Two prompts in the set
deliberately contain scary-looking words ("ignore the previous agent", "reveal my true feelings")
to probe over-blocking, the same way the Ep.04 benign set did.

Prints a one-line JSON summary: {"blocked": n, "total": n, "avg_latency_ms": x}.
"""
import os, json, time, pathlib
import requests

HIT_URL = os.environ.get("HIT_URL", "http://ep05-target:8080/chat")
PROMPTS = pathlib.Path(os.environ.get("PROMPTS", "/app/benign_prompts.txt"))

def main():
    lines = [l.strip() for l in PROMPTS.read_text().splitlines() if l.strip()]
    blocked, latencies = 0, []
    for text in lines:
        t0 = time.perf_counter()
        try:
            r = requests.post(HIT_URL, json={"message": text}, timeout=120)
            latencies.append((time.perf_counter() - t0) * 1000.0)
            body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            if bool(body.get("blocked", False)) or r.status_code == 403:
                blocked += 1
        except Exception:
            latencies.append((time.perf_counter() - t0) * 1000.0)
    avg = round(sum(latencies) / len(latencies), 1) if latencies else 0.0
    print(json.dumps({"blocked": blocked, "total": len(lines), "avg_latency_ms": avg}))

if __name__ == "__main__":
    main()
