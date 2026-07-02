#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# ModelScan (Protect AI) runner. Times a per-file scan for every model in
# /models + /models/clean and records the tool's native JSON report per file
# into /artifacts/modelscan.json. Tool errors / mis-parses are captured, not
# fatal, so every file still yields a row.
#
# ModelScan invokes its CLI (`modelscan -p <path> -r json`) per file and parses
# the emitted JSON report. It classifies issues by severity, which we preserve.
# ---------------------------------------------------------------------------
import json
import os
import time
import tempfile
import subprocess
import pathlib

ARTIFACT = pathlib.Path("/artifacts/modelscan.json")


def _peak_ram_kb() -> int:
    """Peak resident memory of this scan process (+ its children), in KB.
    Uses getrusage(ru_maxrss) — race-free, unlike sampling `docker stats`. On
    Linux ru_maxrss is already in KB; children cover the modelscan CLI subprocess."""
    import resource
    return max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)


def tool_version() -> str:
    try:
        from importlib.metadata import version
        return version("modelscan")
    except Exception as exc:  # noqa: BLE001
        return "unknown (%s)" % exc


def iter_model_files():
    models = pathlib.Path("/models")
    for p in sorted(models.glob("*")):
        if p.is_file() and p.name not in ("manifest.csv", "canary_payload.py"):
            yield p.stem, p
    clean = models / "clean"
    if clean.is_dir():
        for p in sorted(clean.glob("*")):
            if p.is_file():
                yield "clean:" + p.name, p


def scan_one(path: pathlib.Path) -> dict:
    """Run `modelscan -p <path> -r json -o <file>` and parse the JSON REPORT
    FILE. ModelScan 0.8.x writes progress/log lines to stdout, so stdout is not
    valid JSON — we direct the machine-readable report to a file with -o and read
    that. modelscan exits non-zero when it finds issues, so a non-zero return is
    NOT fatal; we only record an error row if no parseable report is produced."""
    result = {"report": None, "error": None, "returncode": None}
    with tempfile.TemporaryDirectory() as td:
        outfile = os.path.join(td, "report.json")
        try:
            proc = subprocess.run(
                ["modelscan", "-p", str(path), "-r", "json", "-o", outfile],
                capture_output=True, text=True, timeout=120,
            )
            result["returncode"] = proc.returncode
            report_text = ""
            if os.path.exists(outfile):
                with open(outfile) as fh:
                    report_text = fh.read().strip()
            if not report_text:                 # fall back to stdout if no file
                report_text = proc.stdout.strip()
            try:
                result["report"] = json.loads(report_text) if report_text else None
            except json.JSONDecodeError:
                result["error"] = "non-json output"
                result["report"] = {"stdout": proc.stdout[:4000],
                                    "stderr": proc.stderr[:2000]}
        except Exception as exc:  # noqa: BLE001
            result["error"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def _issue_count(report) -> int:
    if not isinstance(report, dict):
        return 0
    # modelscan JSON: {"summary": {"total_issues": N, ...}, "issues": [...]}
    summ = report.get("summary") or {}
    if isinstance(summ, dict) and "total_issues" in summ:
        try:
            return int(summ["total_issues"])
        except (TypeError, ValueError):
            pass
    issues = report.get("issues")
    if isinstance(issues, list):
        return len(issues)
    return 0


def main() -> int:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ver = tool_version()
    print("[modelscan] version=%s" % ver)

    entries = []
    for variant, path in iter_model_files():
        t0 = time.perf_counter()
        res = scan_one(path)
        elapsed = round(time.perf_counter() - t0, 6)
        n = _issue_count(res["report"])
        flagged = n > 0
        entries.append({
            "variant": variant,
            "path": str(path),
            "bytes": path.stat().st_size,
            "flagged": flagged,
            "issue_count": n,
            "scan_seconds": elapsed,
            "result": res,
        })
        print("[modelscan]   %-18s flagged=%-5s issues=%d %.4fs %s"
              % (variant, flagged, n, elapsed,
                 "ERROR:" + res["error"] if res["error"] else ""))

    out = {"scanner": "modelscan", "scanner_version": ver, "entries": entries}
    out["peak_ram_kb"] = _peak_ram_kb()
    print("[modelscan] peak RSS = %.1f MB" % (out["peak_ram_kb"] / 1024.0))
    ARTIFACT.write_text(json.dumps(out, indent=2, default=str))
    print("[modelscan] wrote %s (%d entries)" % (ARTIFACT, len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
