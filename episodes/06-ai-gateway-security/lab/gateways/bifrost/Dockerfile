# Ep.06 lab — REAL Bifrost (Maxim AI) gateway, pinned by digest (STEP 0). Resolved 2026-08-05 for
# linux/arm64 (docker pull maximhq/bifrost:latest; version /api/version -> v1.6.8):
#   docker buildx imagetools inspect maximhq/bifrost:latest   # -> @sha256:14f704fc...
#
# Two lab adaptations, both about running fully OFFLINE on the internal labnet:
#   1) Bifrost fatals without a cached pricing catalogue (it normally fetches getbifrost.ai on boot).
#      seed_pricing.sh caches it into data/config.db OUTSIDE the run (like the image pulls); we bake
#      that snapshot in. See seed_pricing.sh.
#   2) config.json points the openai provider at the in-network stub, with allow_private_network so
#      Bifrost will talk http to a private host.
# Bifrost ships NO native content guardrail (its policy layer is bring-your-own / governance), so the
# lab records guardrails_native:false and "not offered" — never a miss. The prior Flask stand-in is
# preserved as Dockerfile.substitute for the RUN.md fallback rule.
FROM maximhq/bifrost@sha256:14f704fcee64de509c139d14458871a4221f71f28a397f2b4d92bbe092d7a63c

USER root
# Baked pricing cache (offline boot) + provider config routing to the stub.
COPY data/config.db /app/data/config.db
COPY config.json /app/data/config.json
RUN chown -R 1000:0 /app/data && chmod -R g+rwX /app/data
USER 1000

# Bind on all interfaces so victim-app on labnet can reach it (Bifrost defaults to localhost).
ENV APP_HOST=0.0.0.0 \
    BIFROST_HOST=0.0.0.0

EXPOSE 8080
