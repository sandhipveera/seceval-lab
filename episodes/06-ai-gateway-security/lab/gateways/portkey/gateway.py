#!/usr/bin/env python3
"""Portkey-OSS-gateway-shaped proxy for the Ep.06 lab. See the judgment-call note in config.json:
this container interprets config.json's declarative input_guardrails/output_guardrails as a
first-class ruleset (no custom Python required to add a check) -- that is the real, documented
Portkey differentiator vs. LiteLLM's hook-based custom guardrail. It does not vendor the literal
`@portkey-ai/gateway` npm package (no network access here to install/verify it).

Posture note (this is a REAL finding, not a lab bug): Portkey's OSS gateway historically ships
without a built-in admin/management-plane auth mechanism -- that lived in Portkey's paid Control
Plane. This container reproduces that: /admin/config answers unauthenticated by design. Recorded
faithfully by the P1 posture check rather than papered over to make the three gateways look even.

Ports: :8787 the OpenAI-compatible proxy (Portkey's conventional default port) + /admin/config.
       :8788 /meta for the runner's posture checks.
"""
import json
import os
import threading

import requests
from flask import Flask, jsonify, request

from patterns import scan_input, scan_output, redact_pii

GATEWAY_NAME = "portkey"
PINNED_VERSION = "1.10.5"  # TODO: verify against the npm registry -- see Dockerfile TODO
STUB_URL = "http://ep06-stub-model:8080/v1/chat/completions"
GUARDRAILS = os.environ.get("GUARDRAILS", "on").strip().lower()
CANARY_VALUE = os.environ.get("CANARY_VALUE", "CANARY-EP06-9f2c1a")

with open(os.environ.get("PORTKEY_CONFIG", "/app/config.json")) as f:
    CONFIG = json.load(f)

ENABLED = GUARDRAILS == "on"

app = Flask(__name__)
meta_app = Flask(__name__ + ".meta")


def _flatten_messages(messages) -> str:
    parts = []
    for m in messages or []:
        c = m.get("content", "")
        if isinstance(c, list):
            c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
        parts.append(str(c))
    return " \n ".join(parts)


def _run_input_guardrails(text: str):
    """Walk config.json's input_guardrails in order. Returns (deny: bool, redacted_text, fired: [ids])."""
    fired = []
    out_text = text
    if not ENABLED:
        return False, out_text, fired
    hits = scan_input(text)
    for g in CONFIG.get("input_guardrails", []):
        for check in g.get("checks", []):
            rule = (check.get("parameters") or {}).get("rule")
            if rule == "injection" and hits["injection"]:
                fired.append(g["id"])
                if g.get("on_fail", {}).get("action") == "deny":
                    return True, out_text, fired
            elif rule == "pii" and hits["pii"]:
                fired.append(g["id"])
                if g.get("on_fail", {}).get("action") == "redact":
                    out_text = redact_pii(out_text)
    return False, out_text, fired


def _run_output_guardrails(text: str):
    fired = []
    if not ENABLED:
        return False, fired
    hits = scan_output(text, CANARY_VALUE)
    for g in CONFIG.get("output_guardrails", []):
        for check in g.get("checks", []):
            rule = (check.get("parameters") or {}).get("rule")
            if rule == "canary" and hits["canary"]:
                fired.append(g["id"])
                if g.get("on_fail", {}).get("action") == "deny":
                    return True, fired
    return False, fired


@app.get("/health")
def health():
    return jsonify(status="ok", guardrails=GUARDRAILS), 200


@app.get("/admin/config")
def admin_config():
    # No auth check -- see the posture note in the module docstring. This is intentional and
    # matches the real product's historical OSS posture, not an oversight.
    return jsonify(CONFIG), 200


@app.post("/v1/chat/completions")
def chat_completions():
    body = request.get_json(force=True, silent=True) or {}
    messages = body.get("messages", [])
    input_text = _flatten_messages(messages)

    deny, redacted_text, fired_in = _run_input_guardrails(input_text)
    if deny:
        return jsonify(error={"message": "denied by portkey guardrail", "type": "guardrail_blocked",
                               "param": ",".join(fired_in)}), 400

    fwd_messages = list(messages)
    if redacted_text != input_text:
        for i in range(len(fwd_messages) - 1, -1, -1):
            if fwd_messages[i].get("role") == "user":
                fwd_messages[i] = {**fwd_messages[i], "content": redacted_text}
                break

    try:
        r = requests.post(STUB_URL, json={**body, "messages": fwd_messages}, timeout=30)
        upstream = r.json()
    except Exception as e:
        return jsonify(error={"message": f"upstream unreachable: {e}", "type": "upstream_error"}), 502

    choices = upstream.get("choices") or []
    reply_text = (choices[0].get("message") or {}).get("content", "") if choices else ""

    deny_out, fired_out = _run_output_guardrails(reply_text)
    if deny_out:
        return jsonify(
            id=upstream.get("id"), object="chat.completion", model=upstream.get("model"),
            error={"message": "response denied by portkey guardrail", "type": "guardrail_blocked",
                   "param": ",".join(fired_out)},
            x_stub_saw=upstream.get("x_stub_saw", ""),
        ), 200

    upstream["x_gateway"] = GATEWAY_NAME
    upstream["x_gateway_guardrails"] = GUARDRAILS
    return jsonify(upstream), 200


@meta_app.get("/meta")
def meta():
    return jsonify(gateway=GATEWAY_NAME, version=PINNED_VERSION,
                    image_digest="TODO(DIGEST-PIN): resolve with `docker buildx imagetools "
                                 "inspect` against the real published image before publishing "
                                 "numbers -- this build environment has no network access",
                    guardrails_enabled=ENABLED,
                    guardrails_native=True,
                    guardrails_mechanism="declarative config.json input_guardrails/"
                                         "output_guardrails, portkey-shaped"), 200


def _run_meta():
    meta_app.run(host="0.0.0.0", port=8788, threaded=True, use_reloader=False)


if __name__ == "__main__":
    print(f"portkey-shaped gateway up — GUARDRAILS={GUARDRAILS}, version={PINNED_VERSION}", flush=True)
    threading.Thread(target=_run_meta, daemon=True).start()
    app.run(host="0.0.0.0", port=8787, threaded=True)
