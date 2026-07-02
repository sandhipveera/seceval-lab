#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# ModelAudit (Promptfoo) runner. Scans every model in /models + /models/clean,
# times each scan, and emits SARIF to /artifacts/modelaudit.sarif plus a JSON
# convenience copy at /artifacts/modelaudit.json (per-file rows the normalizer
# reads). Tool errors are captured per file, never fatal.
#
# ModelAudit is invoked via its CLI: `modelaudit scan <path> --format sarif`.
# We run once per file so timing is attributable per variant, merge the SARIF
# runs into one document, and keep each file's raw result in the JSON sidecar.
# ---------------------------------------------------------------------------
import json
import time
import subprocess
import pathlib

SARIF_OUT = pathlib.Path("/artifacts/modelaudit.sarif")
JSON_OUT = pathlib.Path("/artifacts/modelaudit.json")


def _peak_ram_kb() -> int:
    """Peak resident memory of this scan process (+ its children), in KB.
    Uses getrusage(ru_maxrss) — race-free, unlike sampling `docker stats`. On
    Linux ru_maxrss is already in KB; children cover the modelaudit CLI subprocess."""
    import resource
    return max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)


def tool_version() -> str:
    try:
        from importlib.metadata import version
        return version("modelaudit")
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
    """Run `modelaudit scan <path> --format sarif`. ModelAudit exits non-zero
    when issues are found, so parse stdout regardless of return code."""
    result = {"sarif": None, "error": None, "returncode": None}
    try:
        proc = subprocess.run(
            ["modelaudit", "scan", str(path), "--format", "sarif"],
            capture_output=True, text=True, timeout=120,
        )
        result["returncode"] = proc.returncode
        stdout = proc.stdout.strip()
        try:
            result["sarif"] = json.loads(stdout) if stdout else None
        except json.JSONDecodeError:
            result["error"] = "non-json stdout"
            result["sarif"] = None
            result["stdout"] = proc.stdout[:4000]
            result["stderr"] = proc.stderr[:2000]
    except Exception as exc:  # noqa: BLE001
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def _sarif_result_count(sarif) -> int:
    if not isinstance(sarif, dict):
        return 0
    total = 0
    for run in sarif.get("runs", []) or []:
        total += len(run.get("results", []) or [])
    return total


def main() -> int:
    SARIF_OUT.parent.mkdir(parents=True, exist_ok=True)
    ver = tool_version()
    print("[modelaudit] version=%s" % ver)

    entries = []
    merged_runs = []
    for variant, path in iter_model_files():
        t0 = time.perf_counter()
        res = scan_one(path)
        elapsed = round(time.perf_counter() - t0, 6)
        n = _sarif_result_count(res["sarif"])
        flagged = n > 0
        if isinstance(res["sarif"], dict):
            merged_runs.extend(res["sarif"].get("runs", []) or [])
        entries.append({
            "variant": variant,
            "path": str(path),
            "bytes": path.stat().st_size,
            "flagged": flagged,
            "result_count": n,
            "scan_seconds": elapsed,
            "result": res,
        })
        print("[modelaudit]   %-18s flagged=%-5s results=%d %.4fs %s"
              % (variant, flagged, n, elapsed,
                 "ERROR:" + res["error"] if res["error"] else ""))

    # Merged SARIF document (one runs[] array across all files).
    merged_sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": merged_runs or [{
            "tool": {"driver": {"name": "ModelAudit", "version": ver}},
            "results": [],
        }],
    }
    SARIF_OUT.write_text(json.dumps(merged_sarif, indent=2, default=str))

    out = {"scanner": "modelaudit", "scanner_version": ver, "entries": entries}
    out["peak_ram_kb"] = _peak_ram_kb()
    print("[modelaudit] peak RSS = %.1f MB" % (out["peak_ram_kb"] / 1024.0))
    JSON_OUT.write_text(json.dumps(out, indent=2, default=str))
    print("[modelaudit] wrote %s and %s (%d entries)"
          % (SARIF_OUT, JSON_OUT, len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
