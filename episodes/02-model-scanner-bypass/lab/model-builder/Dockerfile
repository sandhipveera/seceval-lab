# ---------------------------------------------------------------------------
# model-builder — emits ONE base pickle-based "malicious" model plus evasive
# variants (plain, deep_import, renamed, broken_archive) and a clean/ set into
# the shared /models volume.
#
# SAFETY: every emitted file carries only a BENIGN canary payload. On unpickle
# it performs a single HTTP GET to ${CANARY_URL} (an in-network echo sink) and
# nothing else. No shell, no reverse shell, no real exploit, no secrets. See the
# large header comment in build_models.py.
#
# Deterministic: pinned base image, no pip installs (stdlib only), fixed content.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# No third-party deps: the builder uses only the Python standard library
# (pickle, pickletools, zipfile, struct, urllib) so the image is reproducible.

WORKDIR /build
COPY build_models.py /build/build_models.py

# CANARY_URL and VARIANTS are provided by docker-compose at run time.
ENTRYPOINT ["python", "/build/build_models.py"]
