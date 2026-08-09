#!/usr/bin/env bash
# Ep.06 lab — one-time OFFLINE-PREP step for Bifrost (reproducibility of the baked pricing cache).
#
# Bifrost (maximhq/bifrost) FATALS on startup if it cannot sync its model-pricing catalogue from
# getbifrost.ai AND no cached pricing exists ("failed to load pricing data from URL and no existing
# data available"). The lab's runtime network (labnet) is internal:true (no egress, rule 5), so the
# fetch must happen BEFORE/OUTSIDE the run — exactly like the image pulls in STEP 0.
#
# This script runs Bifrost once on a network WITH egress, lets it cache the pricing catalogue into
# config.db, then snapshots that DB into gateways/bifrost/data/config.db, which the Dockerfile bakes
# into the image so the labnet run starts fully offline. Re-run only to refresh the cache.
set -euo pipefail
cd "$(dirname "$0")"
IMG="maximhq/bifrost@sha256:14f704fcee64de509c139d14458871a4221f71f28a397f2b4d92bbe092d7a63c"
SEED_DIR="$(mktemp -d)"
echo "== seeding Bifrost pricing cache with egress (dir=$SEED_DIR) =="
docker rm -f ep06_bifrost_seed >/dev/null 2>&1 || true
docker run -d --name ep06_bifrost_seed -e APP_HOST=0.0.0.0 -e BIFROST_HOST=0.0.0.0 \
  -v "$SEED_DIR":/app/data "$IMG" >/dev/null
for i in $(seq 1 40); do
  docker logs ep06_bifrost_seed 2>&1 | grep -qi "successfully started bifrost" && { echo "seeded ok"; break; }
  docker logs ep06_bifrost_seed 2>&1 | grep -qi "fatal" && { echo "seed FATAL"; docker logs ep06_bifrost_seed 2>&1 | grep -i fatal; exit 1; }
  sleep 2
done
docker stop ep06_bifrost_seed >/dev/null && docker rm ep06_bifrost_seed >/dev/null
mkdir -p data
python3 - "$SEED_DIR/config.db" data/config.db <<'PY'
import sqlite3, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
con = sqlite3.connect(src); con.execute("PRAGMA wal_checkpoint(TRUNCATE)"); con.close()
shutil.copy(src, dst)
print("baked", dst)
PY
rm -rf "$SEED_DIR"
echo "== done: gateways/bifrost/data/config.db =="
