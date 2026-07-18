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
# --wait blocks until each service is healthy (see the healthcheck anchor in
# docker-compose.yml). Critical: without it the battery fires while a guard is
# still loading its model -> connection refused -> app fails OPEN -> a broken
# guard is indistinguishable from one that missed every attack.
if [ "$NAME" = "none" ]; then
  docker compose up -d --build --wait canary-sink vuln-app
else
  docker compose --profile "$NAME" up -d --build --wait
fi

# Replay from inside labnet (no host port publishing needed on the internal net).
docker compose run --rm runner python replay.py "$NAME" attacks

# Tear down WITH the same profile we brought up. A bare `docker compose down`
# only stops default-profile services, leaving the firewall container running and
# holding labnet open ("Network ... Resource is still in use") — which also breaks
# the clean-state-between-runs fairness rule.
if [ "$NAME" = "none" ]; then
  docker compose down --remove-orphans
else
  docker compose --profile "$NAME" down --remove-orphans
fi
echo "== done: artifacts/$NAME.json =="
