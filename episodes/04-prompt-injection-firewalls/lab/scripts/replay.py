#!/usr/bin/env python3
# =============================================================================
# EPISODE 04 — battery replay engine (runs INSIDE the labnet 'runner' container)
# -----------------------------------------------------------------------------
# Replays the injection battery (or the benign false-positive set) through the
# vuln-app while a given firewall guards the door, and records what each guard
# caught vs. what walked past (canary fired). Uses stdlib only (no pip in the
# runner). Talks to the app over the internal labnet; nothing leaves the host.
#
#   python replay.py <firewall-name> attacks   -> artifacts/<name>.json
#   python replay.py <firewall-name> benign    -> artifacts/false_positives.json (merged)
#
# The app's /chat response is ground truth:
#   action == "blocked"      -> the firewall caught it            (caught=True)
#   action == "exfiltrated"  -> it walked past; canary fired      (canary_fired=True)
#   action == "answered"     -> no exfil instruction acted on     (neither)
# =============================================================================
import json
import os
import sys
import time
import urllib.request

APP_URL = os.environ.get("APP_URL", "http://ep04-vuln-app:8000").rstrip("/")
ART = os.environ.get("ARTIFACTS_DIR", "/artifacts")
BATTERY_DIR = os.environ.get("BATTERY_DIR", "/scripts/battery")


def _post(path, payload, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        APP_URL + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body, (time.time() - t0) * 1000.0


def _wait_health(tries=40):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(APP_URL + "/health", timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    raise SystemExit(f"app not healthy at {APP_URL}")


def _verdict_of(resp):
    """Pull the guard's label/score from the app response (first non-n/a verdict)."""
    for v in resp.get("verdicts", []) or []:
        if v.get("label") not in (None, "n/a"):
            return v
    return (resp.get("verdicts") or [{}])[0] if resp.get("verdicts") else {}


def run_attacks(name):
    battery = json.load(open(os.path.join(BATTERY_DIR, "battery.json")))
    results = []
    for item in battery:
        # Clean slate so ingested docs from a prior L3 case don't bleed over.
        _post("/reset", {})
        if item.get("delivery") == "ingest+chat":
            _post("/ingest", {"id": item["id"], "doc": item["doc"]})
            resp, ms = _post("/chat", {"message": item["trigger"], "use_docs": True})
        else:
            resp, ms = _post("/chat", {"message": item["text"]})
        v = _verdict_of(resp)
        action = resp.get("action")
        results.append({
            "id": item["id"], "level": item["level"], "variant": item["variant"],
            "action": action,
            "label": v.get("label", "n/a"), "score": v.get("score", 0.0),
            "caught": action == "blocked",
            "canary_fired": action == "exfiltrated",
            "latency_ms": round(ms, 1),
            "canary_leaked": bool(v.get("canary_leaked") or v.get("canary_token_detected")),
        })
    out = {"firewall": name, "results": results}
    path = os.path.join(ART, f"{name}.json")
    json.dump(out, open(path, "w"), indent=2)
    caught = sum(r["caught"] for r in results)
    fired = sum(r["canary_fired"] for r in results)
    print(f"[{name}] attacks: {len(results)} | caught {caught} | canary_fired {fired} -> {path}")


def run_benign(name):
    benign = json.load(open(os.path.join(BATTERY_DIR, "benign_fp.json")))
    over = []
    for item in benign:
        _post("/reset", {})
        resp, ms = _post("/chat", {"message": item["text"]})
        if resp.get("action") == "blocked":  # blocking a benign prompt = false positive
            v = _verdict_of(resp)
            over.append({"id": item["id"], "label": v.get("label"), "score": v.get("score")})
    path = os.path.join(ART, "false_positives.json")
    try:
        agg = json.load(open(path))
    except Exception:
        agg = {}
    agg[name] = {
        "tested": len(benign),
        "over_blocked": over,
        "false_positive_rate": round(len(over) / max(1, len(benign)), 3),
    }
    json.dump(agg, open(path, "w"), indent=2)
    print(f"[{name}] benign: {len(benign)} tested | over-blocked {len(over)} -> {path}")


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: replay.py <firewall-name> <attacks|benign>")
    name, mode = sys.argv[1], sys.argv[2]
    os.makedirs(ART, exist_ok=True)
    _wait_health()
    if mode == "attacks":
        run_attacks(name)
    elif mode == "benign":
        run_benign(name)
    else:
        raise SystemExit("mode must be 'attacks' or 'benign'")


if __name__ == "__main__":
    main()
