#!/usr/bin/env bash
# =============================================================================
# BENIGN CANARY LAB — Garak runner
# Points garak at the vuln-agent (TARGET_URL) via its REST generator and runs a
# probe set covering jailbreak, prompt injection, leakage, and multi-turn/agent
# probes. Raw report JSON is written to /artifacts/garak.json.
#
# No internet egress at run time: labnet is internal:true and garak only reaches
# the in-network vuln-agent. (garak itself was installed at BUILD time.)
# =============================================================================
set -euo pipefail

TARGET_URL="${TARGET_URL:-http://ep03-vuln-agent:8000/v1}"
ART=/artifacts
mkdir -p "$ART"

# Record the pinned garak version alongside the artifact.
GARAK_VERSION="$(python -c 'import garak; print(getattr(garak, "__version__", "unknown"))' 2>/dev/null || echo unknown)"
echo "garak version: ${GARAK_VERSION}"

# Substitute the target URL into the REST generator config.
sed "s#__TARGET_URL__#${TARGET_URL}#g" rest_generator.json.tmpl > /tmp/rest_generator.json
echo "generator config:"; cat /tmp/rest_generator.json

# --- Probe selection --------------------------------------------------------
# Chosen to cover the four required categories. Probe module names are used
# (garak runs all probes within a module). These modules are stable across
# recent garak releases; if a name is absent in your pin, garak will warn and
# skip it rather than fail. Alternatives are noted in comments.
#   jailbreak         -> dan            (classic DAN-style; alt: promptinject, grandma)
#   prompt injection  -> promptinject   (alt: latentinjection)
#   leakage           -> leakreplay     (alt: xss, information leakage via replay)
#   multi-turn/agent  -> atkgen         (Agent-breaker/GOAT-style generative multi-turn)
PROBES="dan,promptinject,leakreplay,atkgen"

REPORT_PREFIX="${ART}/garak_run"

set +e
python -m garak \
  --model_type rest \
  --generator_option_file /tmp/rest_generator.json \
  --probes "$PROBES" \
  --report_prefix "$REPORT_PREFIX" \
  --generations 1
GARAK_RC=$?
set -e
echo "garak exit code: ${GARAK_RC}"

# garak writes <prefix>.report.jsonl. Normalize to a single garak.json wrapper
# that records the version + points at the raw report lines (parsed downstream).
RAW_JSONL="${REPORT_PREFIX}.report.jsonl"
python - "$RAW_JSONL" "$GARAK_VERSION" "$PROBES" <<'PY'
import json, sys, pathlib
raw_path, version, probes = sys.argv[1], sys.argv[2], sys.argv[3]
records = []
p = pathlib.Path(raw_path)
if p.exists():
    for line in p.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            continue
out = {
    "framework": "garak",
    "garak_version": version,
    "probes": probes,
    "raw_report_path": raw_path,
    "records": records,
}
pathlib.Path("/artifacts/garak.json").write_text(json.dumps(out, indent=2))
print(f"wrote /artifacts/garak.json with {len(records)} records (garak {version})")
PY
