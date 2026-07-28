# NeMo Guardrails in front of the shared target, as an input/output filter proxy.
# Models are BAKED at build (build has network; runtime labnet is no-egress). At runtime we force
# HF offline so nothing tries to phone home.
FROM python:3.11-slim

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1

# nemoguardrails pulls `annoy`, which ships no wheel and compiles from source — needs a C++
# toolchain that python:3.11-slim lacks. Install build tools first (build fix, Ep.05 run).
RUN apt-get update && apt-get install -y --no-install-recommends g++ gcc \
    && rm -rf /var/lib/apt/lists/*

# Pin the framework + its perplexity backend for the jailbreak-detection heuristics.
# NeMo Guardrails 0.21.x (May 2026 line per storyboard). transformers/torch power the offline
# gpt2 perplexity check used by the length/prefix-suffix heuristics.
RUN pip install \
    "nemoguardrails==0.21.0" \
    "transformers==4.44.2" \
    "torch==2.2.2" \
    "numpy<2" \
    "flask==3.0.3" \
    "requests==2.32.3"
# numpy<2: torch 2.2.2 was built against numpy 1.x; a numpy 2.x pulled in transitively makes the
# perplexity heuristic throw "Numpy is not available" (torch tensor->numpy), silently defeating the
# jailbreak rail. Pinning numpy 1.x keeps the perplexity check genuinely live (Ep.05 finding).

# --- Bake models at build so runtime needs no egress -----------------------------------------
# NeMo 0.21's jailbreak perplexity heuristic (heuristics/checks.py) loads **gpt2-large** at import,
# not plain gpt2 — so gpt2-large is what must be in the offline cache or the whole perplexity rail
# silently defers (Ep.05 finding). Bake both the tokenizer and the LM head for gpt2-large.
RUN python - <<'PY'
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
GPT2TokenizerFast.from_pretrained("gpt2-large")
GPT2LMHeadModel.from_pretrained("gpt2-large")
print("baked gpt2-large for NeMo perplexity heuristic")
PY

COPY config/ /app/config/
COPY app.py /app/app.py

# Force offline at runtime.
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CONFIG=/app/config
EXPOSE 8080
CMD ["python", "/app/app.py"]
