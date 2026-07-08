# Episode 04 — deliberately vulnerable LLM app (stub planner, no model key needed).
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
# Single worker keeps the in-memory ingest store + determinism simple.
CMD ["python", "app.py"]
