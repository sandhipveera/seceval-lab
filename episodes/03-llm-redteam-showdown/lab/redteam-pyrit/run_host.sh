#!/usr/bin/env bash
# =============================================================================
# BENIGN CANARY LAB — HOST-RUN wrapper for the OAuth-CLI adversarial PyRIT path
# -----------------------------------------------------------------------------
# Runs run_host.py ON THE HOST. Preconditions:
#   * the chosen vendor CLI ($ADVERSARIAL_CLI, default codex) is on PATH and
#     already OAuth-signed-in (codex login / claude login / gemini login).
#   * python3 can `import pyrit` (else run_host.py drops to the CLI-driven
#     fallback loop, but we still nudge the user to install it for the real path).
#   * the vuln-agent is reachable on the host at :8000 — bring it up with
#     docker-compose.hostpyrit.yml (see README).
# Artifacts are written to ../artifacts so scripts/normalize_findings.py finds
# pyrit.json alongside the other frameworks' outputs.
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

# Point run_host.py at the shared lab artifacts dir (../artifacts).
export ARTIFACTS_DIR="${ARTIFACTS_DIR:-$HERE/../artifacts}"
mkdir -p "$ARTIFACTS_DIR"

ADVERSARIAL_CLI="${ADVERSARIAL_CLI:-codex}"

# 1) Vendor CLI must be on PATH.
if ! command -v "$ADVERSARIAL_CLI" >/dev/null 2>&1; then
  echo "ERROR: '$ADVERSARIAL_CLI' not found on PATH." >&2
  echo "       Install/sign in first (e.g. 'codex login' / 'claude login' / 'gemini login')," >&2
  echo "       or set ADVERSARIAL_CLI to one you have." >&2
  exit 1
fi

# 2) PyRIT is optional (fallback exists) but recommended for the real path.
if ! python3 -c "import pyrit" >/dev/null 2>&1; then
  echo "NOTE: python3 cannot import pyrit — the run will use the CLI-driven fallback loop." >&2
  echo "      For the real multi-turn CrescendoAttack path, install it:" >&2
  echo "      pip install pyrit==0.14.0 httpx" >&2
fi

echo "Running host PyRIT (adversarial CLI = $ADVERSARIAL_CLI, artifacts -> $ARTIFACTS_DIR) ..."
exec python3 run_host.py
