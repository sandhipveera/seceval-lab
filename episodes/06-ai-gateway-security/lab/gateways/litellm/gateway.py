#!/usr/bin/env python3
"""LiteLLM-proxy-shaped gateway for the Ep.06 lab. See the judgment-call note at the top of
config.yaml: this is a lab-built proxy that reproduces LiteLLM Proxy's documented config.yaml
shape, master-key auth default, and custom-guardrail hook points, rather than vendoring the real
`litellm[proxy]` PyPI package (no network access here to install or verify it).

Two HTTP surfaces, run on two ports so version/posture probing never touches the request path:
  :4000  the OpenAI-compatible proxy victim-app talks to, plus the (master-key-gated) admin
         surface LiteLLM exposes at /model/info in the real product.
  :4001  /meta -- read-only container metadata for the runner's posture checks (P2 version read).
         Not part of any real LiteLLM surface; purely a lab convenience so the runner doesn't need
         a docker socket to learn what's running.
"""
import os
import threading

import requests
import yaml
from flask import Flask, jsonify, request

from custom_guardrail import CanaryGuardrail

GATEWAY_NAME = "litellm"
PINNED_VERSION = "1.83.7-stable"  # patched range starts here per the 2026 SQLi advisory (see README)
STUB_URL = "http://ep06-stub-model:8080/v1/chat/completions"
GUARDRAILS = os.environ.get("GUARDRAILS", "on").strip().lower()
MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
CANARY_VALUE = os.environ.get("CANARY_VALUE", "CANARY-EP06-9f2c1a")

with open(os.environ.get("LITELLM_CONFIG", "/app/config.yaml")) as f:
    CONFIG = yaml.safe_load(f)

# NOTE: config.yaml's `guardrails:` list is included for shape-authenticity -- it is what you'd
# actually write for a real LiteLLM Proxy deployment -- but this lab engine does not parse that
# list; it always wires up CanaryGuardrail directly. A real litellm[proxy] install DOES parse it
# (that's the documented `guardrail: <module>.<class>` extension point custom_guardrail.py is
# written against). See the judgment-call note at the top of config.yaml.
guard = CanaryGuardrail(canary_value=CANARY_VALUE, enabled=(GUARDRAILS == "on"))

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


@app.get("/health")
def health():
    return jsonify(status="ok", guardrails=GUARDRAILS), 200


@app.get("/model/info")
def model_info():
    # Real LiteLLM behavior: with a master_key configured, management endpoints require
    # `Authorization: Bearer <master_key>`; without one configured, they are open. This is a real
    # posture fact we faithfully reproduce -- it is what the P1 posture check is measuring.
    if MASTER_KEY:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {MASTER_KEY}":
            return jsonify(error="unauthorized"), 401
    return jsonify(data=[{"model_name": m["model_name"]} for m in CONFIG.get("model_list", [])]), 200


@app.post("/v1/chat/completions")
def chat_completions():
    body = request.get_json(force=True, silent=True) or {}
    messages = body.get("messages", [])
    input_text = _flatten_messages(messages)

    pre = guard.async_pre_call_hook(input_text)
    if pre["block"]:
        return jsonify(error={"message": "blocked by ep06-canary-guard", "type": "guardrail_blocked",
                               "param": pre["rule"]}), 400

    # Forward (possibly redacted) messages upstream to the stub.
    fwd_messages = list(messages)
    if fwd_messages and pre["text"] != input_text:
        # Redaction happened -- rewrite the last user-role turn's content with the redacted text.
        for i in range(len(fwd_messages) - 1, -1, -1):
            if fwd_messages[i].get("role") == "user":
                fwd_messages[i] = {**fwd_messages[i], "content": pre["text"]}
                break

    try:
        r = requests.post(STUB_URL, json={**body, "messages": fwd_messages}, timeout=30)
        upstream = r.json()
    except Exception as e:
        return jsonify(error={"message": f"upstream unreachable: {e}", "type": "upstream_error"}), 502

    choices = upstream.get("choices") or []
    reply_text = (choices[0].get("message") or {}).get("content", "") if choices else ""

    post = guard.async_post_call_success_hook(reply_text)
    if post["block"]:
        return jsonify(
            id=upstream.get("id"), object="chat.completion",
            model=upstream.get("model"),
            error={"message": "response withheld by ep06-canary-guard", "type": "guardrail_blocked",
                   "param": post["rule"]},
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
                    guardrails_enabled=(GUARDRAILS == "on"),
                    guardrails_native=True,
                    guardrails_mechanism="config-declared custom guardrail hook (pre_call + "
                                         "post_call), litellm-shaped"), 200


def _run_meta():
    meta_app.run(host="0.0.0.0", port=4001, threaded=True, use_reloader=False)


if __name__ == "__main__":
    print(f"litellm-shaped gateway up — GUARDRAILS={GUARDRAILS}, version={PINNED_VERSION}", flush=True)
    threading.Thread(target=_run_meta, daemon=True).start()
    app.run(host="0.0.0.0", port=4000, threaded=True)
