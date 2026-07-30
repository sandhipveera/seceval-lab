#!/usr/bin/env bash
# Send plain / charinject / emoji through Meta Llama Guard 4 -> artifacts/llamaguard.json
# GATED model — build first with a Hugging Face token (and accept the license on HF):
#   HF_TOKEN=hf_xxx docker compose build guard-llamaguard
#   # laptop-feasible fallback:
#   LLAMAGUARD_MODEL=meta-llama/Llama-Guard-3-1B HF_TOKEN=hf_xxx docker compose build guard-llamaguard
set -uo pipefail
cd "$(dirname "$0")/.."

docker compose --profile llamaguard up -d --build --wait target-chatbot guard-llamaguard attack-runner || {
  echo "!! llamaguard profile did not come up healthy — check: docker compose --profile llamaguard logs guard-llamaguard"; }

docker compose exec -T \
  -e HIT_URL="http://ep05-guard-llamaguard:8080/chat" \
  -e LABEL="llamaguard" \
  -e OUTFILE="/artifacts/llamaguard.json" \
  attack-runner python /app/run.py

echo "llamaguard -> artifacts/llamaguard.json"
docker compose --profile llamaguard down --remove-orphans
