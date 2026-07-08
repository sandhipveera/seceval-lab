#!/usr/bin/env python3
# =============================================================================
# EP04 firewall wrapper — Meta Llama Prompt Guard 2 (86M/22M binary classifier).
# Exposes POST /classify {text} -> {label: benign|malicious, score}. The model
# weights are baked into the image (see Dockerfile) so this runs OFFLINE.
# =============================================================================
import os

import torch
import torch.nn.functional as F
from flask import Flask, jsonify, request
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_ID = os.environ.get("MODEL_ID", "meta-llama/Llama-Prompt-Guard-2-86M")
THRESHOLD = float(os.environ.get("THRESHOLD", "0.5"))

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
model.eval()

app = Flask(__name__)


def score(text: str):
    inputs = tokenizer(text or "", return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)[0]
    # Prompt Guard 2 is a BINARY classifier; the last index is the
    # malicious/injection class. (Confirm index against your model card pin.)
    malicious = float(probs[-1])
    label = "malicious" if malicious >= THRESHOLD else "benign"
    return label, round(malicious, 4)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "guard": "prompt-guard-2", "model": MODEL_ID})


@app.post("/classify")
def classify():
    text = (request.get_json(force=True, silent=True) or {}).get("text", "")
    label, s = score(text)
    return jsonify({"label": label, "score": s, "guard": "prompt-guard-2"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
