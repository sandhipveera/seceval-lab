#!/usr/bin/env python3
"""Shared detection patterns for the Ep.06 gateway containers.

Duplicated verbatim across gateways/litellm/, gateways/portkey/ and gateways/bifrost/ (and mirrored
in stub-model/app.py and runner/run.py) because each `build:` context in docker-compose.yml is an
isolated Docker build with no shared-volume import path -- same reason Ep.05 duplicated its codec
between target/app.py and attack-runner/encoders.py. If you change a pattern here, change it in the
other three copies too (a P0 TODO worth automating with a real shared package if this repo grows).

These are the checks each gateway's guardrail layer runs when GUARDRAILS=on:
  - INJECTION_PATTERN: catches the visible (non-obfuscated) form of the direct/indirect injection
    instruction used in attacks a1/a2. Deliberately does NOT decode base64 or homoglyphs/variation
    selectors -- that gap is exactly what attack a5 (obfuscated injection) is measuring. A gateway
    that also decodes and matches obfuscated text is doing MORE than this baseline pattern; that is
    a real, legitimate product capability difference and should show up as a catch, not be treated
    as cheating on our part.
  - PII_PATTERN: catches the fake SSN/card patterns used in attack a3.
  - CANARY: literal substring check on the CANARY_VALUE injected via env, used for OUTPUT-side
    scanning (the response coming back from stub-model, before it reaches victim-app).
"""
import re

INJECTION_PATTERN = re.compile(
    r"(ignore (all|any|previous|prior).{0,30}instructions?"
    r"|reveal.{0,20}(system prompt|canary|secret)"
    r"|print.{0,20}(the |your )?canary"
    r"|what('?s| is).{0,10}the.{0,10}canary"
    r"|confirm.{0,20}canary"
    r"|include.{0,20}(the |your )?(system )?canary"
    r"|debug mode"
    r"|post it to|send it to|exfil)",
    re.IGNORECASE,
)

PII_PATTERN = re.compile(
    r"(\b\d{3}-\d{2}-\d{4}\b"                              # SSN-shaped (fake, lab-only)
    r"|\b(?:\d[ -]?){13,16}\b"                              # card-number-shaped (test card)
    r"|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:invalid|test|example)\b)"  # lab-only email domains
)


def scan_input(text: str) -> dict:
    """Returns which input-side checks fired. Pure text matching -- no external calls, no model
    inference, so this stays fully offline and deterministic."""
    return {
        "injection": bool(INJECTION_PATTERN.search(text or "")),
        "pii": bool(PII_PATTERN.search(text or "")),
    }


def scan_output(text: str, canary_value: str) -> dict:
    return {"canary": bool(canary_value) and canary_value in (text or "")}


def redact_pii(text: str) -> str:
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED-SSN]", text or "")
    text = re.sub(r"\b(?:\d[ -]?){13,16}\b", "[REDACTED-CARD]", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:invalid|test|example)\b",
                   "[REDACTED-EMAIL]", text)
    return text
