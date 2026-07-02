#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# fickling (Trail of Bits) runner. Runs fickling's pickle safety check in
# allowlist mode over every model in /models + /models/clean, times each scan,
# and writes raw JSON per file to /artifacts/fickling.json. Tool errors /
# mis-parses are captured per file, never fatal.
#
# fickling takes an *allowlist* philosophy: it decompiles the pickle to an AST
# and asks "is every operation provably one of a small set of safe things?" —
# anything unproven (imports, calls, reduces) is flagged as likely-unsafe. We
# use the CLI `fickling --check-safety <path>` and also fall back to the Python
# API (fickling.analysis) so we get structured results where available.
# ---------------------------------------------------------------------------
import json
import time
import subprocess
import pathlib

ARTIFACT = pathlib.Path("/artifacts/fickling.json")


def _peak_ram_kb() -> int:
    """Peak resident memory of this scan process (+ its children), in KB.
    Uses getrusage(ru_maxrss) — race-free, unlike sampling `docker stats`. On
    Linux ru_maxrss is already in KB; children cover the fickling CLI subprocess."""
    import resource
    return max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)


def tool_version() -> str:
    try:
        from importlib.metadata import version
        return version("fickling")
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


def _api_check(path: pathlib.Path) -> dict:
    """Use fickling's Python API in allowlist mode. Returns structured safety
    info or an error. fickling's API surface has shifted across releases, so we
    probe defensively and record whatever we can extract."""
    info = {"safe": None, "severity": None, "detail": None, "error": None}
    try:
        from fickling.fickle import Pickled
        with path.open("rb") as fh:
            pickled = Pickled.load(fh)
        # check_safety() returns an analysis result object in recent releases.
        try:
            analysis = pickled.check_safety()
            # Object may expose .severity / .analysis / bool-ish safety.
            severity = getattr(analysis, "severity", None)
            info["severity"] = str(severity) if severity is not None else None
            info["detail"] = str(analysis)[:2000]
            # Treat anything above LIKELY_SAFE as unsafe -> flagged.
            sev_str = (info["severity"] or "").upper()
            info["safe"] = sev_str in ("LIKELY_SAFE", "SAFE", "NONE", "")
        except Exception:  # older API: is_likely_safe attr
            info["safe"] = bool(getattr(pickled, "is_likely_safe", False))
    except Exception as exc:  # noqa: BLE001
        info["error"] = "%s: %s" % (type(exc).__name__, exc)
    return info


def _cli_check(path: pathlib.Path) -> dict:
    """Run the fickling CLI safety check as a cross-check / fallback."""
    out = {"returncode": None, "stdout": None, "stderr": None, "error": None}
    try:
        proc = subprocess.run(
            ["fickling", "--check-safety", "-s", str(path)],
            capture_output=True, text=True, timeout=120,
        )
        out["returncode"] = proc.returncode
        out["stdout"] = proc.stdout[:4000]
        out["stderr"] = proc.stderr[:2000]
    except Exception as exc:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
    return out


def _flagged(api: dict, cli: dict) -> bool:
    """A file is 'flagged' only on a POSITIVE unsafe verdict — the API judged it
    not-safe, or the CLI explicitly reported it unsafe. We deliberately do NOT
    treat a non-zero CLI exit as a detection: fickling also exits non-zero when
    it simply cannot parse the input as a pickle (e.g. EmptyPickleError on a
    non-pickle .bin). Counting that parse error as a 'catch' produced a false
    positive on the clean set, so an unparseable file yields flagged=False."""
    if api.get("safe") is False:
        return True
    stdout = (cli.get("stdout") or "").lower()
    if "unsafe" in stdout or "likely unsafe" in stdout or "may be unsafe" in stdout:
        return True
    # Non-zero CLI exit is only a real detection when the file actually parsed as
    # a pickle (no parse error on either path) AND the API reached a verdict.
    parse_error = bool(api.get("error"))
    if (not parse_error
            and api.get("safe") is not None
            and cli.get("returncode") not in (0, None)
            and not cli.get("error")):
        return True
    return False


def main() -> int:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ver = tool_version()
    print("[fickling] version=%s" % ver)

    entries = []
    for variant, path in iter_model_files():
        t0 = time.perf_counter()
        api = _api_check(path)
        cli = _cli_check(path)
        elapsed = round(time.perf_counter() - t0, 6)
        flagged = _flagged(api, cli)
        err = api.get("error") or cli.get("error")
        entries.append({
            "variant": variant,
            "path": str(path),
            "bytes": path.stat().st_size,
            "flagged": flagged,
            "scan_seconds": elapsed,
            "result": {"api": api, "cli": cli},
        })
        print("[fickling]   %-18s flagged=%-5s %.4fs %s"
              % (variant, flagged, elapsed, "ERROR:" + err if err else ""))

    out = {"scanner": "fickling", "scanner_version": ver, "entries": entries}
    out["peak_ram_kb"] = _peak_ram_kb()
    print("[fickling] peak RSS = %.1f MB" % (out["peak_ram_kb"] / 1024.0))
    ARTIFACT.write_text(json.dumps(out, indent=2, default=str))
    print("[fickling] wrote %s (%d entries)" % (ARTIFACT, len(entries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
