#!/usr/bin/env python3
"""Probe which rail/validator fires per variant. Hits HIT_URL with each attack variant and prints
the guard's own `rule`/`note` field, so we can report the MECHANISM (keyword self-check vs
perplexity heuristic vs which validator), not just caught/missed."""
import os, json
import requests
from encoders import ENCODERS

HIT_URL = os.environ["HIT_URL"]
for v, enc in ENCODERS.items():
    body = requests.post(HIT_URL, json={"message": enc()}, timeout=30).json()
    print(json.dumps({"variant": v, "verdict": body.get("verdict"),
                      "rule": body.get("rule") or body.get("note") or "", "http": 200}))
