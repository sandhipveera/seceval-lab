#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Run the Trail of Bits fickling container (allowlist mode) against every model
# variant + the clean set. Entrypoint times each scan and writes raw JSON to
# artifacts/fickling.json (mounted). Container log teed to artifacts/fickling.log.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p artifacts
echo "[run_fickling] scanning /models (variants + clean) with fickling (allowlist)..."
docker compose run --rm fickling 2>&1 | tee artifacts/fickling.log

echo "[run_fickling] raw artifact -> artifacts/fickling.json"
