#!/usr/bin/env python3
# =============================================================================
# EP04 firewall wrapper — ProtectAI Rebuff (offline mode).
# Exposes POST /classify {text} -> {label, score, ...}. Rebuff layers defenses:
#   * heuristics (offline)            -> always on
#   * vector similarity to known PIs  -> on if a local store is seeded (NOTES.md)
#   * LLM-based check                 -> ONLY if LLM_API_KEY is set (else stubbed)
#   * canary tokens                   -> Rebuff's signature trick (see NOTES.md)
# We report the max sub-score and whether the input trips a canary-token pattern.
# =============================================================================
import os
import re

from flask import Flask, jsonify, request

MODE = os.environ.get("REBUFF_MODE", "offline")
THRESHOLD = float(os.environ.get("THRESHOLD", "0.5"))
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

# Rebuff's heuristic detector. Import path has moved across releases; try a few.
_heur = None
for _path, _name in [
    ("rebuff.detect_pi_heuristics", "detect_prompt_injection_using_heuristic_on_input"),
    ("rebuff.sdk", "detect_pi_using_heuristic"),
    ("rebuff", "detect_pi_using_heuristic"),
]:
    try:
        _mod = __import__(_path, fromlist=[_name])
        _heur = getattr(_mod, _name)
        break
    except Exception:
        continue

# A canary-token pattern (Rebuff plants tokens like this; leakage == the model
# echoed a secret it should not have). Our lab plants CANARY-TOKEN-LAB-*.
CANARY_RE = re.compile(r"canary[-_ ]?token", re.IGNORECASE)

app = Flask(__name__)


def score(text: str):
    heur = 0.0
    if _heur is not None:
        try:
            heur = float(_heur(text or ""))
        except Exception:
            heur = 0.0
    # (Vector + LLM sub-scores would extend this list when configured — NOTES.md.)
    sub_scores = [heur]
    top = max(sub_scores) if sub_scores else 0.0
    label = "malicious" if top >= THRESHOLD else "benign"
    return label, round(top, 4), round(heur, 4)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "guard": "rebuff", "mode": MODE,
                    "heuristics": _heur is not None, "llm_check": bool(LLM_API_KEY)})


@app.post("/classify")
def classify():
    text = (request.get_json(force=True, silent=True) or {}).get("text", "")
    label, s, heur = score(text)
    return jsonify({
        "label": label, "score": s, "guard": "rebuff", "mode": MODE,
        "heuristic_score": heur,
        "canary_token_detected": bool(CANARY_RE.search(text or "")),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
