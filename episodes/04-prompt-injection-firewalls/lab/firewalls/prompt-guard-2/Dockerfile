# Meta Llama Prompt Guard 2 firewall — weights baked at BUILD time for offline runtime.
#
# LICENSE: Llama Prompt Guard 2 is distributed under the Llama Community License and
# the model repo is GATED on Hugging Face. Before building/publishing you must (1)
# accept the license on the model page and (2) provide an HF token at build time:
#     docker build --build-arg HF_TOKEN=hf_xxx ./firewalls/prompt-guard-2
# Review and honor the license terms. See LICENSE_NOTE.md.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG MODEL_ID=meta-llama/Llama-Prompt-Guard-2-86M
ENV MODEL_ID=${MODEL_ID}
ARG HF_TOKEN=""

# Fail fast with a readable message instead of a wall of HF traceback when no token
# is supplied. Llama Prompt Guard 2 is GATED: the Llama license must be accepted on
# the model page AND the approval granted before any token works.
RUN if [ -z "$HF_TOKEN" ]; then \
      echo "=========================================================="; \
      echo "ERROR: HF_TOKEN build-arg is empty."; \
      echo "Llama Prompt Guard 2 is a GATED Meta model. You must:"; \
      echo "  1. Accept the Llama license at"; \
      echo "     https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M"; \
      echo "  2. WAIT for the gate request to be APPROVED (not just submitted)"; \
      echo "  3. Re-run:  HF_TOKEN=hf_xxx ./scripts/run_firewall.sh prompt-guard-2"; \
      echo "A 401/GatedRepoError with a valid token means approval is still pending."; \
      echo "=========================================================="; \
      exit 1; \
    fi

# Authenticate (if a token was passed) and pre-download the weights into the image.
RUN if [ -n "$HF_TOKEN" ]; then python -c "from huggingface_hub import login; login('$HF_TOKEN')"; fi \
 && python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification as M; import os; m=os.environ['MODEL_ID']; AutoTokenizer.from_pretrained(m); M.from_pretrained(m)"

# Lock the container to offline model loading at runtime (no network pull).
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
