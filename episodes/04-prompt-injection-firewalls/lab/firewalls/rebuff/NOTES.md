# Rebuff wrapper — offline scope & confirm

Rebuff is a *layered* defense; offline we run the layers that don't need a cloud:

- **Heuristics** — always on (pattern/keyword scoring). `app.py` imports the
  heuristic detector defensively (its module path has moved across releases —
  confirm the import resolves on your pin; if not, update the tried paths).
- **Vector similarity** — off by default. To enable offline, stand up a local
  vector store (e.g., Chroma) seeded with known-attack embeddings and extend
  `score()` to add the vector sub-score. Document it if you turn it on.
- **LLM check** — stubbed unless `LLM_API_KEY` is set (keeps the lab egress-free).
- **Canary tokens** — Rebuff's signature trick is to plant a token in the prompt
  sent to the model and detect if the output leaks it. That needs the
  generate-with-canary flow, which is broader than this input-only `/classify`
  contract. The lab's *ground truth* for a leak is the canary **sink** receiving
  data (tracked by the app), and the wrapper additionally flags inputs that
  reference a canary-token pattern. Note this framing in the write-up.

Report what the run actually catches — do not assume heuristics-only Rebuff
matches full-stack Rebuff.
