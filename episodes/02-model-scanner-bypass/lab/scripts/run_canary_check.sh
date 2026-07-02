#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run_canary_check.sh — GROUND-TRUTH load step for the model-scanner lab.
#
# Loads each malicious variant (and each clean model) inside a container on the
# isolated labnet so its BENIGN canary payload fires against the canary sink,
# then reads the sink's request log to report which files actually executed code.
# A variant that FIRED but was called "safe" by a scanner is a genuine miss; a
# clean model that fires would be a builder bug.
#
# Each load runs with a distinct CANARY_URL path (/loaded/<label>) so the sink
# log distinguishes them. The sink is force-recreated first so the log is fresh.
#
# 100% local, no internet egress (labnet is internal:true). Run AFTER the lab is
# built at least once.  Usage:  bash scripts/run_canary_check.sh
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."   # lab/ root (where docker-compose.yml lives)

SINK_HOST="ep02-canary"
SINK_PORT="8080"

# Malicious variants (label:relative-path-under-/models) — each SHOULD fire.
VARIANTS=(
  "plain:plain.pkl"
  "deep_import:deep_import.pkl"
  "renamed:renamed.bin"
  "broken_archive:broken_archive.bin"
)
# Clean models — each should NOT fire.
CLEANS=(
  "clean_hyperparams:clean/clean_hyperparams.pkl"
  "clean_tokenizer:clean/clean_tokenizer.bin"
  "clean_weights:clean/clean_weights.pkl"
)

echo "[canary-check] ensuring models are built + sink has a fresh log..."
docker compose up -d model-builder >/dev/null 2>&1 || true   # (re)populate /models
docker compose up -d --force-recreate canary-sink >/dev/null # fresh, empty log
sleep 1

load_one() {  # <label> <relpath>
  local label="$1" rel="$2"
  docker compose run --rm -T \
    --entrypoint python \
    -e PYTHONPATH=/models \
    -e "CANARY_URL=http://${SINK_HOST}:${SINK_PORT}/loaded/${label}" \
    -v "$PWD/scripts:/scripts:ro" \
    model-builder /scripts/canary_loader.py "/models/${rel}" "${label}" \
    2>&1 | sed 's/^/  /'
}

echo "[canary-check] loading MALICIOUS variants (each should fire the canary)..."
for v in "${VARIANTS[@]}"; do load_one "${v%%:*}" "${v##*:}"; done
echo "[canary-check] loading CLEAN models (should NOT fire)..."
for c in "${CLEANS[@]}"; do load_one "${c%%:*}" "${c##*:}"; done

sleep 1
logs="$(docker compose logs --no-color canary-sink 2>/dev/null || true)"

echo ""
echo "[canary-check] ===================== GROUND TRUTH ====================="
rc=0
for v in "${VARIANTS[@]}"; do
  label="${v%%:*}"
  if grep -q "/loaded/${label}\b" <<<"$logs"; then
    printf "  FIRED    %-16s payload executed (a 'safe' verdict here = true miss)\n" "$label"
  else
    printf "  NO-HIT   %-16s canary did not log — check labnet/sink\n" "$label"
    rc=1
  fi
done
for c in "${CLEANS[@]}"; do
  label="${c%%:*}"
  if grep -q "/loaded/${label}\b" <<<"$logs"; then
    printf "  FIRED*   %-16s UNEXPECTED: a clean model executed code (builder bug)\n" "$label"
    rc=1
  else
    printf "  clean    %-16s no canary — correct\n" "$label"
  fi
done

echo ""
echo "[canary-check] request paths seen by the sink:"
grep -oE "/loaded/[A-Za-z0-9_]+" <<<"$logs" | sort | uniq -c | sed 's/^/  /' || true
echo "[canary-check] done (exit $rc)."
exit $rc
