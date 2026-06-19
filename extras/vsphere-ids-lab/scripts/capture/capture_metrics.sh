#!/usr/bin/env bash
# Sample CPU/RAM/disk of the product-under-test containers during a test run -> CSV.
# Usage: capture_metrics.sh <run_id> [duration_s] [interval_s]
source "$(dirname "$0")/../lib/common.sh"
require docker
RUN_ID="${1:-$(run_id)}"; DUR="${2:-120}"; INT="${3:-2}"
OUT="$REPO_ROOT/artifacts/$RUN_ID"; mkdir -p "$OUT"
CSV="$OUT/metrics.csv"
echo "timestamp,container,cpu_pct,mem_used_mb,mem_pct" > "$CSV"
log "sampling docker stats for ${DUR}s every ${INT}s -> $CSV"
end=$(( $(date +%s) + DUR ))
while [ "$(date +%s)" -lt "$end" ]; do
  ts=$(date -Is)
  docker stats --no-stream --format '{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}' \
    | sed 's/%//g' \
    | awk -F, -v ts="$ts" '{gsub(/[^0-9.].*/,"",$3); print ts","$1","$2","$3","$4}' >> "$CSV"
  sleep "$INT"
done
log "metrics written: $CSV"
