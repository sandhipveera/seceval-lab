#!/usr/bin/env python3
# =============================================================================
# EP04 firewall wrapper — ProtectAI LLM Guard, PromptInjection input scanner.
# Exposes POST /classify {text} -> {label, score}. The fine-tuned scanner model
# (deberta-v3-based) is cached into the image at build time for offline runtime.
# =============================================================================
import os

from flask import Flask, jsonify, request
from llm_guard.input_scanners import PromptInjection
from llm_guard.input_scanners.prompt_injection import MatchType

THRESHOLD = float(os.environ.get("THRESHOLD", "0.5"))
# FULL match_type scans the whole prompt (not just a sliding window).
scanner = PromptInjection(threshold=THRESHOLD, match_type=MatchType.FULL)

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "guard": "llm-guard"})


@app.post("/classify")
def classify():
    text = (request.get_json(force=True, silent=True) or {}).get("text", "")
    # scan() -> (sanitized_prompt, is_valid, risk_score). is_valid False == injection.
    _sanitized, is_valid, risk_score = scanner.scan(text or "")
    label = "benign" if is_valid else "malicious"
    return jsonify({"label": label, "score": round(float(risk_score), 4), "guard": "llm-guard"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
