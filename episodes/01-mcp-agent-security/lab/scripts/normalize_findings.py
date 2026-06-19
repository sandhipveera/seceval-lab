#!/usr/bin/env python3
"""Merge each scanner's raw output into one comparable CSV: tool, finding, severity, caught.
Claude Code wires the per-scanner parsers; this defines the shared schema the scorecard reads."""
import csv, sys, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "artifacts" / "findings.csv"
OUT.parent.mkdir(exist_ok=True)
HEADER = ["scanner", "target_tool", "finding", "severity", "caught_poison", "false_positive", "scan_seconds"]
# [TODO] Claude Code: parse mcp-scan JSON, golf-scanner output, gateway logs into rows.
rows = []  # list of dicts matching HEADER
with OUT.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADER); w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {OUT} ({len(rows)} rows) — implement parsers per scanner")
