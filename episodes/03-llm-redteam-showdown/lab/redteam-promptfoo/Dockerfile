# Promptfoo red-team runner. Network is used ONLY at build time (npm install).
# At run time it lives on labnet (internal:true) and only reaches the vuln-agent.
FROM node:20-slim

WORKDIR /app

# --- build-time only: install a PINNED promptfoo ----------------------------
# promptfoo 0.121.18 (latest 0.121.x line). Node base is 20.x LTS (>=20.20 as
# promptfoo requires). Verify/bump against https://www.npmjs.com/package/promptfoo.
RUN npm install -g "promptfoo@0.121.18"

COPY promptfooconfig.yaml entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Keep promptfoo fully offline at run time (no telemetry / no update checks).
ENV PROMPTFOO_DISABLE_TELEMETRY=1 \
    PROMPTFOO_DISABLE_UPDATE=1 \
    PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=1

ENTRYPOINT ["./entrypoint.sh"]
