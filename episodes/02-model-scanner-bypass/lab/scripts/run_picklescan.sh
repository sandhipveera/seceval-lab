#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Run the picklescan scanner container against every model variant + the clean
# set. The container's entrypoint iterates the files, times each scan, and
# writes the raw artifact to artifacts/picklescan.json (mounted). We tee the
# container's run log to artifacts/picklescan.log so a small-vs-large timing
# comparison is visible per file.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."   # lab/ root (where docker-compose.yml lives)

mkdir -p artifacts
echo "[run_picklescan] scanning /models (variants + clean) with picklescan..."
docker compose run --rm picklescan 2>&1 | tee artifacts/picklescan.log

echo "[run_picklescan] raw artifact -> artifacts/picklescan.json"
