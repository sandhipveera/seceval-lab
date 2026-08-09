#!/usr/bin/env bash
# The fair-test rule, as a script: tear down to a CLEAN state, bring up exactly one gateway
# profile, repoint victim-app's OPENAI_BASE_URL at it, then run the harness twice --
# GUARDRAILS=off, then GUARDRAILS=on -- so the cost table in Round 3 measures the cost of the
# PROTECTION, not the cost of the proxy. Same target, same attacks, same clean container state;
# only the gateway (and its guardrails knob) changes.
#
# Usage: scripts/run_gateway.sh <litellm|portkey|bifrost>
set -uo pipefail
cd "$(dirname "$0")/.."

GW="${1:-}"
# Real upstream images have no /meta side-port, so version/digest/guardrail facts are passed to the
# runner as env (run.py prefers these over /meta). Digests were pinned by digest in STEP 0; see each
# gateways/*/Dockerfile FROM and artifacts/versions.json. VICTIM_OPENAI_KEY authenticates the client
# to a keyed gateway so we measure the guardrail rather than the auth wall.
VICTIM_OPENAI_KEY="sk-lab-not-a-real-key"
case "$GW" in
  litellm)
    BASE_URL="http://ep06-gw-litellm:4000/v1"; ADMIN_URL="http://ep06-gw-litellm:4000/model/info"
    VICTIM_OPENAI_KEY="sk-lab-master-not-real"          # LiteLLM master_key is set -> client must auth
    GATEWAY_VERSION="1.83.7-stable"
    GATEWAY_DIGEST="sha256:af0152ca6dfb6703b35c0d4899effa9ac132bce9a4fbcbe1dc6ef145c100db26"
    GATEWAY_GUARDRAILS_NATIVE="true"
    GATEWAY_GUARDRAILS_MECHANISM="LiteLLM CustomGuardrail hook (pre_call + post_call)"
    ;;
  portkey)
    # P1 probes the gateway's own web/management UI, which the OSS gateway serves with NO auth.
    BASE_URL="http://ep06-gw-portkey:8787/v1"; ADMIN_URL="http://ep06-gw-portkey:8787/public/"
    GATEWAY_VERSION="1.15.2"
    GATEWAY_DIGEST="sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d"
    GATEWAY_GUARDRAILS_NATIVE="true"
    GATEWAY_GUARDRAILS_MECHANISM="Portkey gateway guardrails (config-declared)"
    ;;
  bifrost)
    # P1 probes Bifrost's config/admin API, which ships with admin auth DISABLED by default
    # (/api/config -> auth_config.is_enabled=false) and returns full provider config unauthenticated.
    BASE_URL="http://ep06-gw-bifrost:8080/v1"; ADMIN_URL="http://ep06-gw-bifrost:8080/api/config"
    GATEWAY_VERSION="1.6.8"                               # /api/version on the pinned image
    GATEWAY_DIGEST="sha256:14f704fcee64de509c139d14458871a4221f71f28a397f2b4d92bbe092d7a63c"
    GATEWAY_GUARDRAILS_NATIVE="false"                    # no native guardrail -> "not offered", not a miss
    GATEWAY_GUARDRAILS_MECHANISM="bring-your-own policy layer (no native guardrail)"
    ;;
  *)
    echo "usage: $0 <litellm|portkey|bifrost>" >&2
    exit 1
    ;;
esac
export GATEWAY_VERSION GATEWAY_DIGEST GATEWAY_GUARDRAILS_NATIVE GATEWAY_GUARDRAILS_MECHANISM VICTIM_OPENAI_KEY

echo "== $GW: tearing down to a clean state (down -v) =="
docker compose --profile litellm --profile portkey --profile bifrost --profile run \
  down -v --remove-orphans

export GATEWAY_UNDER_TEST="$GW"
export GATEWAY_BASE_URL="$BASE_URL"
export GATEWAY_ADMIN_URL="$ADMIN_URL"

for GUARDRAILS in off on; do
  export GUARDRAILS
  # Header-driven gateways get their per-request config (routing + guardrails) via victim-app's
  # OPENAI_EXTRA_HEADERS. Portkey: pick the on/off header set. Others: none.
  if [ "$GW" = "portkey" ]; then
    export OPENAI_EXTRA_HEADERS="$(cat gateways/portkey/headers.$GUARDRAILS.json)"
  else
    export OPENAI_EXTRA_HEADERS=""
  fi
  echo "== $GW: guardrails=$GUARDRAILS -- bringing up target + gateway =="
  docker compose --profile "$GW" up -d --build --wait \
    stub-model doc-server canary-sink victim-app "$GW" || {
    echo "!! $GW (guardrails=$GUARDRAILS) did not come up healthy -- check: "\
"docker compose --profile $GW logs $GW" >&2
    continue
  }

  echo "== $GW: guardrails=$GUARDRAILS -- running the harness =="
  # --build so the runner image always reflects the current runner/ source. Without it, `run`
  # reuses a stale runner image (the `up --build` above only rebuilds the gateway + support
  # services, not the one-shot runner) -- which silently ran an old run.py in the c2 delta.
  docker compose --profile "$GW" --profile run run --build --rm runner || {
    echo "!! runner failed for $GW (guardrails=$GUARDRAILS)" >&2
  }
done

echo "== $GW: done. artifacts/raw_${GW}_off.json and artifacts/raw_${GW}_on.json should exist. =="
docker compose --profile "$GW" --profile run down --remove-orphans
