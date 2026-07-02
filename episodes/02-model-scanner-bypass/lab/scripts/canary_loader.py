#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# canary_loader.py — BENIGN ground-truth load step.
#
# Loads ONE model file with pickle.load so that, if the file is "live", its
# embedded benign canary payload executes and sends a single HTTP GET to the
# in-network canary sink (${CANARY_URL}). That sink hit is our ground truth that
# the file actually runs code — so any scanner that called the file "safe" truly
# missed. Nothing weaponized: the payload only ever pings the sink on the
# isolated, no-egress labnet. See build_models.py for the full payload writeup.
#
# Run inside a container on labnet (e.g. the model-builder image), with
#   PYTHONPATH=/models        so `canary_payload` is importable, and
#   CANARY_URL=http://ep02-canary:8080/loaded/<label>   so each load is
#                              distinguishable in the sink's request log.
#
# Usage: python canary_loader.py <path-to-model-file> [label]
# ---------------------------------------------------------------------------
import os
import sys
import pickle
import pathlib


def main() -> int:
    if len(sys.argv) < 2:
        print("[canary-loader] usage: canary_loader.py <model-file> [label]")
        return 2
    path = pathlib.Path(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) > 2 else path.name
    url = os.environ.get("CANARY_URL", "(unset)")
    print("[canary-loader] loading %-14s <- %s  (CANARY_URL=%s)"
          % (label, path, url))
    try:
        with path.open("rb") as fh:
            pickle.load(fh)
        # pickle.load stops at the first STOP opcode, so the broken-archive
        # trailer is ignored and its leading payload still executes.
        print("[canary-loader]   %s: pickle.load completed — payload executed"
              % label)
    except Exception as exc:  # noqa: BLE001
        # The reduce (and thus the canary GET) may already have fired before any
        # later opcode raised, so a raised exception here is NOT proof of no-fire.
        print("[canary-loader]   %s: load raised %s: %s (canary may have fired)"
              % (label, type(exc).__name__, exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
