# Vigil wrapper — NOT EVALUATED in Ep.04 (documented, not guessed)

**Outcome:** vigil could not be stood up in a clean, offline Docker container within
this lab's constraints. It is reported in the write-up as **not evaluated**, with the
reasons below. We did **not** publish catch/miss numbers for it — a guard that never
starts is not a guard that "missed."

## What we actually hit, in order (each fix revealed the next)

1. **Build dir was never scaffolded.** The Dockerfile `COPY`d `conf/` and
   `signatures/`, neither of which existed →
   `failed to compute cache key: "/signatures": not found`

2. **YARA missing as a system library.** Vigil's docs pin YARA v4.3.2; the image only
   installed `git` + `build-essential`. Fixed by installing `yara` + `libyara-dev`.

3. **Install path wrong.** `requirements.txt` referenced the unpinned PyPI name
   `vigil-llm`; upstream expects clone + `pip install -e .`. Fixed.

4. **sentence-transformers ↔ huggingface_hub conflict.**
   `ImportError: cannot import name 'cached_download' from 'huggingface_hub'`
   vigil pins sentence-transformers 2.2.x, which imports `cached_download` — removed
   in huggingface_hub >= 0.26. Worked around by upgrading sentence-transformers.

5. **nltk `vader_lexicon` fetched at import.** The sentiment scanner downloads it on
   import; labnet has no runtime egress. Worked around by baking it at build.

6. **VectorDB constructed unconditionally — BLOCKER.**
   ```
   Vigil.__init__ -> _initialize_vectordb() -> VectorDB(**params)
   TypeError: VectorDB.__init__() missing 3 required positional arguments:
              'collection', 'db_dir', and 'n_results'
   ```
   `Vigil.__init__` builds a VectorDB even when `vectordb` is **not** in
   `input_scanners`. Adding a fully-populated `[scanner:vectordb]` section
   (collection / db_dir / n_results / threshold) plus a writable `db_dir` did **not**
   resolve it — on the pinned `main`, those params still don't reach the constructor.

## Why we stopped
Three attempts, agreed timebox. Going further appears to need either a Chroma vector DB
seeded with embeddings matching the configured embedding model (not producible offline
here), or a specific historical SHA whose config contract matches its own docs.

## If someone wants to finish it
- Pin `VIGIL_REF` to a release SHA whose `vigil/core/config.py` contract matches the
  documented `[scanner:vectordb]` keys, rather than `main`.
- Read `vigil/vigil.py::_initialize_vectordb` on that pin to see exactly which config
  keys it forwards into `VectorDB(**params)`.
- Seed the vector DB via `loader.py` against a bundled dataset, with the embedding
  model matching the one that generated those embeddings.

**Reporting rule:** report what actually ran. Never invent numbers for a guard that
never started — a broken container and a missed attack look identical in the output,
and only one of them is a finding.
