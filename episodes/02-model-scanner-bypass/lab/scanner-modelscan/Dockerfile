# ---------------------------------------------------------------------------
# scanner-modelscan — Protect AI ModelScan.
# Installs a pinned modelscan and scans /models + /models/clean, writing raw
# JSON per file to /artifacts/modelscan.json. Base image + version pinned.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Pinned current release of Protect AI ModelScan (PyPI package: modelscan).
RUN pip install --no-cache-dir "modelscan==0.8.5"

WORKDIR /scan
COPY entrypoint.py /scan/entrypoint.py

ENTRYPOINT ["python", "/scan/entrypoint.py"]
