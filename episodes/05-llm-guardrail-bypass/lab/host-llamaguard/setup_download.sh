#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_download.sh — one-time host-side bootstrap for the Metal Llama Guard 4 leg.
#
# Docker on macOS runs in a Linux VM with no Metal/CUDA passthrough, so Llama
# Guard 4 12B can only use the Apple GPU when run NATIVELY on the host. This
# builds an isolated Python 3.12 venv (uv) with an MPS-capable torch + the
# transformers 4.51 line that supports the Llama4 arch, then downloads the gated
# model (HF_TOKEN from Keychain; license must already be accepted on HF).
#
# Long pole is the ~24GB download — run this in the background.
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"
HERE="$PWD"
VENV="$HERE/.venv"
MODEL="${LLAMAGUARD_MODEL:-meta-llama/Llama-Guard-4-12B}"

HF_TOKEN="$(security find-generic-password -s HF_TOKEN -w 2>/dev/null)"
if [ -z "$HF_TOKEN" ]; then echo "FATAL: HF_TOKEN not in Keychain"; exit 1; fi
export HF_TOKEN HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"

echo "[setup] creating 3.12 venv via uv at $VENV"
uv venv --python 3.12 "$VENV" || { echo "FATAL: uv venv failed"; exit 1; }

echo "[setup] installing deps (torch MPS + transformers 4.51.3 + hf_transfer)"
uv pip install --python "$VENV" \
  "torch" "transformers==4.51.3" "accelerate" "huggingface_hub" \
  "hf_transfer" "flask" "requests" || { echo "FATAL: pip install failed"; exit 1; }

echo "[setup] torch/MPS check:"
"$VENV/bin/python" -c "import torch,transformers;print('torch',torch.__version__,'mps',torch.backends.mps.is_available(),'tf',transformers.__version__)" \
  || { echo "FATAL: torch import failed"; exit 1; }

echo "[setup] downloading $MODEL (gated) — skipping original/ raw checkpoints to save space"
HF_HUB_ENABLE_HF_TRANSFER=1 "$VENV/bin/python" - "$MODEL" <<'PY'
import sys, os
from huggingface_hub import snapshot_download
model = sys.argv[1]
p = snapshot_download(
    model,
    token=os.environ["HF_TOKEN"],
    ignore_patterns=["original/*", "*.pth", "consolidated*"],  # keep the HF safetensors only
)
print("DOWNLOADED_TO", p)
PY
echo "[setup] done"
