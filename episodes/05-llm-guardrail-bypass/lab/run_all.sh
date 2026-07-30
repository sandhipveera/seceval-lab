#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run_all.sh — deterministic "shell core" for the Ep.05 guardrail-bypass lab.
#
# Chains the exact sequence RUN.md defines, but skips any guard whose token is
# missing instead of failing the whole run. A guard that never ran is left for
# normalize_findings.py to mark [NOT EVALUATED] — this script NEVER fakes a
# catch/miss and never hand-edits artifacts.
#
# Honesty rules (mirror RUN.md): benign canary only; labnet stays internal
# (no egress); if a guard won't build/run, it is NOT EVALUATED. Two of three
# guards running cleanly is a legitimate result.
#
# Env:
#   HF_TOKEN            bakes NeMo's gpt2 + (gated) Llama Guard 4. Unset -> skip both.
#   GUARDRAILS_TOKEN    installs Guardrails AI validators at build. Unset -> skip.
#   LLAMAGUARD_MODEL    optional override, e.g. meta-llama/Llama-Guard-3-1B (lighter).
#   KEEP_UP=1           leave containers running after the run (default: tear down).
#
# Usage:  bash run_all.sh      (run from anywhere; it cd's to its own lab dir)
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"
LAB="$PWD"
log(){ printf '\n[run_all %s] %s\n' "$(basename "$LAB")" "$*"; }

# 1) BASELINE — the attack must work against the raw target, or guards are meaningless.
log "baseline (proving the attack leaks against the raw target)"
./scripts/run_baseline.sh
if ! grep -q '"canary_leaked"[[:space:]]*:[[:space:]]*true' artifacts/baseline.json 2>/dev/null; then
  log "BASELINE DID NOT LEAK — target build is wrong. Aborting (guards would be meaningless)."
  exit 2
fi

# 2) NeMo Guardrails — build bakes gpt2, which needs HF_TOKEN.
if [ -n "${HF_TOKEN:-}" ]; then
  log "nemo"; ./scripts/run_nemo.sh || log "nemo run errored — leaving it NOT EVALUATED"
else
  log "SKIP nemo — HF_TOKEN not set (normalize will mark it NOT EVALUATED)"
fi

# 3) Guardrails AI — Hub validators are baked at build, which needs GUARDRAILS_TOKEN.
if [ -n "${GUARDRAILS_TOKEN:-}" ]; then
  log "guardrails (build + run)"
  GUARDRAILS_TOKEN="$GUARDRAILS_TOKEN" docker compose build guard-guardrails \
    || log "guardrails build failed — leaving it NOT EVALUATED"
  ./scripts/run_guardrails.sh || log "guardrails run errored — leaving it NOT EVALUATED"
else
  log "SKIP guardrails — GUARDRAILS_TOKEN not set (normalize will mark it NOT EVALUATED)"
fi

# 4) Meta Llama Guard 4 — gated; needs HF_TOKEN + accepted license. Heavy (~24GB on the 12B).
if [ -n "${HF_TOKEN:-}" ]; then
  log "llamaguard (build + run; model=${LLAMAGUARD_MODEL:-default 12B})"
  HF_TOKEN="$HF_TOKEN" docker compose build guard-llamaguard \
    || log "llamaguard build failed — leaving it NOT EVALUATED"
  ./scripts/run_llamaguard.sh || log "llamaguard run errored — leaving it NOT EVALUATED"
else
  log "SKIP llamaguard — HF_TOKEN not set (normalize will mark it NOT EVALUATED)"
fi

# 5) Metrics (added latency, peak memory, false positives on the benign set).
log "metrics"; ./scripts/capture_metrics.sh || log "capture_metrics errored"

# 6) Normalize everything into one comparable table (this is what marks NOT EVALUATED).
log "normalize"; python3 scripts/normalize_findings.py || log "normalize errored"

log "=== findings ==="; cat artifacts/findings.csv 2>/dev/null || echo "(no findings.csv produced)"
log "=== metrics  ==="; cat artifacts/metrics.csv  2>/dev/null || echo "(no metrics.csv produced)"

# 7) Teardown. Artifacts live on the ./artifacts host bind-mount, so -v is safe.
if [ -z "${KEEP_UP:-}" ]; then
  log "teardown"
  for p in nemo guardrails llamaguard; do
    docker compose --profile "$p" down --remove-orphans >/dev/null 2>&1
  done
  docker compose down -v --remove-orphans >/dev/null 2>&1
fi
log "done"
