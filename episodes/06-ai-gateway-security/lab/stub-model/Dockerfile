# OpenAI-compatible provider stub for the Ep.06 AI-gateway lab.
# MODE=gullible: complies with whatever instruction the model can reconstruct from the request
# text, including revealing CANARY_VALUE and flagging an exfil intent. Deterministic (no
# sampling, no randomness, no wall-clock in the decision path) so two identical runs -- with or
# without a gateway in front -- produce byte-identical verdicts. This is the attribution anchor:
# any block a gateway shows up as MUST be the gateway's doing, never the model's own refusal.
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir "flask==3.0.3"

COPY app.py /app/app.py

EXPOSE 8080
ENV MODE=gullible CANARY_VALUE=CANARY-EP06-9f2c1a
CMD ["python", "/app/app.py"]
