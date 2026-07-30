#!/usr/bin/env python3
"""Guardrails AI proxy for the Ep.05 lab.

Wraps the shared target with Guardrails AI Hub validators on the input (detect_jailbreak,
detect_prompt_injection) and a canary check on the output. Like the NeMo proxy, it validates the
RAW user text, so the plain jailbreak is expected to fail validation (caught) while the
smuggled/disguised variants pass the validators and reach the model.

Prints the Guardrails AI version on startup. Runtime is offline; validator models were baked at
build. Any validator that cannot load (missing token at build, or needs an LLM) is recorded as an
error rather than silently counting as a catch — same honesty rule as the Ep.04 lab.
"""
import os, re
from flask import Flask, request, jsonify
import requests

UPSTREAM = os.environ.get("UPSTREAM", "http://ep05-target:8080/chat")
CANARY = os.environ.get("CANARY", "CANARY-LAB-5-9F3A")
VALIDATORS = [v.strip() for v in os.environ.get("VALIDATORS", "detect-jailbreak,detect-prompt-injection").split(",")]

try:
    import guardrails as gd
    GR_VERSION = getattr(gd, "__version__", "unknown")
except Exception as e:            # pragma: no cover - surfaced on the Mac run
    GR_VERSION = f"import-error: {e}"

# Build the input Guard from whichever validators are installed. Each is optional; a missing one
# is recorded so we never miscount an unavailable validator as a successful catch.
_INPUT_GUARD = None
_LOAD_ERRORS = {}

def build_guard():
    global _INPUT_GUARD
    from guardrails import Guard
    guard = Guard()
    used = 0
    if "detect-jailbreak" in VALIDATORS:
        try:
            from guardrails.hub import DetectJailbreak
            guard = guard.use(DetectJailbreak, on_fail="exception")
            used += 1
        except Exception as e:
            _LOAD_ERRORS["detect-jailbreak"] = str(e)
    if "detect-prompt-injection" in VALIDATORS:
        try:
            from guardrails.hub import DetectPromptInjection
            guard = guard.use(DetectPromptInjection, on_fail="exception")
            used += 1
        except Exception as e:
            _LOAD_ERRORS["detect-prompt-injection"] = str(e)
    _INPUT_GUARD = guard if used else None

try:
    build_guard()
except Exception as e:
    _LOAD_ERRORS["guard"] = str(e)

def input_validates_clean(text: str):
    """Return (blocked, rule_or_error). blocked=True means a validator flagged the input."""
    if _INPUT_GUARD is None:
        return False, f"no-validators-loaded:{_LOAD_ERRORS}"
    try:
        _INPUT_GUARD.validate(text)
        return False, ""          # passed all validators
    except Exception as e:
        return True, f"guardrails:{type(e).__name__}"

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok", guard="guardrails-ai", version=GR_VERSION,
                   validators_loaded=(_INPUT_GUARD is not None), load_errors=_LOAD_ERRORS), 200

@app.post("/chat")
def chat():
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("message", "")

    blocked, rule = input_validates_clean(text)
    if blocked:
        return jsonify(blocked=True, verdict="block", rule=rule, reply=""), 200

    try:
        up = requests.post(UPSTREAM, json={"message": text}, timeout=30).json()
        reply = up.get("reply", "")
    except Exception as e:
        return jsonify(blocked=False, verdict="pass", reply="", error=str(e)), 200

    if CANARY in reply:
        return jsonify(blocked=True, verdict="block", rule="output-canary-check",
                       reply="[blocked: response withheld by output validator]"), 200

    return jsonify(blocked=False, verdict="pass", reply=reply, note=rule), 200

if __name__ == "__main__":
    print(f"Guardrails AI proxy up — version {GR_VERSION}; validators_loaded={_INPUT_GUARD is not None}", flush=True)
    app.run(host="0.0.0.0", port=8080)
