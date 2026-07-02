# ---------------------------------------------------------------------------
# scanner-modelaudit — Promptfoo ModelAudit.
# Installs a pinned modelaudit and scans /models + /models/clean, writing SARIF
# to /artifacts/modelaudit.sarif (plus a JSON convenience copy). Pinned base +
# version for reproducibility.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Promptfoo ModelAudit ships as the PyPI package `modelaudit`.
RUN pip install --no-cache-dir "modelaudit==0.2.4"

WORKDIR /scan
COPY entrypoint.py /scan/entrypoint.py

ENTRYPOINT ["python", "/scan/entrypoint.py"]
