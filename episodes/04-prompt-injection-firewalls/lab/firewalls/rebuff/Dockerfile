# ProtectAI Rebuff firewall (offline). Heuristics always on; vector/LLM optional (see NOTES.md).
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV REBUFF_MODE=offline
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
