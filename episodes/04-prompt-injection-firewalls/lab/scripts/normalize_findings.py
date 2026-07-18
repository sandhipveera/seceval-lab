#!/usr/bin/env python3
"""Merge each firewall's raw artifact into one comparable CSV.

Same vulnerable app, same injection battery, same benign set — only the firewall
in front changes (fair-test rule). Parsers are DEFENSIVE: a missing/unreadable
artifact yields a `note` row instead of crashing, so the scorecard shows the gap.

findings.csv columns:
  firewall, attack_level, attack_variant, verdict, caught, false_positive,
  canary_fired, latency_ms
"""
import csv
import glob
import json
import os
import pathlib

ART = pathlib.Path(__file__).resolve().parent.parent / "artifacts"
OUT = ART / "findings.csv"
HEADER = ["firewall", "attack_level", "attack_variant", "verdict", "caught",
          "false_positive", "canary_fired", "latency_ms"]

KNOWN = ["none", "prompt-guard-2", "vigil", "llm-guard", "rebuff"]


def _load(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


def _row(fw, level="", variant="", verdict="", caught="", fp="", canary="",
         latency="", note_variant=None):
    return {"firewall": fw, "attack_level": level,
            "attack_variant": note_variant if note_variant is not None else variant,
            "verdict": verdict, "caught": caught, "false_positive": fp,
            "canary_fired": canary, "latency_ms": latency}


def main():
    rows = []

    # 1) Per-firewall attack artifacts (<name>.json).
    seen = set()
    for path in sorted(glob.glob(str(ART / "*.json"))):
        name = os.path.basename(path)[:-5]
        if name in ("findings", "false_positives", "metrics"):
            continue
        data = _load(path)
        if not data or "results" not in data:
            rows.append(_row(name, note_variant="[missing/unreadable artifact]"))
            continue
        # INTEGRITY GUARD: if every verdict is "error", the guard never answered —
        # the app fails OPEN, so each attack looks like a miss. That is a BROKEN
        # CONTAINER, not a finding. Record it as NOT EVALUATED instead of emitting
        # rows that read "caught 0/N". (Ep.04: this is exactly how vigil failed.)
        results = data.get("results", []) or []
        if results and all(str(r.get("label", "")).lower() == "error" for r in results):
            rows.append(_row(name, level="[NOT EVALUATED]",
                             note_variant="guard never started — all verdicts 'error' "
                                          "(app failed open; not a miss)"))
            seen.add(name)
            continue

        seen.add(name)
        for r in results:
            rows.append(_row(
                name,
                level=r.get("level", ""),
                variant=r.get("variant", ""),
                verdict=r.get("label", ""),
                caught=bool(r.get("caught")),
                canary=bool(r.get("canary_fired")),
                latency=r.get("latency_ms", ""),
            ))

    # 2) Note any known firewall whose attack artifact never showed up.
    for name in KNOWN:
        if name not in seen and not os.path.exists(ART / f"{name}.json"):
            rows.append(_row(name, level="[run pending]"))

    # 3) False-positive summary (benign-but-scary set).
    fp = _load(ART / "false_positives.json") or {}
    for name, info in fp.items():
        rate = info.get("false_positive_rate", "")
        over = len(info.get("over_blocked", []))
        tested = info.get("tested", "")
        rows.append(_row(name, level="benign-fp", variant=f"{over}/{tested} over-blocked",
                         fp=rate))

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
