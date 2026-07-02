# Episode 02 Lab — AI model-scanner bypass teardown (Docker)

Local, isolated, **no internet egress**. One malicious model file (pickle-based, carrying a
**benign canary** payload) plus a few evasive variants. You run four scanners against the same
files and compare what each catches.

## Safety
- `labnet` is `internal: true` — containers cannot reach the internet. The payload only ever hits
  the in-network `canary-sink`, which logs it. Nothing leaves your machine.
- The payload is a **benign canary**: on model load it makes a single request to `${CANARY_URL}`.
  It is NOT a reverse shell, NOT a real exploit. Do not add real secrets or weaponize it.
- Assumes **patched, current** scanner versions. The goal is not to re-fire the disclosed 2025 CVEs
  (they're fixed) — it's to test how each detection *philosophy* holds up against the *class* of
  evasion those CVEs represent. Responsible disclosure if you find a real, current tool bug.

## Bring it up
```bash
docker compose up -d --build              # canary sink + model-builder + all four scanners
docker compose logs -f model-builder      # confirm variants written to the shared /models volume
```

## The model files (built into the shared `models` volume)
- `plain`          — payload with a directly-named dangerous callable (the easy case).
- `deep_import`    — same payload reached via a submodule a naive blocklist doesn't enumerate.
- `renamed`        — pickle content wearing a PyTorch-style `.bin` extension.
- `broken_archive` — payload-first stream / non-zip container so a scanner mis-parses and reports nothing.
- `clean/`         — a set of benign models for false-positive measurement.

## Run the scanners (Round 1–2)
```bash
scripts/run_picklescan.sh      # picklescan (blocklist) -> artifacts/picklescan.json
scripts/run_modelscan.sh       # ModelScan (Protect AI) -> artifacts/modelscan.json
scripts/run_modelaudit.sh      # ModelAudit (Promptfoo, SARIF) -> artifacts/modelaudit.sarif
scripts/run_fickling.sh        # fickling (allowlist) -> artifacts/fickling.json
scripts/normalize_findings.py  # merge all outputs -> artifacts/findings.csv (caught/missed per variant)
```

## What "caught" means
- A scanner **catches** a file if it flags the dangerous callable / opcode (or refuses it) for that
  variant.
- Check `canary-sink` logs: if it received a hit when a variant was *loaded*, the payload executed
  (ground truth that the file is live). A scanner that reports "safe" on a file whose canary fires
  is a **miss**.

## Tear down
```bash
docker compose down -v      # -v also drops the shared models volume
```

> The `model-builder/`, `scanner-*/` build folders and `scripts/` are scaffolded by Claude Code
> from CLAUDE_CODE_BUILD.md — this folder ships the lab definition and the contract; the
> implementations get generated on first build.
