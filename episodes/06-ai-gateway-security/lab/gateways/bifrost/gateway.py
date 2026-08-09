#!/usr/bin/env python3
"""Bifrost (Maxim AI)-shaped proxy for the Ep.06 lab. JUDGMENT CALL (flag for operator review):
this container does not vendor the real Bifrost Go binary/image -- no network access in this
build environment to pull or verify it. gateway.py implements the routing config.json describes
(provider -> stub-model) plus, when GUARDRAILS=on, the bring-your-own policy_layer.py -- clearly
NOT a Bifrost-native feature; see that module's docstring and the coverage grid this produces via
/meta. Before publishing numbers, swap in the real upstream image (see Dockerfile TODO) and
re-run; if the real Bifrost genuinely ships no native guardrails catalog, this lab's bring-your-
own numbers should be reported as exactly that -- the cost of adding policy yourself -- not
compared as if it were an apples-to-apples native feature against LiteLLM/Portkey.

Ports: :8080 the OpenAI-compatible proxy + /admin/status.  :8081 /meta for posture checks.
"""
import json
import os
import threading

import requests
from flask import Flask, jsonify, request

from policy_layer import check_input, check_output

GATEWAY_NAME = "bifrost"
PINNED_VERSION = "0.10.0"  # TODO: verify against the real Bifrost release -- see Dockerfile TODO
STUB_URL = "http://ep06-stub-model:8080/v1/chat/completions"
GUARDRAILS = os.environ.get("GUARDRAILS", "on").strip().lower()
ENABLED = GUARDRAILS == "on"
CANARY_VALUE = os.environ.get("CANARY_VALUE", "CANARY-EP06-9f2c1a")

with open(os.environ.get("BIFROST_CONFIG", "/app/config.json")) as f:
    CONFIG = json.load(f)

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


@app.get("/admin/status")
def admin_status():
    # No auth check -- Bifrost's OSS core does not ship an admin auth layer either, per this
    # episode's research. Recorded faithfully by the P1 posture check.
    return jsonify(providers=[p["name"] for p in CONFIG.get("providers", [])],
                    guardrails_native=False), 200


@app.post("/v1/chat/completions")
def chat_completions():
    body = request.get_json(force=True, silent=True) or {}
    messages = body.get("messages", [])
    input_text = _flatten_messages(messages)

    deny, redacted_text, fired_in = check_input(input_text, ENABLED)
    if deny:
        return jsonify(error={"message": "denied by bring-your-own policy layer",
                               "type": "guardrail_blocked", "param": ",".join(fired_in)}), 400

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

    deny_out, fired_out = check_output(reply_text, CANARY_VALUE, ENABLED)
    if deny_out:
        return jsonify(
            id=upstream.get("id"), object="chat.completion", model=upstream.get("model"),
            error={"message": "response denied by bring-your-own policy layer",
                   "type": "guardrail_blocked", "param": ",".join(fired_out)},
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
                    guardrails_native=False,
                    guardrails_mechanism="bring-your-own (policy_layer.py) -- NOT a Bifrost-"
                                         "native capability, see coverage grid"), 200


def _run_meta():
    meta_app.run(host="0.0.0.0", port=8081, threaded=True, use_reloader=False)


if __name__ == "__main__":
    print(f"bifrost-shaped gateway up — GUARDRAILS={GUARDRAILS} (bring-your-own), "
          f"version={PINNED_VERSION}", flush=True)
    threading.Thread(target=_run_meta, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, threaded=True)
