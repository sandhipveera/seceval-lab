#!/usr/bin/env bash
# Capture dashboard screenshots for the eval writeup (headless chromium).
# Usage: capture_screenshots.sh <run_id> <url> [name]
source "$(dirname "$0")/../lib/common.sh"
RUN_ID="${1:?run_id}"; URL="${2:?url}"; NAME="${3:-shot}"
OUT="$REPO_ROOT/artifacts/$RUN_ID/screenshots"; mkdir -p "$OUT"
if command -v chromium >/dev/null; then BIN=chromium
elif command -v google-chrome >/dev/null; then BIN=google-chrome
else die "install chromium/google-chrome for screenshots"; fi
log "screenshot $URL -> $OUT/$NAME.png"
"$BIN" --headless --disable-gpu --no-sandbox --window-size=1600,1000 \
  --screenshot="$OUT/$NAME.png" "$URL"
