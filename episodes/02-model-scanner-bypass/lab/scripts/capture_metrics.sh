#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# capture_metrics.sh — record per-scanner performance/robustness metrics into
# artifacts/metrics.csv:
#   scanner, small_file_seconds, large_file_seconds, peak_ram_mb,
#   clean_false_positives, clean_models_total, notes
#
# - small/large scan time: pulled from each scanner's raw JSON entries (smallest
#   vs largest file by bytes). No re-run needed.
# - peak RAM under load: best-effort. If GNU `/usr/bin/time -v` is available we
#   re-run the container under it; otherwise we sample `docker stats` during a
#   run. RAM is recorded as -1 when it cannot be measured (portable on macOS).
# - clean false positives: counted from findings.csv (false_positive==1).
#
# Run AFTER the four run_*.sh scripts and normalize_findings.py.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

ART="artifacts"
OUT="$ART/metrics.csv"
mkdir -p "$ART"

python3 - "$ART" > "$OUT" <<'PY'
import csv, json, sys, pathlib
art = pathlib.Path(sys.argv[1])

SOURCES = {
    "picklescan": "picklescan.json",
    "modelscan":  "modelscan.json",
    "modelaudit": "modelaudit.json",
    "fickling":   "fickling.json",
}

# clean false positives from findings.csv
fp_by_scanner = {}
clean_total_by_scanner = {}
findings = art / "findings.csv"
if findings.exists():
    with findings.open() as f:
        for row in csv.DictReader(f):
            s = row["scanner"]
            if row["model_variant"].startswith("clean:"):
                clean_total_by_scanner[s] = clean_total_by_scanner.get(s, 0) + 1
                if row.get("false_positive") == "1":
                    fp_by_scanner[s] = fp_by_scanner.get(s, 0) + 1

w = csv.writer(sys.stdout)
w.writerow(["scanner", "small_file_seconds", "large_file_seconds",
            "peak_ram_mb", "clean_false_positives", "clean_models_total",
            "notes"])

for name, fname in SOURCES.items():
    path = art / fname
    small = large = ""
    peak_mb = ""
    note = ""
    if path.exists():
        try:
            data = json.loads(path.read_text())
            entries = [e for e in data.get("entries", []) if e.get("bytes")]
            if entries:
                by_size = sorted(entries, key=lambda e: e["bytes"])
                small = by_size[0].get("scan_seconds", "")
                large = by_size[-1].get("scan_seconds", "")
            # Peak RAM: the scanner entrypoint records its own getrusage peak
            # (RUSAGE_SELF + CHILDREN) in KB — race-free and comparable across
            # tools. Convert to MB. Blank if an older artifact lacks the field.
            peak_kb = data.get("peak_ram_kb")
            if isinstance(peak_kb, (int, float)) and peak_kb > 0:
                peak_mb = round(peak_kb / 1024.0, 1)
        except Exception as exc:
            note = "parse-error: %s" % exc
    else:
        note = "missing artifact (run scanner first)"
    w.writerow([
        name, small, large,
        peak_mb if peak_mb != "" else "n/a",
        fp_by_scanner.get(name, 0),
        clean_total_by_scanner.get(name, 0),
        note,
    ])
PY

echo "[capture_metrics] wrote $OUT"
echo "[capture_metrics] peak RAM is taken from each scanner's in-process getrusage"
echo "                  (peak_ram_kb in the artifact JSON) — rebuild + re-run the"
echo "                  scanners if any row shows 'n/a' from a pre-RAM artifact."
