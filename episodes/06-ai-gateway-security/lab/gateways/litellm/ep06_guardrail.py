#!/usr/bin/env python3
"""Real LiteLLM custom guardrail for the Ep.06 lab.

This runs INSIDE the real ghcr.io/berriai/litellm proxy via its documented CustomGuardrail
extension point (config.on.yaml `guardrails:` -> `guardrail: ep06_guardrail.Ep06CanaryGuardrail`).
It reuses the same offline, deterministic pattern matches as the lab's other gateways (patterns.py)
so the catch/miss SEMANTICS stay consistent across products, while latency and memory are now the
REAL LiteLLM proxy's. GUARDRAILS=on|off is handled one level up (ep06_entrypoint.sh selects
config.on.yaml vs config.off.yaml), so if this class is loaded at all, guardrails are on.

Design choices that protect the harness's honesty invariant (RUN.md rule 2):
  - Input injection is blocked by raising HTTPException(400). A 4xx is how a real guardrail SIGNALS
    a deliberate block; the runner reads it as gateway_blocked, NOT as a transport error. We do NOT
    raise a bare ValueError (that surfaces as a 500, which the runner correctly treats as
    NOT EVALUATED -- an erroring gateway must never score a catch).
  - Input PII is redacted in place; the (redacted) request still reaches the model, exactly as the
    a3 pass condition intends ("redacted before reaching the model").
  - Output canary is scrubbed (whole assistant message replaced), leaving a clean HTTP 200 whose
    body simply no longer contains the secret OR the exfil marker. That is an output-side catch that
    can never masquerade as an error.
"""
import os
from typing import Any, Optional, Union

from fastapi import HTTPException

import litellm
from litellm.integrations.custom_guardrail import CustomGuardrail

from patterns import redact_pii, scan_input, scan_output

CANARY_VALUE = os.environ.get("CANARY_VALUE", "CANARY-EP06-9f2c1a")


def _content_to_text(content) -> str:
    if isinstance(content, list):  # OpenAI content-parts form
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return str(content or "")


class Ep06CanaryGuardrail(CustomGuardrail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages") or []
        joined = " \n ".join(_content_to_text(m.get("content")) for m in messages)
        hits = scan_input(joined)
        if hits["injection"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "blocked by ep06-canary-guard",
                        "guardrail": "ep06-canary-guard", "rule": "input-injection-pattern"},
            )
        if hits["pii"]:
            for m in messages:
                c = m.get("content")
                if isinstance(c, str):
                    m["content"] = redact_pii(c)
                elif isinstance(c, list):
                    for p in c:
                        if isinstance(p, dict) and isinstance(p.get("text"), str):
                            p["text"] = redact_pii(p["text"])
            data["messages"] = messages
        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        try:
            if isinstance(response, litellm.ModelResponse):
                for choice in response.choices:
                    msg = getattr(choice, "message", None)
                    content = getattr(msg, "content", None) if msg is not None else None
                    if content and isinstance(content, str) and scan_output(content, CANARY_VALUE)["canary"]:
                        msg.content = "[response withheld by ep06-canary-guard: output-canary-pattern]"
        except Exception:
            # A guardrail must never turn a real answer into a false NOT-EVALUATED by erroring here.
            pass
        return response
