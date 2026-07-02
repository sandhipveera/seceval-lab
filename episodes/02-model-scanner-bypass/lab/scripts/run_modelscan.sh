#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Run the Protect AI ModelScan container against every model variant + the
# clean set. Entrypoint times each per-file scan and writes the raw JSON to
# artifacts/modelscan.json (mounted). Container log is teed to
# artifacts/modelscan.log for small-vs-large timing.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p artifacts
echo "[run_modelscan] scanning /models (variants + clean) with ModelScan..."
docker compose run --rm modelscan 2>&1 | tee artifacts/modelscan.log

echo "[run_modelscan] raw artifact -> artifacts/modelscan.json"
