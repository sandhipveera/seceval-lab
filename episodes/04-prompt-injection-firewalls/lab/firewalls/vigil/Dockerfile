# deadbits/vigil-llm firewall — EP04 lab.
#
# Real-run findings that shaped this file:
#  * Vigil requires YARA as a SYSTEM library (docs pin v4.3.2). Without libyara
#    the package import fails — the first cut never installed it.
#  * Upstream install is "clone + pip install -e .", not the unpinned `vigil-llm`
#    PyPI name.
#  * Config schema per https://vigil.deadbits.ai/overview/use-vigil/configuration.
#    We run a reduced TRANSFORMER + YARA scanner set; vectordb is disabled because
#    it needs a seeded Chroma DB whose embeddings match the embedding model, which
#    can't be produced offline here. Reported as a weaker config, not faked.
FROM python:3.11-slim
WORKDIR /app

# System deps: YARA (+ headers so yara-python can build), git, toolchain.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential automake libtool make gcc pkg-config \
      libssl-dev libmagic-dev yara libyara-dev \
 && rm -rf /var/lib/apt/lists/*

# Clone + install vigil from source. Pin VIGIL_REF to a known-good SHA once one
# is confirmed (packaging has drifted across releases — see NOTES.md).
ARG VIGIL_REF=main
RUN git clone https://github.com/deadbits/vigil-llm.git /opt/vigil-llm \
 && cd /opt/vigil-llm \
 && git checkout "${VIGIL_REF}" \
 && pip install --no-cache-dir -e .

# --- Dependency conflicts found on the real run -------------------------------
# 1) vigil pins sentence-transformers 2.2.x, which does
#      `from huggingface_hub import cached_download`
#    That symbol was REMOVED in huggingface_hub >= 0.26, so importing vigil dies with
#      ImportError: cannot import name 'cached_download' from 'huggingface_hub'
#    Upgrade sentence-transformers to a line that uses the modern hub API instead of
#    pinning the hub backwards (transformers needs the newer hub).
RUN pip install --no-cache-dir -U "sentence-transformers>=2.7,<4"

# 2) vigil's sentiment scanner pulls nltk's vader_lexicon at IMPORT time. labnet has
#    no egress at runtime, so bake it into the image now.
ENV NLTK_DATA=/usr/local/share/nltk_data
RUN python -m nltk.downloader -d /usr/local/share/nltk_data vader_lexicon
# ------------------------------------------------------------------------------

# Wrapper deps (flask).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Our reduced config (transformer + yara; YARA rules come from the repo clone).
COPY conf/ /app/conf/

# Vigil always constructs a VectorDB at startup even with the scanner disabled,
# so give Chroma a writable dir to create its (empty, unused) store in.
RUN mkdir -p /app/data/vdb

# Bake models at BUILD so runtime needs no network (labnet has no egress).
RUN python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification as M; m='deepset/deberta-v3-base-injection'; AutoTokenizer.from_pretrained(m); M.from_pretrained(m)"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || \
    echo "NOTE: sentence-transformers embed model not baked (only needed if vectordb is enabled)"

ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 VIGIL_CONF=/app/conf/server.conf
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
