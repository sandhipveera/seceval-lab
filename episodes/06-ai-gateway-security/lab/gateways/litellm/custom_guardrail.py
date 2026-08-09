#!/usr/bin/env python3
"""LiteLLM-shaped custom guardrail for the Ep.06 lab.

Modeled on LiteLLM Proxy's documented CustomGuardrail extension point (a class with pre-call and
post-call hooks, registered in config.yaml under `guardrails:` as `guardrail: <module>.<class>`).
This file is written to be portable to a REAL litellm[proxy] install with minimal changes -- the
hook names and responsibilities match the documented shape -- but gateway.py in this container
calls it directly (see the judgment-call note at the top of config.yaml) rather than through the
real litellm proxy engine, since this build environment cannot install/verify that package.

Both hooks are pure, offline, deterministic pattern matches against patterns.py. No network calls,
no model inference -- this guardrail can never itself be the source of nondeterminism.
"""
from patterns import scan_input, scan_output, redact_pii


class CanaryGuardrail:
    """mode=["pre_call", "post_call"] per config.yaml."""

    def __init__(self, canary_value: str, enabled: bool = True):
        self.canary_value = canary_value
        self.enabled = enabled

    # ---- pre_call: runs on the REQUEST, before it reaches the model ----------------------------
    def async_pre_call_hook(self, input_text: str) -> dict:
        """Returns {"block": bool, "rule": str, "text": <possibly redacted text to forward>}."""
        if not self.enabled:
            return {"block": False, "rule": "", "text": input_text}
        hits = scan_input(input_text)
        if hits["injection"]:
            return {"block": True, "rule": "input-injection-pattern", "text": input_text}
        if hits["pii"]:
            # PII is redacted, not blocked outright -- the request still proceeds (attack a3's
            # pass condition is "redacted before reaching stub-model", not "request rejected").
            return {"block": False, "rule": "input-pii-redacted", "text": redact_pii(input_text)}
        return {"block": False, "rule": "", "text": input_text}

    # ---- post_call: runs on the RESPONSE, before it reaches the caller -------------------------
    def async_post_call_success_hook(self, output_text: str) -> dict:
        """Returns {"block": bool, "rule": str}."""
        if not self.enabled:
            return {"block": False, "rule": ""}
        hits = scan_output(output_text, self.canary_value)
        if hits["canary"]:
            return {"block": True, "rule": "output-canary-pattern"}
        return {"block": False, "rule": ""}
