#!/usr/bin/env bash
# Fully scripted install of the product(s) under test. If you typed it by hand it doesn't count.
# Runs on the controller VM. Must be idempotent and start from a clean snapshot.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "[*] installing products under test for $(basename "$HERE")"
# Example: docker compose -f docker-compose.tools.yml up -d
echo "[TODO] implement install + record wall-clock time to ready"
