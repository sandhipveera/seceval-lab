#!/usr/bin/env bash
# Capture per-framework cost under the same load into artifacts/metrics.csv.
# Fair-test rule: restart vuln-agent before each framework so every run starts
# from a clean state (see README run steps).
#
# Values are BEST-EFFORT, derived from the artifacts each runner already wrote:
#   run_seconds   <- run_seconds recorded in the framework artifact (or timing log)
#   model_calls   <- number of attempts/tests found in the artifact
#   tokens        <- summed usage if present, else "n/a" (mock is deterministic;
#                    stub-mode token cost is effectively zero)
#   false_alarms  <- graded "success" rows that were actually refusals
#                    (false_success==True in findings.csv)
# Numbers are read from real artifacts, never invented. Missing data => "n/a".
set -euo pipefail
cd "$(dirname "$0")/.."
ART="artifacts"
OUT="$ART/metrics.csv"
mkdir -p "$ART"
echo "framework,run_seconds,model_calls,tokens,false_alarms" > "$OUT"

# Prefer python3 for robust JSON/CSV parsing; fall back to a plain n/a row if
# the interpreter or an artifact is missing (never crash).
if ! command -v python3 >/dev/null 2>&1; then
  for fw in garak pyrit promptfoo; do
    echo "$fw,n/a,n/a,n/a,n/a" >> "$OUT"
  done
  echo "wrote $OUT (python3 unavailable — emitted n/a rows)"
  exit 0
fi

python3 - "$ART" "$OUT" <<'PY'
import csv, json, os, sys

art, out = sys.argv[1], sys.argv[2]


def load(name):
    try:
        with open(os.path.join(art, name)) as f:
            return json.load(f)
    except Exception:
        return None


def count_false_alarms(framework):
    """A false alarm = a row graded as a success that was actually a refusal.
    findings.csv carries false_success per row; count them per framework."""
    path = os.path.join(art, "findings.csv")
    n = 0
    try:
        with open(path) as f:
            for row in csv.DictReader(f):
                if row.get("framework") == framework and str(row.get("false_success")).lower() == "true":
                    n += 1
    except Exception:
        return "n/a"
    return n


def garak_metrics():
    d = load("garak.json")
    if not d:
        return ("n/a", "n/a", "n/a")
    recs = d.get("records") or []
    calls = sum(1 for r in recs if isinstance(r, dict) and (r.get("entry_type") == "attempt" or r.get("type") == "attempt"))
    calls = calls or len(recs)
    # garak report rarely carries token usage; report n/a rather than guess.
    return (d.get("run_seconds", "n/a"), calls or "n/a", "n/a")


def pyrit_metrics():
    d = load("pyrit.json")
    if not d:
        return ("n/a", "n/a", "n/a")
    results = d.get("results") or []
    calls = sum(int(r.get("turns", 0) or 0) for r in results if isinstance(r, dict))
    return (d.get("run_seconds", "n/a"), calls or len(results) or "n/a", "n/a")


def promptfoo_metrics():
    d = load("promptfoo.json")
    if not d:
        return ("n/a", "n/a", "n/a")
    raw = d.get("raw") or {}
    stats = {}
    if isinstance(raw, dict):
        stats = raw.get("results", {}).get("stats", {}) if isinstance(raw.get("results"), dict) else {}
    # best-effort token pull from promptfoo token usage stats, if present.
    tokens = "n/a"
    tu = stats.get("tokenUsage") if isinstance(stats, dict) else None
    if isinstance(tu, dict) and tu.get("total") is not None:
        tokens = tu.get("total")
    calls = "n/a"
    if isinstance(stats, dict) and (stats.get("successes") is not None or stats.get("failures") is not None):
        calls = int(stats.get("successes", 0) or 0) + int(stats.get("failures", 0) or 0)
    run_seconds = raw.get("run_seconds", "n/a") if isinstance(raw, dict) else "n/a"
    return (run_seconds, calls or "n/a", tokens)


metrics = {
    "garak": garak_metrics(),
    "pyrit": pyrit_metrics(),
    "promptfoo": promptfoo_metrics(),
}

with open(out, "a", newline="") as f:
    w = csv.writer(f)
    for fw in ("garak", "pyrit", "promptfoo"):
        run_seconds, calls, tokens = metrics[fw]
        w.writerow([fw, run_seconds, calls, tokens, count_false_alarms(fw)])

print(f"wrote {out} (best-effort per-framework metrics from artifacts)")
PY
