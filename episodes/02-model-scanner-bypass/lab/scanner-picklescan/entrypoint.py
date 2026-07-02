#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# picklescan runner. Iterates every model file under /models (variants) and
# /models/clean (benign set), times each scan, and records a row per file into
# /artifacts/picklescan.json. Handles tool errors / mis-parses gracefully so a
# scanner that crashes on the broken_archive still yields a recorded row.
#
# picklescan is a blocklist scanner: it walks pickle opcodes and flags GLOBAL
# imports that resolve to a known-dangerous (module, name). This runner shells
# to nothing dangerous — it only imports the library and calls its scanner API.
# ---------------------------------------------------------------------------
import io
import json
import time
import contextlib
import pathlib

ARTIFACT = pathlib.Path("/artifacts/picklescan.json")


def _peak_ram_kb() -> int:
    """Peak resident memory of this scan process (+ its children), in KB.
    Uses getrusage(ru_maxrss) — race-free, unlike sampling `docker stats`. On
    Linux ru_maxrss is already in KB; children cover any subprocess-based tools."""
    import resource
    return max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)


def tool_version() -> str:
    try:
        from importlib.metadata import version
        return version("picklescan")
    except Exception as exc:  # noqa: BLE001
        return "unknown (%s)" % exc


def iter_model_files():
    """Yield (variant_label, path) for every file under test."""
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
    """Run picklescan's file scanner on one path, capturing its result and any
    error. Returns a normalized dict; never raises."""
    result = {"globals": [], "raw": None, "error": None}
    try:
        from picklescan import scanner as ps
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            res = ps.scan_file_path(str(path))
        # ScanResult exposes .globals (list) and .scan_err / .infected_files etc.
        globals_found = []
        for g in getattr(res, "globals", []) or []:
            globals_found.append({
                "module": getattr(g, "module", None),
                "name": getattr(g, "name", None),
                "safety": str(getattr(g, "safety", "")),
            })
        result["globals"] = globals_found
        result["raw"] = {
            "scanned_files": getattr(res, "scanned_files", None),
            "issues_count": getattr(res, "issues_count", None),
            "infected_files": getattr(res, "infected_files", None),
            "scan_err": getattr(res, "scan_err", None),
            "log": buf.getvalue()[:4000],
        }
    except Exception as exc:  # noqa: BLE001
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def main() -> int:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ver = tool_version()
    print("[picklescan] version=%s" % ver)

    entries = []
    for variant, path in iter_model_files():
        t0 = time.perf_counter()
        res = scan_one(path)
        elapsed = round(time.perf_counter() - t0, 6)
        flagged = bool(res["globals"]) or bool(
            (res["raw"] or {}).get("issues_count"))
        entries.append({
            "variant": variant,
            "path": str(path),
            "bytes": path.stat().st_size,
            "flagged": flagged,
            "scan_seconds": elapsed,
            "result": res,
        })
        print("[picklescan]   %-18s flagged=%-5s %.4fs %s"
              % (variant, flagged, elapsed,
                 "ERROR:" + res["error"] if res["error"] else ""))

    out = {"scanner": "picklescan", "scanner_version": ver, "entries": entries}
    out["peak_ram_kb"] = _peak_ram_kb()
    print("[picklescan] peak RSS = %.1f MB" % (out["peak_ram_kb"] / 1024.0))
    ARTIFACT.write_text(json.dumps(out, indent=2, default=str))
    print("[picklescan] wrote %s (%d entries)" % (ARTIFACT, len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
