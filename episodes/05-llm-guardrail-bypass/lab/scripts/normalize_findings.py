#!/usr/bin/env python3
"""Merge each guardrail's raw output into one comparable CSV.

Reads artifacts/{baseline,nemo,guardrails}.json (whichever exist) and emits artifacts/findings.csv
with columns: guardrail, variant, verdict, canary_leaked, caught, false_positive, latency_ms.

Integrity guard (Ep.04 lesson): if EVERY variant for a guardrail errored (the proxy never
answered — http==0 or an error field), we do NOT record it as "caught 0/3". A guard that never
ran is not a guard that missed. Those rows are marked verdict=error / caught=[NOT EVALUATED], and
a warning is printed so the write-up reports it honestly.
"""
import csv, json, pathlib

ART = pathlib.Path(__file__).resolve().parent.parent / "artifacts"
OUT = ART / "findings.csv"
HEADER = ["guardrail", "variant", "verdict", "canary_leaked", "caught", "false_positive", "latency_ms"]

def load_fp():
    """Per-guard false-positive counts from metrics.csv, if present."""
    fp = {}
    m = ART / "metrics.csv"
    if m.exists():
        with m.open() as f:
            for row in csv.DictReader(f):
                g = row.get("guardrail", "")
                if g and row.get("false_positives", "") != "":
                    fp[g] = row["false_positives"]
    return fp

def main():
    fp_by_guard = load_fp()
    rows, warnings = [], []
    for name in ("baseline", "nemo", "guardrails"):
        path = ART / f"{name}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        results = data.get("results", [])
        errored = [r for r in results if r.get("http", 0) == 0 or r.get("error")]
        all_errored = bool(results) and len(errored) == len(results)
        for r in results:
            if all_errored:
                rows.append({"guardrail": name, "variant": r.get("variant", ""),
                             "verdict": "error", "canary_leaked": "", "caught": "[NOT EVALUATED]",
                             "false_positive": "", "latency_ms": r.get("latency_ms", "")})
            else:
                rows.append({"guardrail": name, "variant": r.get("variant", ""),
                             "verdict": r.get("verdict", ""),
                             "canary_leaked": r.get("canary_leaked", ""),
                             "caught": r.get("caught", ""),
                             "false_positive": fp_by_guard.get(name, ""),
                             "latency_ms": r.get("latency_ms", "")})
        if all_errored:
            warnings.append(f"{name}: all variants errored -> reported as NOT EVALUATED")

    ART.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for wmsg in warnings:
        print("  WARNING:", wmsg)

if __name__ == "__main__":
    main()
