# Garak red-team runner. Network is used ONLY at build time (pip install garak).
# At run time it lives on labnet (internal:true) and only reaches the vuln-agent.
FROM python:3.12-slim

WORKDIR /app

# --- build-time only: install a PINNED garak -------------------------------
# garak 0.15.0 (released 2026-05-01) — the release that shipped the multi-turn
# GOAT probe and the Agent-breaker probe this episode relies on.
RUN pip install --no-cache-dir "garak==0.15.0"

# --- PRE-CACHE detector + probe-generator models at BUILD time ---------------
# garak's model-backed detectors (e.g. unsafe_content.ToxicCommentModel ->
# garak-llm/roberta_toxicity_classifier) and generative probes (atkgen) pull HF
# weights AND datasets on first use. We warm the caches at build (network is
# available then) so the run is fast; anything not pre-cached is fetched at run
# time over the dedicated egress bridge (docker-compose.hostgarak.yml). NOTE: we
# do NOT force *_OFFLINE here — garak (the attacker) is allowed model egress, the
# same way the PyRIT/Promptfoo attackers use your OAuth CLI. The TARGET agent +
# canary stay on labnet (internal:true), so no target data ever leaves the host.
RUN python -m garak --model_type test.Blank \
      --probes dan,promptinject,leakreplay,atkgen --generations 1 || true
RUN python -c "from transformers import AutoModelForSequenceClassification as M, AutoTokenizer as T; \
m='garak-llm/roberta_toxicity_classifier'; T.from_pretrained(m); M.from_pretrained(m)" || true

COPY rest_generator.json.tmpl entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Artifacts volume is mounted by docker-compose at /artifacts.
ENTRYPOINT ["./entrypoint.sh"]
