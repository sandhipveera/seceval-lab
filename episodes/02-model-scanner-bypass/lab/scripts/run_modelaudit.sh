#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Run the Promptfoo ModelAudit container against every model variant + the
# clean set. Entrypoint times each scan and writes SARIF to
# artifacts/modelaudit.sarif plus a JSON sidecar at artifacts/modelaudit.json
# (mounted). Container log teed to artifacts/modelaudit.log.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p artifacts
echo "[run_modelaudit] scanning /models (variants + clean) with ModelAudit..."
docker compose run --rm modelaudit 2>&1 | tee artifacts/modelaudit.log

echo "[run_modelaudit] raw artifacts -> artifacts/modelaudit.sarif (+ .json)"
