#!/usr/bin/env bash
# =============================================================================
# EPISODE 04 — false-positive (over-defense) test.
# Replays the BENIGN-but-scary set (prompts that merely contain words like
# "ignore", "system prompt", "password reset") through each firewall and records
# how many it wrongly blocks -> artifacts/false_positives.json.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."   # -> lab/

for NAME in prompt-guard-2 vigil llm-guard rebuff; do
  echo "== false-positive test: GUARD=$NAME =="
  export GUARD="$NAME"
  docker compose --profile "$NAME" up -d --build
  docker compose run --rm runner python replay.py "$NAME" benign
  docker compose down
done
echo "== done: artifacts/false_positives.json =="
