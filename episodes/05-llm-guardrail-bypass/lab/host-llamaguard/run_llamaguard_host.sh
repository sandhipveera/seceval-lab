#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run_llamaguard_host.sh — the host-side Metal Llama Guard 4 leg.
#
# 1. Brings up the target-chatbot with the host-published port (compose override).
# 2. Starts the MPS Llama Guard proxy (app_host.py) on :8091 and waits for it to
#    finish loading the model onto the Apple GPU.
# 3. Fires the same plain/charinject/emoji attack host-side via the real
#    attack-runner code -> artifacts/llamaguard.json (same schema as the
#    containerized guards, so normalize_findings.py just merges it).
# 4. Runs the benign fp_probe host-side for llamaguard's latency/false-positive row.
# 5. Tears the leg down. Honesty rule intact: if the model never loaded, the JSON
#    carries errors and the normalizer marks Llama Guard NOT EVALUATED.
# ---------------------------------------------------------------------------
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAB="$(cd "$HERE/.." && pwd)"
VENV="$HERE/.venv"
PY="$VENV/bin/python"
ART="$LAB/artifacts"
CANARY="CANARY-LAB-5-9F3A"
export LLAMAGUARD_MODEL="${LLAMAGUARD_MODEL:-meta-llama/Llama-Guard-4-12B}"
export LLAMAGUARD_FORCE_MM="${LLAMAGUARD_FORCE_MM:-1}"   # use the proper multimodal loader (torchvision installed)
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1     # model is already local; no egress at run time
export HF_TOKEN="$(security find-generic-password -s HF_TOKEN -w 2>/dev/null)"
mkdir -p "$ART"
log(){ printf '\n[llamaguard-host] %s\n' "$*"; }

cleanup(){
  log "cleanup"
  [ -n "${GUARD_PID:-}" ] && kill "$GUARD_PID" 2>/dev/null
  ( cd "$LAB" && docker compose -f docker-compose.yml -f host-llamaguard/docker-compose.hostguard.yml down --remove-orphans >/dev/null 2>&1 )
}
trap cleanup EXIT

# 1) target-chatbot with host-published port
log "bringing up target-chatbot (host-published :8080)"
( cd "$LAB" && docker compose -f docker-compose.yml -f host-llamaguard/docker-compose.hostguard.yml up -d --build --wait target-chatbot ) \
  || { log "target did not come up healthy"; exit 1; }
curl -fsS -m 5 http://localhost:8080/health >/dev/null && log "target reachable on host :8080" \
  || { log "target NOT reachable on host :8080 — check the override/port"; exit 1; }

# 2) start the MPS proxy and wait for the model to load
log "starting MPS Llama Guard proxy on :8091 (loading ${LLAMAGUARD_MODEL} onto Apple GPU)"
export UPSTREAM="http://127.0.0.1:8080/chat" CANARY PORT=8091
export PYTORCH_ENABLE_MPS_FALLBACK=1              # let unsupported ops fall back to CPU instead of crashing
"$PY" "$HERE/app_host.py" > "$HERE/proxy.log" 2>&1 &
GUARD_PID=$!

# poll /health until the model is loaded (or the proxy dies). Big model load can take minutes.
ready=""
for i in $(seq 1 120); do
  kill -0 "$GUARD_PID" 2>/dev/null || { log "proxy process died — see proxy.log"; break; }
  st=$(curl -fsS -m 3 http://localhost:8091/health 2>/dev/null)
  case "$st" in
    *'"status":"ok"'*|*'"status": "ok"'*) ready=1; log "proxy healthy: $st"; break;;
    *'model-not-loaded'*) log "model failed to load — will record NOT EVALUATED. health=$st"; break;;
  esac
  sleep 5
done

# 3) fire the attack host-side (real attack-runner code; encoders.py lives beside run.py)
log "firing plain/charinject/emoji host-side -> artifacts/llamaguard.json"
( cd "$LAB/attack-runner" && \
  HIT_URL="http://localhost:8091/chat" LABEL="llamaguard" CANARY="$CANARY" \
  VARIANTS="plain,charinject,emoji" OUTFILE="$ART/llamaguard.json" \
  "$PY" run.py )

# 4) benign false-positive / latency probe host-side (best-effort; feeds metrics)
if [ -n "$ready" ]; then
  log "benign fp_probe host-side -> artifacts/llamaguard_fp.json"
  ( cd "$LAB/attack-runner" && HIT_URL="http://localhost:8091/chat" PROMPTS="$LAB/attack-runner/benign_prompts.txt" \
    "$PY" fp_probe.py ) | tee "$ART/llamaguard_fp.json"
fi

log "done — see artifacts/llamaguard.json (proxy log: host-llamaguard/proxy.log)"
