# Deliberately vulnerable chatbot for the Ep.05 guardrail-bypass lab.
# Holds a BENIGN canary in its system prompt; MODE=stub is deterministic + jailbreakable so runs
# are repeatable with no API key. MODE=live drives a real model iff LLM_API_KEY is set.
FROM python:3.11-slim

WORKDIR /app
# requests is only needed for MODE=live; kept tiny for a fast, offline-buildable image.
RUN pip install --no-cache-dir "flask==3.0.3" "requests==2.32.3"

COPY app.py /app/app.py

EXPOSE 8080
ENV MODE=stub CANARY=CANARY-LAB-5-9F3A
CMD ["python", "/app/app.py"]
