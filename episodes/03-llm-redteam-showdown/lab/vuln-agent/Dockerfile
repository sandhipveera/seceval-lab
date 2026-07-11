# Deliberately vulnerable OpenAI-compatible agent (:8000).
# Network is used ONLY at build time (pip install). At run time it lives on
# labnet (internal:true): it talks to the mock-llm and the benign canary sink
# and has NO route to the internet.
FROM python:3.12-slim

WORKDIR /app

# --- build-time only: install pinned deps -----------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

# Weak defaults; docker-compose overrides these for A/B baselining.
ENV MODE="stub" \
    SYSTEM_PROMPT="weak" \
    TOOL_ALLOWLIST=""

CMD ["python", "app.py"]
