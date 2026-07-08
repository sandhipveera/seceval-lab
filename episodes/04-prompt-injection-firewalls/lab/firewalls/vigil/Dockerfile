# deadbits/vigil-llm firewall. Models baked + local vector DB seeded at build for offline runtime.
# NOTE: vigil's packaging/config path has drifted across versions — see NOTES.md. Pin a known-good
# commit and confirm the config + seed steps before publishing.
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bundled config + known-attack signatures (offline seed source).
COPY conf/ /app/conf/
COPY signatures/ /app/signatures/

# Bake the transformer + embedding models and seed the local vector DB from the
# bundled signatures so runtime needs no network. CONFIRM these entrypoints
# against your vigil pin (module paths for the seeder have changed across releases).
RUN python -m vigil.utils.seed --config /app/conf/server.conf --input /app/signatures || \
    echo "WARN: adjust the vigil seed command for your pin (see NOTES.md)"

ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 VIGIL_CONF=/app/conf/server.conf
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
