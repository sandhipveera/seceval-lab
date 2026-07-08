# ProtectAI LLM Guard — PromptInjection input scanner. Model cached at build for offline runtime.
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Warm the scanner once at build so its fine-tuned model is baked into the image.
RUN python -c "from llm_guard.input_scanners import PromptInjection; from llm_guard.input_scanners.prompt_injection import MatchType; PromptInjection(match_type=MatchType.FULL)"

# No network model pulls at runtime.
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
