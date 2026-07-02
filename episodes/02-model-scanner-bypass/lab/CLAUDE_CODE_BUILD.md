# Claude Code — Build Contract for the Episode 02 Lab

Paste into Claude Code from this `lab/` folder to generate the container implementations the
`docker-compose.yml` references, then run the teardown and capture results.

```
Build the Docker lab defined by ./docker-compose.yml for an AI model-scanner bypass evaluation. It
must run 100% locally with NO internet egress (labnet is internal:true) and use only a BENIGN
canary payload (a single request to ${CANARY_URL} on model load — NEVER a reverse shell or real
exploit). Generate these build contexts and scripts:

1) model-builder/ — a container that emits ONE base malicious pickle-based model file plus the
   evasive VARIANTS (env-driven) into the shared /models volume, plus a clean/ set for
   false-positive testing:
     - plain          : payload via a directly-named dangerous callable (easy case).
     - deep_import    : SAME payload reached via a submodule a naive blocklist doesn't enumerate
                        (conceptually the CVE-2025-10157 class — do NOT target a specific fixed CVE).
     - renamed        : pickle content written to a PyTorch-style .bin extension (CVE-2025-10155 class).
     - broken_archive : payload-first stream and/or a non-zip container so a scanner mis-parses and
                        reports nothing (nullifAI / broken-pickle class).
   Every variant's payload does exactly ONE thing when loaded: GET/POST ${CANARY_URL}. Keep it
   benign; add a big header comment stating so. Also emit /models/clean/ with 2–3 benign models.
2) scanner-picklescan/  — installs the LATEST picklescan (>= 0.0.31), runs it over /models and
   /models/clean, saves raw JSON to /artifacts/picklescan.json. Record version.
3) scanner-modelscan/   — installs Protect AI ModelScan, scans the same files, saves raw output to
   /artifacts/modelscan.json.
4) scanner-modelaudit/  — installs Promptfoo ModelAudit, scans the same files with SARIF output to
   /artifacts/modelaudit.sarif (and a JSON copy if convenient).
5) scanner-fickling/    — installs Trail of Bits fickling, runs its pickle scanner (allowlist mode)
   over the same files, saves raw output to /artifacts/fickling.json.
6) scripts/run_*.sh (one per scanner) — exec the scanner container against every variant and the
   clean set; time each scan (small + large file); tee raw output to the artifact path above.
7) scripts/normalize_findings.py — implement the parsers so it emits artifacts/findings.csv with
   columns: scanner,scanner_version,model_variant,finding,severity,caught,false_positive,scan_seconds.
   One row per (scanner x variant) and per (scanner x clean model).
8) scripts/capture_metrics.sh — record scan time (small/large), peak RAM under load, and clean-set
   false-positive counts per scanner into artifacts/metrics.csv.

Verification before done:
- `docker compose up -d --build` succeeds; the model-builder writes all variants + clean set to
  the shared volume.
- Loading a variant (in an ISOLATED loader step) makes the canary sink log a hit — proving each
  malicious file is genuinely live — while the clean set does NOT.
- Each scanner runs and writes its raw artifact; normalize_findings.py produces findings.csv.
- Confirm labnet has no internet route (a curl to a public host from a container fails).
- Re-run twice; confirm results are stable (deterministic builder + pinned tool versions).

Then fill the [FILL] tables in ../POST.md and the metrics/scorecard cards from the real artifacts.
Keep everything benign and isolated; test against PATCHED current tool versions; never ship a
weaponized exploit, and follow responsible disclosure if a real current-version bug surfaces.
```
