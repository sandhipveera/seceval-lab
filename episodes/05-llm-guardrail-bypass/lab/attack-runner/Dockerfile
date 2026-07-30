# Attack runner for the Ep.05 guardrail-bypass lab. Sends the same benign jailbreak three ways
# (plain / character-injection / emoji-smuggled) and records what each guard caught.
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir "requests==2.32.3"
COPY encoders.py run.py fp_probe.py benign_prompts.txt /app/
# Idle by default; the run_*.sh scripts exec run.py with the right LABEL/HIT_URL/OUTFILE.
CMD ["sleep", "infinity"]
