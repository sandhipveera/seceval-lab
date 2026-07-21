#!/usr/bin/env bash
# Send plain / charinject / emoji through NeMo Guardrails -> artifacts/nemo.json
set -uo pipefail
cd "$(dirname "$0")/.."

# --wait blocks until healthchecks pass, so the guard is never probed before it is up (Ep.04 fix).
docker compose --profile nemo up -d --build --wait target-chatbot guard-nemo attack-runner || {
  echo "!! nemo profile did not come up healthy — check: docker compose --profile nemo logs guard-nemo"; }

docker compose exec -T \
  -e HIT_URL="http://ep05-guard-nemo:8080/chat" \
  -e LABEL="nemo" \
  -e OUTFILE="/artifacts/nemo.json" \
  attack-runner python /app/run.py

echo "nemo -> artifacts/nemo.json"
# Profile-aware teardown so the profiled guard doesn't hold the network (Ep.04 fix).
docker compose --profile nemo down --remove-orphans
