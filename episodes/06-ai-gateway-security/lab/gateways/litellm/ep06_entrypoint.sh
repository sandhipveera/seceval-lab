#!/bin/sh
# Ep.06 lab — pick the LiteLLM config by the GUARDRAILS knob, then hand off to the REAL upstream
# entrypoint. run_gateway.sh brings the container up fresh for each GUARDRAILS value, so selecting a
# config at start (rather than a live reload) is sufficient and keeps each run's state clean.
set -e
if [ "${GUARDRAILS:-on}" = "on" ]; then
  CFG=/app/config.on.yaml
else
  CFG=/app/config.off.yaml
fi
echo "[ep06] litellm starting: GUARDRAILS=${GUARDRAILS:-on} config=$CFG"
exec /app/docker/prod_entrypoint.sh --config "$CFG" --port 4000
