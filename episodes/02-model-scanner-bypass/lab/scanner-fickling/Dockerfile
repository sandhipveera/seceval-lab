# ---------------------------------------------------------------------------
# scanner-fickling — Trail of Bits fickling (allowlist philosophy).
# Installs a pinned fickling and runs its pickle scanner in allowlist mode over
# /models + /models/clean, writing raw JSON to /artifacts/fickling.json.
# Pinned base image + tool version for reproducibility.
# ---------------------------------------------------------------------------
# NOTE: fickling 0.1.3 imports the stdlib `distutils`, which was REMOVED in
# Python 3.12. Pin this scanner to 3.11 (distutils still present) so it runs.
FROM python:3.11-slim

# Trail of Bits fickling (PyPI package: fickling).
# setuptools<81 also vendors a distutils shim as a belt-and-suspenders fallback.
RUN pip install --no-cache-dir "setuptools<81" "fickling==0.1.3"

WORKDIR /scan
COPY entrypoint.py /scan/entrypoint.py

ENTRYPOINT ["python", "/scan/entrypoint.py"]
