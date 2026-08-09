# Attack + posture harness for the Ep.06 lab. Fires the six declarative scenarios in attacks/ at
# victim-app, in fixed order, then runs the read-only P1/P2/P3 posture checks against the active
# gateway (see posture.py -- no exploit code, version/reachability/pinning checks only).
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir "requests==2.32.3" "pyyaml==6.0.2"
COPY encoders.py posture.py run.py /app/
CMD ["python", "/app/run.py"]
