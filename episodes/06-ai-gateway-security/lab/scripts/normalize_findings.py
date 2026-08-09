#!/usr/bin/env python3
"""Merge every artifacts/raw_*.json (one per gateway x guardrails-state, plus the no-gateway
baseline) into two comparable CSVs:

  artifacts/findings.csv -- columns: gateway,version,guardrails,scenario,attack_class,blocked,
    canary_leaked,canary_sink_hit,false_positive,detection_source,notes
  artifacts/posture.csv  -- columns: gateway,version,check,result,evidence

Integrity guard (the Ep.05 lesson this whole build is named after): a scenario whose runner row
came back with blocked="" (run.py's score functions leave it blank when the request errored, see
`is_errored()` in runner/run.py) is written through AS blank here, never coerced to True/False and
never counted as a catch. An errored request is not evaluated, full stop -- see the WARNING this
script prints if a raw file's results are entirely blank.
"""
import csv
import glob
import json
import pathlib

ART = pathlib.Path(__file__).resolve().parent.parent / "artifacts"
FINDINGS_OUT = ART / "findings.csv"
POSTURE_OUT = ART / "posture.csv"

FINDINGS_HEADER = ["gateway", "version", "guardrails", "scenario", "attack_class", "blocked",
                   "canary_leaked", "canary_sink_hit", "false_positive", "detection_source", "notes"]
POSTURE_HEADER = ["gateway", "version", "check", "result", "evidence"]


def main():
    findings_rows = []
    posture_rows = []
    warnings = []

    raw_files = sorted(glob.glob(str(ART / "raw_*.json")))
    if not raw_files:
        print(f"no artifacts/raw_*.json found in {ART} -- run scripts/run_gateway.sh first")
        return

    for path in raw_files:
        data = json.loads(pathlib.Path(path).read_text())
        gateway = data.get("gateway", "")
        version = data.get("version", "")
        guardrails = data.get("guardrails", "")
        results = data.get("results", [])

        # Clean sets (c*) have no blocked/missed verdict by design -- they report a false-positive
        # COUNT. Excluding every c* scenario, not just c1, keeps the integrity guard below measuring
        # what it is meant to measure: whether the scored attack scenarios all errored.
        def _is_clean_set(r):
            return str(r.get("scenario", "")).startswith("c")

        blank_count = sum(1 for r in results if r.get("blocked", "") == "" and not _is_clean_set(r))
        scored_count = sum(1 for r in results if not _is_clean_set(r))
        if scored_count and blank_count == scored_count:
            warnings.append(f"{path}: every scored scenario errored (transport/upstream failure) "
                             f"-- {gateway}/{guardrails} produced NO usable findings, not a clean "
                             f"sweep. Fix the run before trusting any number for this row.")

        for r in results:
            findings_rows.append({
                "gateway": gateway, "version": version, "guardrails": guardrails,
                "scenario": r.get("scenario", ""), "attack_class": r.get("attack_class", ""),
                "blocked": r.get("blocked", ""), "canary_leaked": r.get("canary_leaked", ""),
                "canary_sink_hit": r.get("canary_sink_hit", ""),
                "false_positive": r.get("false_positive", ""),
                "detection_source": r.get("detection_source", ""),
                "notes": r.get("notes", ""),
            })

        for p in data.get("posture", []):
            posture_rows.append({
                "gateway": gateway, "version": version,
                "check": p.get("check", ""), "result": p.get("result", ""),
                "evidence": p.get("evidence", ""),
            })

    ART.mkdir(exist_ok=True)
    with FINDINGS_OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FINDINGS_HEADER)
        w.writeheader()
        w.writerows(findings_rows)
    with POSTURE_OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=POSTURE_HEADER)
        w.writeheader()
        w.writerows(posture_rows)

    print(f"wrote {FINDINGS_OUT} ({len(findings_rows)} rows)")
    print(f"wrote {POSTURE_OUT} ({len(posture_rows)} rows)")
    for w in warnings:
        print("  WARNING:", w)


if __name__ == "__main__":
    main()
