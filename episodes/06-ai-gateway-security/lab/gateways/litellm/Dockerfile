# Ep.06 lab — REAL LiteLLM Proxy, pinned by digest (STEP 0). Resolved 2026-08-05 for linux/arm64:
#   docker pull ghcr.io/berriai/litellm:v1.83.7-stable
#   docker buildx imagetools inspect ghcr.io/berriai/litellm:v1.83.7-stable   # -> @sha256:af0152ca...
# v1.83.7-stable is the first patched release for the 2026 advisories (CVE-2026-42208 pre-auth SQLi
# et al., which cover 1.81.16–1.83.6). A fixed TAG is still a floating reference, so we pin the
# DIGEST — which is itself the P3 posture lesson this episode argues for.
#
# This container routes the lab's victim-app to the local stub and wires the canary guardrail
# through LiteLLM's real CustomGuardrail extension point (see ep06_guardrail.py / config.on.yaml).
# The prior Flask stand-in is preserved as Dockerfile.substitute for the RUN.md fallback rule.
FROM ghcr.io/berriai/litellm@sha256:af0152ca6dfb6703b35c0d4899effa9ac132bce9a4fbcbe1dc6ef145c100db26

WORKDIR /app

# Guardrail + its detection patterns + both config variants + the toggle entrypoint, placed next to
# the config so LiteLLM resolves `ep06_guardrail.Ep06CanaryGuardrail` relative to it.
COPY patterns.py ep06_guardrail.py config.off.yaml config.on.yaml ep06_entrypoint.sh /app/
RUN chmod +x /app/ep06_entrypoint.sh

ENV GUARDRAILS=on \
    CANARY_VALUE=CANARY-EP06-9f2c1a \
    LITELLM_MASTER_KEY=sk-lab-master-not-real

EXPOSE 4000
ENTRYPOINT ["/app/ep06_entrypoint.sh"]
