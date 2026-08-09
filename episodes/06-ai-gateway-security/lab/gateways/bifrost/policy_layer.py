#!/usr/bin/env python3
"""Bring-your-own policy layer for Bifrost -- NOT a Bifrost-native feature.

Build item 6 in CLAUDE_CODE_BUILD.md is explicit: "bring-your-own policy layer if it has no
native equivalent -- note that honestly in the coverage grid rather than scoring it as a miss."
Bifrost's OSS core (per Maxim AI's own positioning, and this episode's POST.md) is the low-
overhead router, not a guardrails product -- it does not ship an input/output prompt-inspection
catalog the way LiteLLM's custom-guardrail hook or Portkey's declarative guardrails do. GUARDRAILS
=on in this container therefore does not turn on a Bifrost feature; it turns on THIS module, which
we wrote for the lab using the exact same shared patterns.py every other gateway uses, so the
detection LOGIC is comparable even though the capability is not native. The coverage grid must
record "guardrails_native: false" for Bifrost -- see gateway.py's /meta endpoint -- so nobody
reads a Bifrost catch as evidence the product ships this out of the box.
"""
from patterns import scan_input, scan_output, redact_pii


def check_input(text: str, enabled: bool):
    if not enabled:
        return False, text, []
    hits = scan_input(text)
    fired = []
    out = text
    if hits["injection"]:
        fired.append("bring-your-own-injection-guard")
        return True, out, fired
    if hits["pii"]:
        fired.append("bring-your-own-pii-guard")
        out = redact_pii(out)
    return False, out, fired


def check_output(text: str, canary_value: str, enabled: bool):
    if not enabled:
        return False, []
    hits = scan_output(text, canary_value)
    if hits["canary"]:
        return True, ["bring-your-own-canary-egress-guard"]
    return False, []
