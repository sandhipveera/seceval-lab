# Meta Llama Guard 4 in front of the shared target, as a safety-classifier proxy.
# Llama Guard is a GATED Meta model: you must accept its license on Hugging Face AND pass an
# HF token at build. Model is baked at build (build has network); runtime is offline (no egress).
#
# Feasibility note: Llama-Guard-4-12B is large (~24GB fp16) and slow on CPU. For a laptop run,
# override LLAMAGUARD_MODEL to a smaller family member (e.g. meta-llama/Llama-Guard-3-1B) — the
# proxy logic is identical. See NOTES.md.
FROM python:3.11-slim

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1

# transformers >= 4.51 is required for the Llama4 architecture used by Llama Guard 4.
RUN pip install \
    "transformers==4.51.3" \
    "torch==2.2.2" \
    "accelerate==0.34.2" \
    "huggingface_hub==0.25.2" \
    "flask==3.0.3" \
    "requests==2.32.3"

ARG HF_TOKEN=""
ARG LLAMAGUARD_MODEL="meta-llama/Llama-Guard-4-12B"
ENV LLAMAGUARD_MODEL=${LLAMAGUARD_MODEL}

# Fail fast with a clear message if the gated model can't be fetched (mirrors Ep.04 Prompt Guard 2).
RUN if [ -z "$HF_TOKEN" ]; then \
      echo "ERROR: HF_TOKEN build-arg is empty. Llama Guard is gated: accept the license at" \
           "https://huggingface.co/${LLAMAGUARD_MODEL} and rebuild with" \
           "--build-arg HF_TOKEN=hf_xxx  (see NOTES.md)"; exit 1; fi

# Bake the model at build so runtime needs no egress. Try the Llama Guard 4 (multimodal) loader
# first, then fall back to the text-only causal loader for smaller Llama Guard 3 variants.
RUN python - <<PY
import os
tok = os.environ.get("HF_TOKEN")
model = os.environ.get("LLAMAGUARD_MODEL")
from huggingface_hub import login; login(token=tok)
ok = False
try:
    from transformers import AutoProcessor, AutoModelForImageTextToText
    AutoProcessor.from_pretrained(model)
    AutoModelForImageTextToText.from_pretrained(model, torch_dtype="auto")
    print("baked", model, "(image-text-to-text / Llama Guard 4)"); ok = True
except Exception as e:
    print("multimodal load failed:", e)
if not ok:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    AutoTokenizer.from_pretrained(model)
    AutoModelForCausalLM.from_pretrained(model, torch_dtype="auto")
    print("baked", model, "(causal LM / Llama Guard 3)")
PY

COPY app.py /app/app.py
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
EXPOSE 8080
CMD ["python", "/app/app.py"]
