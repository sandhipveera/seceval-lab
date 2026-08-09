# Ep.06 lab — REAL Portkey OSS gateway (@portkey-ai/gateway), pinned by digest (STEP 0). Resolved
# 2026-08-05 for linux/arm64:
#   docker pull portkeyai/gateway:latest        # image labels: version 1.15.2, MIT, Portkey-AI/gateway
#   docker buildx imagetools inspect portkeyai/gateway:latest   # -> @sha256:97f094d9...
#
# Routing + guardrails are driven per-request via x-portkey-config (see gen_headers.py; victim-app
# injects it from OPENAI_EXTRA_HEADERS), the way a real Portkey client integrates. The only build-time
# need is to let the gateway route to the in-network stub: Portkey's SSRF guard rejects any
# custom_host whose hostname is not in TRUSTED_CUSTOM_HOSTS (default: localhost only). The prior Flask
# stand-in is preserved as Dockerfile.substitute for the RUN.md fallback rule.
FROM portkeyai/gateway@sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d

# Allow routing to the lab's in-network stub (SSRF allowlist). No egress: labnet is internal.
ENV TRUSTED_CUSTOM_HOSTS=ep06-stub-model

EXPOSE 8787
