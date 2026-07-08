#!/usr/bin/env python3
# =============================================================================
# EP04 firewall wrapper — deadbits/vigil-llm (patterns + embedding similarity).
# Exposes POST /classify {text} -> {label, score}. Vigil runs several input
# scanners (transformer injection model, YARA rules, and a vector-DB similarity
# check against known attack embeddings). We flag "malicious" if any scanner
# hits, and derive a score from the strongest match.
#
# OFFLINE SETUP (see NOTES.md): the transformer + embedding models are baked at
# build; the vector DB is seeded from bundled signatures. CONFIRM the API shape
# below against your vigil pin — perform_scan()'s return dict has shifted across
# releases; the parser here is defensive and treats any non-empty match as a hit.
# =============================================================================
import os

from flask import Flask, jsonify, request
from vigil.vigil import Vigil

CONF = os.environ.get("VIGIL_CONF", "/app/conf/server.conf")
vigil = Vigil.from_config(CONF)

app = Flask(__name__)


def _extract(result):
    """Defensively pull (flagged, score, n_matches) from vigil's scan result."""
    matches = []
    if isinstance(result, dict):
        res = result.get("results", result)
        if isinstance(res, dict):
            for _scanner, r in res.items():
                m = r.get("matches") if isinstance(r, dict) else None
                if m:
                    matches.extend(m if isinstance(m, list) else [m])
        flagged = bool(matches) or bool(result.get("messages"))
    else:
        flagged = bool(result)
    score = 0.0
    for m in matches:
        if isinstance(m, dict):
            for k in ("similarity", "score", "confidence", "distance"):
                if k in m:
                    try:
                        score = max(score, float(m[k]))
                    except (TypeError, ValueError):
                        pass
    return flagged, round(score, 4), len(matches)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "guard": "vigil"})


@app.post("/classify")
def classify():
    text = (request.get_json(force=True, silent=True) or {}).get("text", "")
    result = vigil.input_scanner.perform_scan(input_prompt=text or "")
    flagged, score, n = _extract(result)
    return jsonify({"label": "malicious" if flagged else "benign",
                    "score": score, "guard": "vigil", "matches": n})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
