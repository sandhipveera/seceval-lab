# Deliberately vulnerable chat app for the Ep.06 AI-gateway lab. Holds a BENIGN canary in its
# system prompt, retrieves attacker-controlled docs unsanitized, and faithfully acts on whatever
# the model tells it to -- including POSTing to CANARY_URL. That fidelity is what makes the
# canary-sink hit meaningful ground truth: if the model was allowed to say "exfil now", this app
# actually tries. Talks to whichever OPENAI_BASE_URL points at (a gateway, or the stub directly).
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir "flask==3.0.3" "requests==2.32.3"

COPY app.py /app/app.py

EXPOSE 8080
ENV OPENAI_BASE_URL="http://ep06-stub-model:8080/v1" \
    OPENAI_API_KEY="sk-lab-not-a-real-key" \
    SYSTEM_CANARY="CANARY-EP06-9f2c1a" \
    DOC_SERVER_URL="http://ep06-docs:8080" \
    CANARY_URL="http://ep06-canary:8080/exfil"
CMD ["python", "/app/app.py"]
