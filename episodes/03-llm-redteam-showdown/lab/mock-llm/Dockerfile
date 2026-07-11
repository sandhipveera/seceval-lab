# Deterministic OpenAI-compatible mock LLM backend (:9000).
# Network is used ONLY at build time (pip install). At run time the container
# lives on labnet (internal:true) and never egresses.
FROM python:3.12-slim

WORKDIR /app

# --- build-time only: install pinned deps -----------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 9000

ENV PERSONA="over-helpful-weak-guardrails"

# Single-worker Flask dev server is fine: this is a deterministic lab mock.
CMD ["python", "app.py"]
