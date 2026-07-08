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

# Authenticate (if a token was passed) and pre-download the weights into the image.
RUN if [ -n "$HF_TOKEN" ]; then python -c "from huggingface_hub import login; login('$HF_TOKEN')"; fi \
 && python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification as M; import os; m=os.environ['MODEL_ID']; AutoTokenizer.from_pretrained(m); M.from_pretrained(m)"

# Lock the container to offline model loading at runtime (no network pull).
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
