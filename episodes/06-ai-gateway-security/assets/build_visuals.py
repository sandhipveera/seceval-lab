#!/usr/bin/env python3
"""Ep.06 visual driver. Emits cover (1200x1500) + 5-slide carousel (1080x1350) + PDF.

Every number below is verified against lab/artifacts/{findings,posture,metrics}.csv and
versions.json at commit f079f5b. Do NOT edit a number here without re-running the CSV check.

Two framings that must not be softened, both hard-won:
  * "5 of 5 blocked" measures ENFORCEMENT of my own policy, not any vendor's detection quality.
  * "13 of 24" is a fact about a test I deliberately wrote to be hard. It is not a
    false-positive rate over production traffic, and must never be phrased as one.
"""
import os, sys

sys.path.insert(0, "/sessions/busy-nifty-newton/mnt/dev/projectmgmt/data/linkedin/_brand")
from casestudy_visuals import build_all  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

SPEC = {
    "date": "2026-08-12",
    "slug": "ep06-ai-gateway-security",
    "eyebrow": "SECURITY LAB EP.06",   # this is an episode, not a case study
    "logo": "/sessions/busy-nifty-newton/mnt/dev/accessquint/dist/public/logo-assets/logo-light.png",

    "title": ["5 of 5 attacks blocked.", "13 of 24 real questions refused."],
    "subhead": ["The same guardrail, installed inside three AI gateways.",
                "The second number is the one nobody sells you."],

    "carousel_hook": ["Same guardrail.", "Three AI gateways.", "5 of 5 attacks blocked."],
    "carousel_hook_accent": "13 of 24 real questions refused.",

    "timeline": [
        ("MAR 2026", ["TeamPCP backdoors two LiteLLM",
                      "releases on PyPI. Live for",
                      "about forty minutes."]),
        ("APR 2026", ["CVE-2026-42208: pre-auth SQL",
                      "injection in LiteLLM Proxy.",
                      "Exploited within 36 hours."]),
        ("MAY 2026", ["Palo Alto Networks closes its",
                      "acquisition of Portkey."]),
        ("AUG 2026", ["This lab: three real gateways,",
                      "pinned by digest, no egress,",
                      "one policy installed in each."]),
    ],

    "what_happened": [
        "One detection policy, installed in all three gateways. Five benign attacks",
        "plus two clean sets, fired through a vulnerable app holding a canary.",
        "My first clean set scored zero false positives, and it was worthless:",
        "not one of its 24 prompts contained a single word the guard looks for.",
    ],

    "stats": [
        ("5 / 5", "attacks blocked by LiteLLM and Portkey with the policy on"),
        ("0 / 24", "flagged on the easy clean set: guaranteed by construction, not measured"),
        ("13 / 24", "refused on the hard clean set, the identical 13 on both gateways"),
        ("2 of 3", "ship the admin API reachable without credentials in-network"),
    ],

    "why_it_matters": [
        "A gateway is an enforcement surface, not a detector. All three did exactly",
        "what they are built to do. The policy you install is where the security",
        "actually lives, and the policy that stopped every attack also refused more",
        "than half of a set of questions a real customer would plausibly ask.",
    ],

    "kicker": ["Portkey refuses visibly. LiteLLM rewrites the question and answers anyway.",
               "The same 13 of 24. One failure you can see, one you cannot."],

    "moves_title": "FIVE MOVES THIS QUARTER",
    "moves": [
        "Write a hard clean set before you trust any false-positive number, including your own.",
        "Ask what your gateway does to a request it dislikes but does not refuse.",
        "Close the admin API. “Internal network” is not an authentication scheme.",
        "Pin gateway images by digest. A fixed tag is still a floating reference.",
        "Budget for the proxy, not the guardrail. Scanning is nearly free; the hop is not.",
    ],

    "cta": "Enforcement is not detection. Proving what a control actually does, and what it breaks, "
           "is the work. Full teardown and the reproducible lab in the comments.",

    "sources_line": "Security Lab Ep.06 · LiteLLM 1.83.7 · Portkey 1.15.2 · Bifrost 1.6.8  |  seceval-lab @f079f5b",
}

if __name__ == "__main__":
    out = build_all(SPEC, HERE)
    print("cover    :", out["cover_png"])
    print("carousel :", out["carousel_pdf"])
    for s in out["slides"]:
        print("   slide :", os.path.basename(s))
