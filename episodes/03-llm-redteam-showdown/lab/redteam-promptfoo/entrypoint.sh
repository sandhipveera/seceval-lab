#!/usr/bin/env bash
# =============================================================================
# BENIGN CANARY LAB — Promptfoo runner
# Runs `promptfoo redteam` against the vuln-agent (TARGET_URL) and writes the
# JSON report to /artifacts/promptfoo.json.
#
# No internet egress at run time: labnet is internal:true; promptfoo runs fully
# offline (telemetry/update/remote-generation disabled via Dockerfile env).
# The base image is node:20-slim (no python), so the JSON wrapper uses node.
# =============================================================================
set -euo pipefail

export TARGET_URL="${TARGET_URL:-http://ep03-vuln-agent:8000/v1}"
# promptfoo's openai provider reads OPENAI_BASE_URL / OPENAI_API_KEY too; set both
# so the config resolves regardless of which the pinned version honors.
export OPENAI_BASE_URL="${TARGET_URL}"
export OPENAI_API_KEY="lab-dummy-key"

ART=/artifacts
mkdir -p "$ART"

PROMPTFOO_VERSION="$(promptfoo --version 2>/dev/null || echo unknown)"
echo "promptfoo version: ${PROMPTFOO_VERSION}"

# Generate + run the red-team eval. `promptfoo redteam run` both synthesizes the
# adversarial tests and evaluates them, writing the JSON report we normalize.
set +e
promptfoo redteam run \
  --config promptfooconfig.yaml \
  --output "${ART}/promptfoo_raw.json" \
  --no-progress-bar
PF_RC=$?
set -e
echo "promptfoo exit code: ${PF_RC}"

# Wrap/normalize into a single /artifacts/promptfoo.json with version metadata,
# tolerating a missing/renamed raw file (never crash the run).
node -e '
  const fs = require("fs");
  const art = process.argv[1];
  const ver = process.argv[2];
  let raw = null;
  try { raw = JSON.parse(fs.readFileSync(art + "/promptfoo_raw.json", "utf8")); }
  catch (e) { raw = null; }
  const out = { framework: "promptfoo", promptfoo_version: ver, raw: raw };
  fs.writeFileSync(art + "/promptfoo.json", JSON.stringify(out, null, 2));
  console.log("wrote " + art + "/promptfoo.json (raw " + (raw ? "present" : "missing") + ")");
' "$ART" "$PROMPTFOO_VERSION"
