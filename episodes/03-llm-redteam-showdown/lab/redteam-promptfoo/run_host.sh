#!/usr/bin/env bash
# =============================================================================
# BENIGN CANARY LAB — HOST-RUN wrapper for the OAuth-CLI adversarial Promptfoo path.
# Mirrors redteam-pyrit/run_host.sh. Runs `promptfoo redteam` ON THE HOST so its
# generator (cli_provider.js) can drive your OAuth'd CLI, while the objective
# target stays the LOCAL vuln-agent (published to localhost:18000). Writes
# ../artifacts/promptfoo.json so scripts/normalize_findings.py finds it.
#
# Preconditions:
#   * the vendor CLI ($ADVERSARIAL_CLI, default codex) is on PATH + OAuth-signed-in.
#   * promptfoo is available (global install or via npx).
#   * the vuln-agent is reachable at :18000 — bring it up with
#       docker compose -f docker-compose.yml -f docker-compose.hostpyrit.yml up -d --build
# =============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

export ARTIFACTS_DIR="${ARTIFACTS_DIR:-$HERE/../artifacts}"
mkdir -p "$ARTIFACTS_DIR"
export TARGET_URL="${TARGET_URL:-http://localhost:18000/v1}"
export ADVERSARIAL_CLI="${ADVERSARIAL_CLI:-codex}"

# Keep promptfoo offline for everything except our CLI generator (which is the
# only thing that legitimately reaches a model, OUTSIDE Docker, via OAuth).
export PROMPTFOO_DISABLE_TELEMETRY=1
export PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=1

# 1) Vendor CLI must be on PATH + logged in.
if ! command -v "$ADVERSARIAL_CLI" >/dev/null 2>&1; then
  echo "ERROR: '$ADVERSARIAL_CLI' not found on PATH." >&2
  echo "       Install/sign in first (e.g. 'codex login'), or set ADVERSARIAL_CLI." >&2
  exit 1
fi

# 2) Resolve a promptfoo runner (global bin, else npx with the pinned version).
if command -v promptfoo >/dev/null 2>&1; then
  PF=(promptfoo)
else
  echo "NOTE: 'promptfoo' not on PATH — using 'npx -y promptfoo@0.121.18'." >&2
  PF=(npx -y promptfoo@0.121.18)
fi
PF_VERSION="$(${PF[@]} --version 2>/dev/null || echo unknown)"
echo "promptfoo version: ${PF_VERSION} | adversarial CLI: ${ADVERSARIAL_CLI} | target: ${TARGET_URL}"

# 3) Run the red-team eval (synthesize + evaluate). Never hard-fail the wrapper.
set +e
"${PF[@]}" redteam run \
  --config promptfooconfig.host.yaml \
  --output "${ARTIFACTS_DIR}/promptfoo_raw.json" \
  --no-progress-bar
PF_RC=$?
set -e
echo "promptfoo exit code: ${PF_RC}"

# 4) Wrap/normalize into a single promptfoo.json (same shape the container writes),
#    tolerating a missing/renamed raw file.
node -e '
  const fs = require("fs");
  const art = process.argv[1];
  const ver = process.argv[2];
  let raw = null;
  try { raw = JSON.parse(fs.readFileSync(art + "/promptfoo_raw.json", "utf8")); }
  catch (e) { raw = null; }
  const out = { framework: "promptfoo", promptfoo_version: ver, engine: "host-cli-generator", raw: raw };
  fs.writeFileSync(art + "/promptfoo.json", JSON.stringify(out, null, 2));
  console.log("wrote " + art + "/promptfoo.json (raw " + (raw ? "present" : "missing") + ")");
' "$ARTIFACTS_DIR" "$PF_VERSION"
