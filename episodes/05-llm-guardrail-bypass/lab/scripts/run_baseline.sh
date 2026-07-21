#!/usr/bin/env bash
# Baseline: no guardrail. Prove the attack works against the raw target on plain + emoji (+ charinject).
set -uo pipefail
cd "$(dirname "$0")/.."

docker compose up -d --build --wait target-chatbot attack-runner || {
  echo "!! target/attacker did not come up healthy"; exit 1; }

docker compose exec -T \
  -e HIT_URL="http://ep05-target:8080/chat" \
  -e LABEL="baseline" \
  -e OUTFILE="/artifacts/baseline.json" \
  attack-runner python /app/run.py

echo "baseline -> artifacts/baseline.json"
