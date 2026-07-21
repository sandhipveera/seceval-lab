# Guardrails AI in front of the shared target, as an input/output validator proxy.
# Hub validators (detect_jailbreak, detect_prompt_injection) pull HF models; we install them AND
# bake their models at BUILD time (build has network), then force offline at runtime (no egress).
FROM python:3.11-slim

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

RUN pip install \
    "guardrails-ai==0.6.5" \
    "transformers==4.44.2" \
    "torch==2.2.2" \
    "flask==3.0.3" \
    "requests==2.32.3"

# Guardrails Hub needs a token to install validators. Pass at build:
#   docker compose build --build-arg GUARDRAILS_TOKEN=xxxx guard-guardrails
# The token is only used during build; it is NOT baked into the runtime image layers we run.
ARG GUARDRAILS_TOKEN=""
RUN if [ -n "$GUARDRAILS_TOKEN" ]; then \
      guardrails configure --token "$GUARDRAILS_TOKEN" --disable-metrics --disable-remote-inferencing || true ; \
      guardrails hub install hub://guardrails/detect_jailbreak || true ; \
      guardrails hub install hub://guardrails/detect_prompt_injection || true ; \
    else echo "WARN: no GUARDRAILS_TOKEN; validators not installed (see NOTES.md)"; fi

# Bake validator models so runtime needs no egress. Best-effort: if a validator ships a HF model,
# instantiating it here downloads and caches it.
RUN python - <<'PY'
try:
    from guardrails.hub import DetectJailbreak
    DetectJailbreak(on_fail="noop")
    print("baked detect_jailbreak model")
except Exception as e:
    print("detect_jailbreak bake skipped:", e)
try:
    from guardrails.hub import DetectPromptInjection
    DetectPromptInjection(on_fail="noop")
    print("baked detect_prompt_injection model")
except Exception as e:
    print("detect_prompt_injection bake skipped:", e)
PY

COPY app.py /app/app.py
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 VALIDATORS=detect-jailbreak,detect-prompt-injection
EXPOSE 8080
CMD ["python", "/app/app.py"]
