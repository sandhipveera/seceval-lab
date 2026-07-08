#!/usr/bin/env bash
# =============================================================================
# EPISODE 04 — cost/noise metrics per firewall.
# Reads the raw artifacts and writes artifacts/metrics.csv with added latency
# (p50/p95 over the battery calls), the false-positive rate, and whether the
# guard spends an extra inference call. Pure stdlib; run after the battery +
# false-positive tests have produced artifacts.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."   # -> lab/

python3 - <<'PY'
import glob, json, os, statistics, csv, pathlib
ART = pathlib.Path("artifacts")

# What each guard spends beyond baseline (qualitative; verified by design).
INFERENCE = {
    "none": "none",
    "prompt-guard-2": "1 classifier forward-pass (Prompt Guard 2)",
    "llm-guard": "1 classifier forward-pass (fine-tuned PromptInjection model)",
    "vigil": "embedding lookup + pattern match (no generative call)",
    "rebuff": "heuristics + vector lookup (+1 LLM call only if LLM_API_KEY set)",
}

def pct(vals, p):
    if not vals:
        return ""
    vals = sorted(vals)
    k = (len(vals) - 1) * (p / 100.0)
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return round(vals[lo] + (vals[hi] - vals[lo]) * (k - lo), 1)

fp = {}
try:
    fp = json.load(open(ART / "false_positives.json"))
except Exception:
    fp = {}

rows = []
for path in sorted(glob.glob(str(ART / "*.json"))):
    name = os.path.basename(path)[:-5]
    if name in ("findings", "false_positives", "metrics"):
        continue
    try:
        data = json.load(open(path))
    except Exception:
        continue
    lat = [r.get("latency_ms") for r in data.get("results", []) if isinstance(r.get("latency_ms"), (int, float))]
    rows.append({
        "firewall": name,
        "p50_ms": pct(lat, 50),
        "p95_ms": pct(lat, 95),
        "false_positive_rate": fp.get(name, {}).get("false_positive_rate", ""),
        "added_inference": INFERENCE.get(name, "unknown"),
    })

out = ART / "metrics.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["firewall", "p50_ms", "p95_ms", "false_positive_rate", "added_inference"])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {out} ({len(rows)} firewalls)")
PY
