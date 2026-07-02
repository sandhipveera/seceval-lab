# Setup — Step by Step

Everything runs locally. You said you already have **Docker, git, Node + Python, ffmpeg + jq**,
and your **ElevenLabs key + voice id** — so this is mostly wiring and a first run.

Repo root in these steps = this folder:
`/Users/veera/dev/prod-eval/docs`

---

## Step 0 — Confirm prerequisites (30 sec)

Open a terminal in the repo root and run:

```bash
cd /Users/veera/dev/prod-eval/docs
docker --version && docker compose version
git --version
node --version && python3 --version
ffmpeg -version | head -1 && jq --version
```

All should print a version. If `docker compose` errors, start Docker Desktop first.

---

## Step 1 — Initialize the repo (run this yourself — 30 sec)

A partial `.git/` may exist from setup but with stale lock files (the setup environment can't
delete files in your folder). Reset it cleanly on your machine, where this just works:

```bash
cd /Users/veera/dev/prod-eval/docs
rm -rf .git                    # clears any partial repo + stale lock files
git init -b main
git add -A
git commit -m "Security Lab: initial commit"
git log --oneline -1           # verify
```

If you want it on GitHub:

```bash
git remote add origin git@github.com:<you>/security-lab.git
git push -u origin main
```

> `.gitignore` already excludes secrets (`video/.env`), build output, and run artifacts —
> confirm with `git status` that `video/.env` is NOT listed once you create it.

---

## Step 2 — Wire up your ElevenLabs voice (2 min)

```bash
cp video/.env.example video/.env
```

Open `video/.env` and paste your two values:

```
ELEVENLABS_API_KEY=sk-...your key...
ELEVENLABS_VOICE_ID=...your cloned voice id...
```

Find the voice id in ElevenLabs → Voices → your voice → it's the id in the URL / API list.
`video/.env` is gitignored, so your key never gets committed.

Then install the video pipeline deps once:

```bash
cd video
pip install -r requirements.txt
npm install && npx playwright install chromium
cd ..
```

---

## Step 3 — Bring up Episode 01's lab (5 min)

The first episode (MCP agent-security) ships a real, isolated Docker lab. First let Claude Code
generate the container internals from the build contract, then start it.

```bash
cd episodes/01-mcp-agent-security/lab
# In Claude Code, from this folder, paste the prompt in CLAUDE_CODE_BUILD.md
# It generates: mcp-clean/, mcp-poisoned/, agent/, gateway/, scripts/*
```

Once generated:

```bash
docker compose up -d --build       # agent + clean MCP + poisoned MCP + canary sink
docker compose ps                  # confirm 4 containers are healthy
```

Safety check — the network has **no internet route** (this should FAIL, which is correct):

```bash
docker compose exec agent sh -c "curl -m 5 https://example.com" ; echo "exit=$?"
```

---

## Step 4 — Run the evaluation (10 min)

```bash
# from episodes/01-mcp-agent-security/lab
scripts/run_golf_scanner.sh        # fast local checks
scripts/run_mcp_scan.sh            # deeper static + dynamic
scripts/run_gateway_test.sh        # confirm the gateway blocks the exfil at runtime
scripts/normalize_findings.py      # -> artifacts/findings.csv
scripts/capture_metrics.sh         # -> artifacts/metrics.csv
```

Ground truth: check the canary. If `ep01-canary` logged a hit, that layer **failed** to stop
the poison. With the gateway profile on, it should be blocked.

```bash
docker compose logs canary-sink | grep -i exfil || echo "no exfil reached canary"
```

---

## Step 5 — Fill the content from real numbers

Open `episodes/01-mcp-agent-security/POST.md` and replace every `[FILL]` using
`lab/artifacts/findings.csv` and `metrics.csv`. Do the same in the metric/scorecard cards. Never
invent numbers — the reproducibility is the whole brand.

When done, set `episodes/01-mcp-agent-security/STATUS.yaml` → `status: in_production`.

---

## Step 6 — Produce the video (15 min)

```bash
make voiceover EP=01-mcp-agent-security   # ElevenLabs narration in your voice + manifest + captions
make record    EP=01-mcp-agent-security   # Playwright records the browser scenes / title cards
# record terminal scenes for real (optional but recommended):
video/record/record_terminal.sh lab_bringup "cd episodes/01-mcp-agent-security/lab && docker compose up"
make video     EP=01-mcp-agent-security   # assemble -> video/build/<slug>.mp4
```

> Note: Episode 01's `script.yaml` references a couple of scene cards that don't exist yet
> (`mcp_diagram.html`, `threats.html`). Either ask me to generate them, or the assembler will
> fall back to a slate for those scenes.

---

## Step 7 — Publish & advance

1. Publish the blog (`POST.md`) and the video; use `YOUTUBE.md` for title/description/chapters.
2. Set `STATUS.yaml` → `status: published`.
3. `git add -A && git commit -m "episode 01: mcp agent security"` (and push).

---

## The weekly auto-delivery

Every Monday, the **weekly-episode-storyboard** task drops the next episode into `episodes/`
with `STATUS: new`. To make sure its web-search permission is pre-approved, open the **Scheduled**
panel in the sidebar and click **Run now** once. After that it runs hands-free.

## Handy

```bash
make help        # list all targets
make new-episode SLUG=02-ai-model-scanner   # scaffold a folder manually if you ever need to
```

Stuck on a step? Tell me which number and what it printed, and I'll unblock it.
