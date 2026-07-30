#!/usr/bin/env bash
# Send plain / charinject / emoji through Guardrails AI -> artifacts/guardrails.json
# Needs the Hub validators baked at build:
#   GUARDRAILS_TOKEN=xxxx docker compose build guard-guardrails
set -uo pipefail
cd "$(dirname "$0")/.."

docker compose --profile guardrails up -d --build --wait target-chatbot guard-guardrails attack-runner || {
  echo "!! guardrails profile did not come up healthy — check: docker compose --profile guardrails logs guard-guardrails"; }

docker compose exec -T \
  -e HIT_URL="http://ep05-guard-guardrails:8080/chat" \
  -e LABEL="guardrails" \
  -e OUTFILE="/artifacts/guardrails.json" \
  attack-runner python /app/run.py

echo "guardrails -> artifacts/guardrails.json"
docker compose --profile guardrails down --remove-orphans
