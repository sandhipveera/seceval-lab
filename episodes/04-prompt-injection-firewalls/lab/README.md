# Episode 04 Lab — Prompt-injection firewall teardown (Docker)

Local, isolated, **no internet egress**. A deliberately vulnerable LLM app can be talked into
POSTing its context to an address via a prompt injection — but that address is an in-network
**canary sink**, so the payload is benign and nothing leaves your machine. You run the same
injection battery through four firewalls, one at a time, and compare what each catches.

Firewalls under test: **Prompt Guard 2** (Meta, binary classifier) · **Vigil** (patterns +
embeddings) · **LLM Guard** (Protect AI toolkit, PromptInjection scanner) · **Rebuff**
(heuristics + LLM + vector store + canary tokens).

## Safety
- `labnet` is `internal: true` — containers cannot reach the internet. The "exfil" only ever hits
  the in-network `canary-sink`, which logs it. Nothing leaves your machine.
- Payloads are benign canaries. Do not add real secrets. Responsible disclosure if you find a real
  tool bug. Review each tool's license before publishing figures (Prompt Guard 2 is under Meta's
  Llama license).

## Bring it up
```bash
docker compose up -d --build                          # vuln app + canary sink (baseline, no guard)
docker compose --profile prompt-guard-2 up -d --build # add Prompt Guard 2 at the door
docker compose --profile vigil up -d --build          # ...or Vigil
docker compose --profile llm-guard up -d --build      # ...or LLM Guard
docker compose --profile rebuff up -d --build         # ...or Rebuff
```
Run exactly one firewall profile per pass, resetting to a clean container state between runs
(`docker compose down && docker compose up -d --build`) so every guard faces identical conditions.

## Run the injection battery (Round 1–3)
```bash
scripts/run_firewall.sh none            # baseline: confirm the injection reaches the canary
scripts/run_firewall.sh prompt-guard-2  # send the battery with Prompt Guard 2 in front
scripts/run_firewall.sh vigil
scripts/run_firewall.sh llm-guard
scripts/run_firewall.sh rebuff
scripts/false_positive_test.sh          # feed benign-but-scary prompts; count over-blocks
scripts/normalize_findings.py           # merge all outputs -> artifacts/findings.csv (caught/missed)
scripts/capture_metrics.sh              # added latency + false-positive rate -> artifacts/metrics.csv
```

The battery escalates: **L1** plain direct injection, **L2** obfuscated (spaced / homoglyph /
base64), **L3** indirect (payload hidden in a retrieved document).

## What "caught" means
- A firewall **catches** an attack if it labels the injected input malicious / blocks it before the
  app acts.
- Check `canary-sink` logs: if it received the payload, the injection **won** for that
  configuration (that guard did NOT stop it).

## Tear down
```bash
docker compose --profile prompt-guard-2 --profile vigil --profile llm-guard --profile rebuff down -v
```

> The `vuln-app/`, `firewalls/*/` build folders and `scripts/` are scaffolded by Claude Code from
> CLAUDE_CODE_BUILD.md — this folder ships the lab definition and the contract; the implementations
> get generated on first build.
