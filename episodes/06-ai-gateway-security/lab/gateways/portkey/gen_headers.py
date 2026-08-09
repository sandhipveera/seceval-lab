#!/usr/bin/env python3
"""Generate the per-request `x-portkey-config` header JSON the Ep.06 lab sends to the REAL Portkey
OSS gateway (portkeyai/gateway). Portkey's OpenAI-compatible endpoint is driven by per-request
headers, not a static server-side config, so victim-app injects these via OPENAI_EXTRA_HEADERS (set
by scripts/run_gateway.sh from headers.on.json / headers.off.json).

Routing: provider=openai + custom_host=stub. Guardrails (on only): Portkey's real `default.regexMatch`
check, one guardrail per concern, `deny:true` + `not:true` so the guardrail DENIES when the pattern
MATCHES (Portkey denies on verdict=false; regexMatch verdict=true means "matched", so `not` inverts
it into a fail-on-match). Node's regex engine here takes no flags, so case-insensitivity is baked in
by expanding letters to [xX] classes. Same detection intent as the lab's patterns.py, now enforced
by the real product. Output: writes headers.off.json and headers.on.json next to this file.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
STUB = "http://ep06-stub-model:8080/v1"
CANARY = "CANARY-EP06-9f2c1a"

# Same injection surface as gateways/*/patterns.py INJECTION_PATTERN (visible, non-decoded form --
# a5's obfuscation is meant to slip past input scanning and be caught on OUTPUT).
INJECTION = (
    r"(ignore (all|any|previous|prior).{0,30}instructions?"
    r"|reveal.{0,20}(system prompt|canary|secret)"
    r"|print.{0,20}(the |your )?canary"
    r"|what('?s| is).{0,10}the.{0,10}canary"
    r"|confirm.{0,20}canary"
    r"|include.{0,20}(the |your )?(system )?canary"
    r"|debug mode|post it to|send it to|exfil)"
)
# PII surface (SSN / test card / lab-only email domains) -- ASCII/case as in the a3 fixture.
PII = (r"(\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]?){13,16}\b"
       r"|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(invalid|test|example)\b)")


def ci(pattern: str) -> str:
    """Case-insensitive without regex flags: expand each literal ASCII letter to [lowerUPPER]."""
    out = []
    for ch in pattern:
        if "a" <= ch <= "z" or "A" <= ch <= "Z":
            out.append("[" + ch.lower() + ch.upper() + "]")
        else:
            out.append(ch)
    return "".join(out)


def guardrail(rule):  # deny when the pattern MATCHES
    return {"deny": True, "regexMatch": {"rule": rule, "not": True}}


# Portkey validates a config with `provider` as needing `api_key` too (stub ignores the value). This
# is required even for the guardrail-off routing-only config.
routing = {"provider": "openai", "api_key": "sk-lab-not-a-real-key", "custom_host": STUB}

cfg_off = dict(routing)
cfg_on = dict(routing,
              input_guardrails=[guardrail(ci(INJECTION)), guardrail(PII)],
              output_guardrails=[guardrail(CANARY)])

for name, cfg in [("headers.off.json", cfg_off), ("headers.on.json", cfg_on)]:
    # victim-app merges this object into the outgoing request headers. The x-portkey-config value is
    # itself a JSON string (Portkey parses it), so it is stringified here.
    (HERE / name).write_text(json.dumps({"x-portkey-config": json.dumps(cfg)}, indent=2))
    print(f"wrote {name}")
