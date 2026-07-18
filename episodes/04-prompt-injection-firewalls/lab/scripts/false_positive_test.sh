#!/usr/bin/env bash
# =============================================================================
# EPISODE 04 — false-positive (over-defense) test.
# Replays the BENIGN-but-scary set (prompts that merely contain words like
# "ignore", "system prompt", "password reset") through each firewall and records
# how many it wrongly blocks -> artifacts/false_positives.json.
#
# This is the test that separates "smart" from "paranoid": a guard that blocks
# 6/6 attacks AND 6/6 benign prompts hasn't defended anything, it's just off.
#
# NOTE: deliberately NOT `set -e`. One guard that can't build must not abort the
# whole sweep (pg2 is license-gated; vigil won't start — see firewalls/vigil/NOTES.md).
# Pass guard names to override the default set, e.g.
#   ./scripts/false_positive_test.sh llm-guard rebuff prompt-guard-2
# =============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."   # -> lab/

GUARDS=("$@")
if [ ${#GUARDS[@]} -eq 0 ]; then
  GUARDS=(llm-guard rebuff)     # the guards that actually stand up in this lab
fi

for NAME in "${GUARDS[@]}"; do
  echo "== false-positive test: GUARD=$NAME =="
  export GUARD="$NAME"
  # --wait: never fire the benign set at a guard that isn't listening yet.
  if ! docker compose --profile "$NAME" up -d --build --wait; then
    echo "!! SKIP $NAME — failed to build/start; NOT EVALUATED (no numbers recorded)"
    docker compose --profile "$NAME" down --remove-orphans >/dev/null 2>&1 || true
    continue
  fi
  docker compose run --rm runner python replay.py "$NAME" benign \
    || echo "!! $NAME — benign replay failed; NOT EVALUATED"
  docker compose --profile "$NAME" down --remove-orphans
done
echo "== done: artifacts/false_positives.json =="
