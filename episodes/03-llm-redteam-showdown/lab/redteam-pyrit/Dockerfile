# PyRIT red-team runner. Network is used ONLY at build time (pip install pyrit).
# At run time it lives on labnet (internal:true) and only reaches the vuln-agent.
FROM python:3.12-slim

WORKDIR /app

# --- build-time only: install a PINNED PyRIT --------------------------------
# pip runs at BUILD time ONLY; at run time the container has no egress.
# Pinned to PyRIT 0.14.0 (the API the entrypoint targets: OpenAIChatTarget,
# SubStringScorer, PromptSendingAttack, AttackScoringConfig, initialize_pyrit_async).
# httpx is used by the entrypoint's benign fallback driver / verdict re-probe.
RUN pip install --no-cache-dir "pyrit==0.14.0" "httpx==0.27.2"

COPY entrypoint.py .

ENTRYPOINT ["python", "entrypoint.py"]
