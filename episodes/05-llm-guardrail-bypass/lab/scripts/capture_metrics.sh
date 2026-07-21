#!/usr/bin/env bash
# Per-guard metrics: added latency vs the raw target, peak memory under the benign load, and
# false positives on the benign prompt set. Writes artifacts/metrics.csv.
# Runs each guard on its own (up -> measure -> down), so it is independent of the run_*.sh scripts.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p artifacts
OUT=artifacts/metrics.csv
echo "guardrail,baseline_latency_ms,guard_latency_ms,added_latency_ms,peak_mem_mb,false_positives,benign_total" > "$OUT"

# Baseline latency straight at the target (no guard).
docker compose up -d --build --wait target-chatbot attack-runner >/dev/null 2>&1 || true
BASE=$(docker compose exec -T -e HIT_URL="http://ep05-target:8080/chat" attack-runner python /app/fp_probe.py)
BASE_LAT=$(echo "$BASE" | python3 -c "import sys,json;print(json.load(sys.stdin)['avg_latency_ms'])")

measure () {   # $1 = profile/label, $2 = guard container, $3 = guard url
  local NAME="$1" CONT="$2" URL="$3"
  docker compose --profile "$NAME" up -d --build --wait target-chatbot "$CONT" attack-runner >/dev/null 2>&1 || {
    echo "$NAME,,,,,ERROR,ERROR" >> "$OUT"; docker compose --profile "$NAME" down --remove-orphans >/dev/null 2>&1; return; }

  # Sample peak memory of the guard while the benign probe runs.
  local PEAK=0
  ( for _ in $(seq 1 40); do
      MB=$(docker stats --no-stream --format '{{.MemUsage}}' "$CONT" 2>/dev/null | awk '{print $1}' | sed 's/[A-Za-z]//g')
      echo "$MB"; sleep 0.25
    done > /tmp/ep05_mem_$NAME.txt ) &
  local SAMPLER=$!

  # fp_probe runs in the attack-runner, pointed at the guard URL.
  local RES; RES=$(docker compose exec -T -e HIT_URL="$URL" attack-runner python /app/fp_probe.py 2>/dev/null)
  wait $SAMPLER 2>/dev/null || true
  PEAK=$(sort -n /tmp/ep05_mem_$NAME.txt 2>/dev/null | tail -1)

  local GLAT FP TOT
  GLAT=$(echo "$RES" | python3 -c "import sys,json;print(json.load(sys.stdin)['avg_latency_ms'])" 2>/dev/null || echo "")
  FP=$(echo "$RES"  | python3 -c "import sys,json;print(json.load(sys.stdin)['blocked'])" 2>/dev/null || echo "")
  TOT=$(echo "$RES" | python3 -c "import sys,json;print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "")
  local ADD; ADD=$(python3 -c "print(round(float('${GLAT:-0}')-float('${BASE_LAT:-0}'),1))" 2>/dev/null || echo "")
  echo "$NAME,$BASE_LAT,$GLAT,$ADD,${PEAK:-},$FP,$TOT" >> "$OUT"
  docker compose --profile "$NAME" down --remove-orphans >/dev/null 2>&1
}

measure nemo       ep05-guard-nemo        "http://ep05-guard-nemo:8080/chat"
measure guardrails ep05-guard-guardrails  "http://ep05-guard-guardrails:8080/chat"

docker compose down --remove-orphans >/dev/null 2>&1 || true
echo "wrote $OUT"; cat "$OUT"
