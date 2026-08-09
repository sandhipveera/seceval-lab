#!/usr/bin/env bash
# Per-gateway performance metrics under identical load (LOAD_REQUESTS / LOAD_CONCURRENCY, same
# knobs the runner uses). Measures the BASELINE (no gateway) first so "added latency" is a real
# subtraction, then sweeps guardrails=off and guardrails=on for each gateway, because the honest
# number is the cost of the PROTECTION, not the cost of the proxy. Writes artifacts/metrics.csv
# with columns: gateway,guardrails,added_latency_p50_ms,added_latency_p95_ms,throughput_rps,
# mem_mb,cpu_pct
#
# Independent of scripts/run_gateway.sh (its own up/measure/down cycle), same pattern as Ep.05's
# capture_metrics.sh. Load generation runs INSIDE the `runner` container (via `docker compose
# run`), the same way Ep.05 drove its probes through `attack-runner` -- victim-app has no host
# port mapping in docker-compose.yml (labnet is internal-only), so this has to run from a
# container already on that network rather than from the host.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p artifacts
OUT=artifacts/metrics.csv
echo "gateway,guardrails,added_latency_p50_ms,added_latency_p95_ms,throughput_rps,mem_mb,cpu_pct" > "$OUT"

export LOAD_REQUESTS="${LOAD_REQUESTS:-200}"
export LOAD_CONCURRENCY="${LOAD_CONCURRENCY:-10}"

# Runs inside the runner container's network (labnet). Prints one line: "p50_ms p95_ms rps" or
# "ERROR ERROR ERROR" if every request failed (never silently treated as a fast/zero result).
LOADGEN_PY='
import concurrent.futures, os, time, requests
url = os.environ.get("VICTIM_URL", "http://ep06-victim-app:8080") + "/chat"
n = int(os.environ.get("LOAD_REQUESTS", "200"))
c = int(os.environ.get("LOAD_CONCURRENCY", "10"))
payload = {"message": "What time zone are your support hours in?"}
def one(_):
    t0 = time.perf_counter()
    try:
        requests.post(url, json=payload, timeout=30)
        return time.perf_counter() - t0
    except Exception:
        return None
t_wall0 = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=c) as ex:
    samples = list(ex.map(one, range(n)))
wall = time.perf_counter() - t_wall0
ok = sorted(s for s in samples if s is not None)
if not ok:
    print("ERROR ERROR ERROR")
else:
    def pct(p):
        idx = min(len(ok) - 1, int(round(p * (len(ok) - 1))))
        return round(ok[idx] * 1000.0, 1)
    rps = round(len(ok) / wall, 2) if wall > 0 else 0
    print(f"{pct(0.50)} {pct(0.95)} {rps}")
'

load_and_measure() {
  docker compose --profile run run --rm -T runner python3 -c "$LOADGEN_PY" 2>/dev/null | tail -1
}

