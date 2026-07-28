#!/usr/bin/env bash
# Bring up target (host-published) + MPS proxy, leave them running, and run the ground-truth probe.
# Proxy forwards via 127.0.0.1 (not localhost) to rule out the ::1 vs 127.0.0.1 mismatch.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; LAB="$(cd "$HERE/.." && pwd)"; PY="$HERE/.venv/bin/python"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTORCH_ENABLE_MPS_FALLBACK=1

( cd "$LAB" && docker compose -f docker-compose.yml -f host-llamaguard/docker-compose.hostguard.yml up -d --build --wait target-chatbot ) || exit 1
echo "target up; direct health: $(curl -fsS -m5 http://127.0.0.1:8080/health)"

# (re)start proxy
pkill -f app_host.py 2>/dev/null; sleep 1
UPSTREAM="http://127.0.0.1:8080/chat" PORT=8091 CANARY="CANARY-LAB-5-9F3A" \
  nohup "$PY" "$HERE/app_host.py" > "$HERE/proxy.log" 2>&1 &
echo "proxy starting (pid $!)"
for i in $(seq 1 60); do
  case "$(curl -fsS -m3 http://127.0.0.1:8091/health 2>/dev/null)" in
    *'"status":"ok"'*) echo "proxy healthy"; break;; esac
  sleep 3
done
echo "===== DIAGNOSE ====="
"$PY" "$HERE/diagnose.py"
