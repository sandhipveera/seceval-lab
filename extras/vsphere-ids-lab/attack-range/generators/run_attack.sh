#!/usr/bin/env bash
# Execute an attack scenario against the isolated range. Tags output with a run id.
# Usage: run_attack.sh <scenario.yml> <run_id>
set -euo pipefail
SCENARIO="${1:?scenario yaml required}"
RUN_ID="${2:-$(date +%Y%m%d-%H%M%S)}"
OUT="artifacts/${RUN_ID}/attack"
mkdir -p "$OUT"

echo "[*] Running scenario '$SCENARIO' as run '$RUN_ID'"
echo "[!] SAFETY: confirm you are on the isolated attack segment (see docs/SAFETY.md)"

# This is a scaffold. Claude Code should implement a YAML parser that walks `steps` and
# invokes each tool inside the attack-range container, writing logs to $OUT.
# Placeholder so the pipeline wiring is testable end-to-end:
echo "scenario=$SCENARIO run_id=$RUN_ID started=$(date -Is)" | tee "$OUT/run.meta"
echo "[TODO] implement step execution (nmap/ffuf/nuclei/...) -> $OUT"
