#!/usr/bin/env bash
# Run the scenario against the products and capture artifacts. Exit 0 on success.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
RUN_ID="${RUN_ID:-$(date +%Y%m%d-%H%M%S)}"
echo "[*] run $RUN_ID"
# 1. start metric capture in background
"$ROOT/scripts/capture/capture_metrics.sh" "$RUN_ID" 180 2 &
MPID=$!
# 2. fire the attack scenario
"$ROOT/attack-range/generators/run_attack.sh" "$ROOT/attack-range/scenarios/web-recon-v1.yml" "$RUN_ID"
# 3. stop capture, collect alerts/exports
wait $MPID || true
echo "[TODO] export each product's alerts/findings into artifacts/$RUN_ID/"
echo "[*] done: artifacts/$RUN_ID"
