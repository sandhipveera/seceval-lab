# NeMo Guardrails in front of the shared target, as an input/output filter proxy.
# Models are BAKED at build (build has network; runtime labnet is no-egress). At runtime we force
# HF offline so nothing tries to phone home.
FROM python:3.11-slim

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1

# Pin the framework + its perplexity backend for the jailbreak-detection heuristics.
# NeMo Guardrails 0.21.x (May 2026 line per storyboard). transformers/torch power the offline
# gpt2 perplexity check used by the length/prefix-suffix heuristics.
RUN pip install \
    "nemoguardrails==0.21.0" \
    "transformers==4.44.2" \
    "torch==2.2.2" \
    "flask==3.0.3" \
    "requests==2.32.3"

# --- Bake models at build so runtime needs no egress -----------------------------------------
# gpt2 for the jailbreak perplexity heuristic. If the pinned NeMo version changes the heuristic
# backend, update this bake step to match (see NOTES.md).
RUN python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
AutoTokenizer.from_pretrained("gpt2")
AutoModelForCausalLM.from_pretrained("gpt2")
print("baked gpt2 for perplexity heuristic")
PY

COPY config/ /app/config/
COPY app.py /app/app.py

# Force offline at runtime.
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CONFIG=/app/config
EXPOSE 8080
CMD ["python", "/app/app.py"]
