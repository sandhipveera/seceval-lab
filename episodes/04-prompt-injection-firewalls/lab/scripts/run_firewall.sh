#!/usr/bin/env bash
# =============================================================================
# EPISODE 04 — run the injection battery with ONE firewall guarding the door.
#   ./scripts/run_firewall.sh <none|prompt-guard-2|vigil|llm-guard|rebuff>
# Resets to a clean state, brings up the target (+ the named firewall profile),
# replays the full battery via the in-network runner, and writes
# artifacts/<name>.json. Baseline: `run_firewall.sh none` MUST fire the canary
# on every attack (proves the injection works before any guard is added).
# =============================================================================
set -euo pipefail
NAME="${1:?usage: run_firewall.sh <none|prompt-guard-2|vigil|llm-guard|rebuff>}"
cd "$(dirname "$0")/.."   # -> lab/

export GUARD="$NAME"
echo "== Episode 04: running battery with GUARD=$NAME =="

# Bring up the target (+ firewall). --build so image changes take effect.
if [ "$NAME" = "none" ]; then
  docker compose up -d --build canary-sink vuln-app
else
  docker compose --profile "$NAME" up -d --build
fi

# Replay from inside labnet (no host port publishing needed on the internal net).
docker compose run --rm runner python replay.py "$NAME" attacks

docker compose down
echo "== done: artifacts/$NAME.json =="