sample_container() {  # $1 = container name, $2 = seconds; prints "mem_mb cpu_pct" (or ERROR ERROR)
  local CONT="$1" SECS="$2"
  local MEMS=() CPUS=()
  local N=$((SECS * 4))
  for _ in $(seq 1 "$N"); do
    local LINE
    # MemUsage renders as "<used> / <limit>" then CPUPerc, so the fields are:
    #   $1=used(with unit)  $2=/  $3=limit  $4=cpu%   -- CPU is $4, NOT $3 (which is the mem limit).
    LINE=$(docker stats --no-stream --format '{{.MemUsage}} {{.CPUPerc}}' "$CONT" 2>/dev/null || echo "")
    if [ -n "$LINE" ]; then
      MEMS+=("$(echo "$LINE" | awk '{print $1}')")            # keep the unit; normalized to MB below
      CPUS+=("$(echo "$LINE" | awk '{print $4}' | tr -d '%')")
    fi
    sleep 0.25
  done
  if [ "${#MEMS[@]}" -eq 0 ]; then echo "ERROR ERROR"; return; fi
  local PEAK_MEM AVG_CPU
  # Peak used-memory in MB, unit-aware (MiB/GiB/KiB/MB/GB/kB) so a >1GiB gateway isn't mis-ranked.
  PEAK_MEM=$(printf '%s\n' "${MEMS[@]}" | python3 -c "
import sys, re
def mb(tok):
    m = re.match(r'([0-9.]+)\s*([A-Za-z]+)', tok.strip())
    if not m: return None
    v, u = float(m.group(1)), m.group(2).lower()
    f = {'kib':1/1024,'mib':1,'gib':1024,'kb':0.001,'mb':1,'gb':1000,'b':1/1048576}.get(u, 1)
    return v*f
vals=[mb(x) for x in sys.stdin if x.strip()]; vals=[x for x in vals if x is not None]
print(round(max(vals),1) if vals else 'ERROR')")
  AVG_CPU=$(printf '%s\n' "${CPUS[@]}" | python3 -c "import sys; v=[float(x) for x in sys.stdin if x.strip()]; print(round(sum(v)/len(v),1) if v else 'ERROR')")
  echo "$PEAK_MEM $AVG_CPU"
}

echo "== baseline: no gateway =="
docker compose --profile litellm --profile portkey --profile bifrost --profile run down -v --remove-orphans >/dev/null 2>&1 || true
docker compose up -d --build --wait stub-model doc-server canary-sink victim-app >/dev/null 2>&1 || {
  echo "!! baseline did not come up healthy" >&2; exit 1; }

read -r BASE_P50 BASE_P95 BASE_RPS <<< "$(load_and_measure)"
if [ "$BASE_P50" = "ERROR" ]; then
  echo "!! baseline load generation failed -- every request errored; check victim-app/stub-model logs" >&2
  echo "none,n/a,ERROR,ERROR,ERROR,," >> "$OUT"
else
  echo "none,n/a,0,0,$BASE_RPS,," >> "$OUT"   # baseline row: added latency is 0 by definition; no
                                                # gateway container exists to sample mem/cpu for
  echo "baseline p50=${BASE_P50}ms p95=${BASE_P95}ms throughput=${BASE_RPS}rps"
fi

measure_gateway() {  # $1 = litellm|portkey|bifrost, $2 = base_url, $3 = container, $4 = guardrails
  local GW="$1" BASE_URL="$2" CONT="$3" GUARDRAILS="$4"
  export GATEWAY_BASE_URL="$BASE_URL"
  export GATEWAY_UNDER_TEST="$GW"
  export GUARDRAILS="$GUARDRAILS"
  # Same per-gateway client config as run_gateway.sh, so the load actually reaches the model:
  # LiteLLM needs the master key; Portkey needs its per-request config header set.
  if [ "$GW" = "litellm" ]; then export VICTIM_OPENAI_KEY="sk-lab-master-not-real"; else export VICTIM_OPENAI_KEY="sk-lab-not-a-real-key"; fi
  if [ "$GW" = "portkey" ]; then export OPENAI_EXTRA_HEADERS="$(cat gateways/portkey/headers.$GUARDRAILS.json)"; else export OPENAI_EXTRA_HEADERS=""; fi
  docker compose --profile "$GW" up -d --build --wait \
    stub-model doc-server canary-sink victim-app "$GW" >/dev/null 2>&1 || {
    echo "$GW,$GUARDRAILS,ERROR,ERROR,ERROR,ERROR,ERROR" >> "$OUT"; return; }

  sample_container "$CONT" 10 > /tmp/ep06_sample_"$GW"_"$GUARDRAILS".txt &
  local SAMPLER=$!
  read -r P50 P95 RPS <<< "$(load_and_measure)"
  wait "$SAMPLER" 2>/dev/null || true
  read -r MEM CPU < /tmp/ep06_sample_"$GW"_"$GUARDRAILS".txt
  rm -f /tmp/ep06_sample_"$GW"_"$GUARDRAILS".txt

  if [ "$P50" = "ERROR" ] || [ "$BASE_P50" = "ERROR" ]; then
    echo "$GW,$GUARDRAILS,ERROR,ERROR,${RPS:-ERROR},${MEM:-ERROR},${CPU:-ERROR}" >> "$OUT"
    return
  fi
  local ADD50 ADD95
  ADD50=$(python3 -c "print(round(${P50}-${BASE_P50},1))")
  ADD95=$(python3 -c "print(round(${P95}-${BASE_P95},1))")
  echo "$GW,$GUARDRAILS,$ADD50,$ADD95,$RPS,${MEM:-ERROR},${CPU:-ERROR}" >> "$OUT"
}

for GUARDRAILS in off on; do
  measure_gateway litellm "http://ep06-gw-litellm:4000/v1" ep06-gw-litellm "$GUARDRAILS"
  measure_gateway portkey "http://ep06-gw-portkey:8787/v1" ep06-gw-portkey "$GUARDRAILS"
  measure_gateway bifrost "http://ep06-gw-bifrost:8080/v1" ep06-gw-bifrost "$GUARDRAILS"
done

docker compose --profile litellm --profile portkey --profile bifrost --profile run \
  down --remove-orphans >/dev/null 2>&1 || true
echo "wrote $OUT"; cat "$OUT"
