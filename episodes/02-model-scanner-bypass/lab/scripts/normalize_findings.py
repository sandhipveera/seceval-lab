#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# normalize_findings.py — merge all four scanners' raw artifacts into one
# comparable CSV the scorecard reads.
#
# Output: artifacts/findings.csv with EXACT columns:
#   scanner, scanner_version, model_variant, finding, severity, caught,
#   false_positive, scan_seconds
#
# One row per (scanner x variant) and per (scanner x clean model).
#   caught          = 1 if the scanner flagged a MALICIOUS variant, else 0.
#                     (Not meaningful for clean models -> left 0.)
#   false_positive  = 1 if the scanner flagged a CLEAN model, else 0.
#
# Each scanner's entrypoint writes a normalized {"entries": [...]} shape with a
# per-file `flagged` boolean and `scan_seconds`, so this parser is uniform; it
# still degrades gracefully if a file is missing or a tool errored on a file.
# ---------------------------------------------------------------------------
import csv
import json
import pathlib

ART = pathlib.Path(__file__).resolve().parent.parent / "artifacts"
OUT = ART / "findings.csv"
HEADER = ["scanner", "scanner_version", "model_variant", "finding",
          "severity", "caught", "false_positive", "scan_seconds"]

# Raw artifact file per scanner. ModelAudit uses its JSON sidecar (same shape).
SOURCES = {
    "picklescan": "picklescan.json",
    "modelscan": "modelscan.json",
    "modelaudit": "modelaudit.json",
    "fickling": "fickling.json",
}


def load(name: str):
    path = ART / SOURCES[name]
    if not path.exists():
        print("[normalize] MISSING %s (did run_%s.sh run?)" % (path, name))
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        print("[normalize] could not parse %s: %s" % (path, exc))
        return None


def _finding_text(entry: dict) -> str:
    """Best-effort short human description of what (if anything) was found."""
    res = entry.get("result") or {}
    # picklescan globals
    globs = res.get("globals")
    if globs:
        return ";".join(
            "%s.%s" % (g.get("module"), g.get("name")) for g in globs)[:200]
    # modelscan issues
    report = res.get("report")
    if isinstance(report, dict):
        issues = report.get("issues")
        if isinstance(issues, list) and issues:
            descs = [str(i.get("description") or i.get("severity") or "issue")
                     for i in issues]
            return ";".join(descs)[:200]
    # modelaudit sarif
    sarif = res.get("sarif")
    if isinstance(sarif, dict):
        msgs = []
        for run in sarif.get("runs", []) or []:
            for r in run.get("results", []) or []:
                msgs.append(str((r.get("message") or {}).get("text") or "result"))
        if msgs:
            return ";".join(msgs)[:200]
    # fickling
    if isinstance(res.get("api"), dict) and res["api"].get("detail"):
        if entry.get("flagged"):
            return str(res["api"].get("severity") or "unsafe")[:200]
    if entry.get("error"):
        return "scan-error: %s" % entry["error"]
    if res.get("error"):
        return "scan-error: %s" % res["error"]
    return "flagged" if entry.get("flagged") else "clean"


def _severity(entry: dict) -> str:
    res = entry.get("result") or {}
    report = res.get("report")
    if isinstance(report, dict):
        summ = report.get("summary") or {}
        sev = summ.get("total_issues_by_severity") or {}
        if isinstance(sev, dict):
            for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                if sev.get(level):
                    return level
    sarif = res.get("sarif")
    if isinstance(sarif, dict):
        for run in sarif.get("runs", []) or []:
            for r in run.get("results", []) or []:
                lvl = r.get("level")
                if lvl:
                    return str(lvl)
    if isinstance(res.get("api"), dict) and res["api"].get("severity"):
        return str(res["api"]["severity"])
    return "high" if entry.get("flagged") else "none"


def rows_for(name: str, data: dict):
    rows = []
    ver = data.get("scanner_version", "unknown")
    for entry in data.get("entries", []) or []:
        variant = entry.get("variant", "?")
        is_clean = variant.startswith("clean:")
        flagged = bool(entry.get("flagged"))
        rows.append({
            "scanner": name,
            "scanner_version": ver,
            "model_variant": variant,
            "finding": _finding_text(entry),
            "severity": _severity(entry),
            "caught": 0 if is_clean else (1 if flagged else 0),
            "false_positive": 1 if (is_clean and flagged) else 0,
            "scan_seconds": entry.get("scan_seconds", ""),
        })
    return rows


def main() -> int:
    ART.mkdir(exist_ok=True)
    all_rows = []
    for name in SOURCES:
        data = load(name)
        if data is None:
            continue
        all_rows.extend(rows_for(name, data))

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)

    caught = sum(r["caught"] for r in all_rows)
    fps = sum(r["false_positive"] for r in all_rows)
    print("[normalize] wrote %s (%d rows, %d caught, %d false-positives)"
          % (OUT, len(all_rows), caught, fps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
