#!/usr/bin/env python3
"""Host-side Metal (MPS) Llama Guard 4 proxy for the Ep.05 lab.

Docker on macOS is CPU-only (no Metal passthrough), so to run the FAITHFUL Llama Guard 4 12B on the
Apple GPU we serve it as a native macOS process here. Logic is identical to the containerized
guard-llamaguard/app.py — classify raw user text as safe/unsafe, block unsafe input, forward allowed
text to the (host-published) target, and block any reply carrying the canary — but the model loads
onto MPS. Serves :8091; UPSTREAM points at the target-chatbot's host-published port.

Honesty rule preserved: if the model cannot load, /health reports it and every verdict is an error,
so normalize_findings.py marks Llama Guard NOT EVALUATED rather than crediting a catch.
"""
import os
from flask import Flask, request, jsonify
import requests

UPSTREAM = os.environ.get("UPSTREAM", "http://localhost:8080/chat")
CANARY   = os.environ.get("CANARY", "CANARY-LAB-5-9F3A")
MODEL    = os.environ.get("LLAMAGUARD_MODEL", "meta-llama/Llama-Guard-4-12B")
PORT     = int(os.environ.get("PORT", "8091"))

_MODE = None            # "mm" (processor) | "lm" (tokenizer)
_proc = _model = _tok = None
_LOAD_ERR = ""
_DEVICE = "cpu"
TF_VERSION = "?"
try:
    import torch, transformers
    TF_VERSION = transformers.__version__
    _DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
    _DTYPE = torch.bfloat16
    _FORCE_MM = os.environ.get("LLAMAGUARD_FORCE_MM") == "1"   # surface mm load errors, no silent lm fallback
    try:
        from transformers import AutoProcessor, AutoModelForImageTextToText
        _proc = AutoProcessor.from_pretrained(MODEL)
        _model = AutoModelForImageTextToText.from_pretrained(MODEL, torch_dtype=_DTYPE).to(_DEVICE)
        _MODE = "mm"
    except Exception as e_mm:
        if _FORCE_MM:
            raise
        from transformers import AutoTokenizer, AutoModelForCausalLM
        _tok = AutoTokenizer.from_pretrained(MODEL)
        _model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=_DTYPE).to(_DEVICE)
        _MODE = "lm"
    _model.eval()
except Exception as e:
    TF_VERSION = "import-error"
    _LOAD_ERR = str(e)


def _to_device(inputs):
    if hasattr(inputs, "to"):
        return inputs.to(_DEVICE)
    return {k: (v.to(_DEVICE) if hasattr(v, "to") else v) for k, v in inputs.items()}


def classify_unsafe(text: str):
    """Return (is_unsafe, raw_label). Raises if the model isn't loaded."""
    import torch
    if _MODE == "mm":
        # Llama Guard 4's multimodal processor expects structured content, not a bare string.
        conversation = [{"role": "user", "content": [{"type": "text", "text": text}]}]
        inputs = _proc.apply_chat_template(
            conversation, add_generation_prompt=True, return_tensors="pt",
            return_dict=True, tokenize=True,
        )
        inputs = _to_device(inputs)
        with torch.no_grad():
            out = _model.generate(**inputs, max_new_tokens=20, do_sample=False, use_cache=False)
        n = inputs["input_ids"].shape[-1]
        decoded = _proc.decode(out[0][n:], skip_special_tokens=True).strip().lower()
    else:
        conversation = [{"role": "user", "content": text}]
        enc = _tok.apply_chat_template(conversation, add_generation_prompt=True,
                                       return_tensors="pt", return_dict=True)
        input_ids = enc["input_ids"].to(_DEVICE)
        attn = enc.get("attention_mask")
        attn = attn.to(_DEVICE) if attn is not None else torch.ones_like(input_ids)
        with torch.no_grad():
            # Llama4 defaults to a StaticCache whose max_cache_len is None here -> min(sliding_window,
            # None) TypeError (device-independent). The dynamic cache sidesteps it.
            out = _model.generate(input_ids=input_ids, attention_mask=attn,
                                  max_new_tokens=20, do_sample=False, use_cache=False)
        n = input_ids.shape[-1]
        decoded = _tok.decode(out[0][n:], skip_special_tokens=True).strip().lower()
    return (decoded.startswith("unsafe"), decoded[:40])


app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok" if _model is not None else "model-not-loaded",
                   guard="llama-guard", model=MODEL, mode=_MODE, device=_DEVICE,
                   transformers=TF_VERSION, load_error=_LOAD_ERR), 200

@app.post("/chat")
def chat():
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("message", "")

    if _model is None:
        return jsonify(blocked=False, verdict="error", reply="",
                       error=f"model-not-loaded:{_LOAD_ERR[:80]}"), 200
    try:
        unsafe, label = classify_unsafe(text)
    except Exception as e:
        return jsonify(blocked=False, verdict="error", reply="", error=str(e)[:120]), 200

    if unsafe:
        return jsonify(blocked=True, verdict="block", rule=f"llama-guard:{label}", reply=""), 200

    try:
        up = requests.post(UPSTREAM, json={"message": text}, timeout=30).json()
        reply = up.get("reply", "")
    except Exception as e:
        return jsonify(blocked=False, verdict="pass", reply="", error=str(e)), 200

    if CANARY in reply:
        return jsonify(blocked=True, verdict="block", rule="output-canary-check",
                       reply="[blocked: response withheld by output check]"), 200

    return jsonify(blocked=False, verdict="pass", reply=reply, note=f"llama-guard:{label}"), 200

if __name__ == "__main__":
    print(f"[host-llamaguard] up — model={MODEL} mode={_MODE} device={_DEVICE} "
          f"transformers={TF_VERSION}{' LOAD_ERROR=' + _LOAD_ERR if _LOAD_ERR else ''}", flush=True)
    app.run(host="127.0.0.1", port=PORT)
