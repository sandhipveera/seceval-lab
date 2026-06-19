#!/usr/bin/env bash
# Bundle all artifacts for an eval into a single tarball for the writeup/repo.
# Usage: collect_artifacts.sh <slug> <run_id>
source "$(dirname "$0")/../lib/common.sh"
SLUG="${1:?slug}"; RUN_ID="${2:?run_id}"
SRC="$REPO_ROOT/artifacts/$RUN_ID"
DST="$REPO_ROOT/evaluations/$SLUG/artifacts/$RUN_ID"
mkdir -p "$DST"; cp -r "$SRC/." "$DST/" 2>/dev/null || true
( cd "$REPO_ROOT/evaluations/$SLUG/artifacts" && tar czf "$RUN_ID.tar.gz" "$RUN_ID" )
log "artifacts collected -> $DST (+ tarball)"
