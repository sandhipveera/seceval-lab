# ---------------------------------------------------------------------------
# scanner-picklescan — Trail-of-scope: picklescan (blocklist philosophy).
# Installs a pinned, current picklescan (>= 0.0.31) and scans every model file
# in /models + /models/clean, writing raw JSON to /artifacts/picklescan.json.
# Base image + tool version pinned for reproducibility.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# Pinned recent release (satisfies the >=0.0.31 contract requirement).
RUN pip install --no-cache-dir "picklescan==0.0.31"

WORKDIR /scan
COPY entrypoint.py /scan/entrypoint.py

ENTRYPOINT ["python", "/scan/entrypoint.py"]
