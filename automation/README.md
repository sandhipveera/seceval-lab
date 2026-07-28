# Weekly episode runner (local Docker, launchd)

Runs **this week's episode lab** on your Mac and captures real artifacts. It only
touches episodes that have a `lab/RUN.md` (empty slates like ep06 are skipped),
picks the **highest-numbered unrun** one, and runs it. It never pushes,
publishes, fills `POST.md`, or merges branches.

## Pieces

| File | Role |
|---|---|
| `select_episode.sh` | Prints this week's target slug (newest RUN.md-having, unrun episode), or nothing. |
| `run_all.sh` (in each lab) | **Shell core** — deterministic build+run+normalize chain for one lab. Skips guards whose token is missing; a guard that never ran is left `[NOT EVALUATED]`. |
| `weekly_run.sh` | **launchd entrypoint.** Loads tokens from Keychain, selects the episode, runs it via the agent driver (default) or `--shell`. Logs to `logs/YYYY-Www.log`. |
| `com.accessquint.weekly-episode.plist` | LaunchAgent — fires Mondays 03:00. |

Two run modes (you built both):
- **agent** (default): `claude -p` opens the lab's `RUN.md`, follows it, applies the
  NOT-EVALUATED honesty rules, writes a prose summary, then stops.
- **shell** (`--shell`): runs the lab's `run_all.sh` — deterministic, free, no summary.

## One-time setup

### 1. Store tokens in the login Keychain
The runner reads each token as a generic password whose **service name = the env var**:
```bash
security add-generic-password -a "$USER" -s HF_TOKEN         -w 'hf_xxxxxxxx'
security add-generic-password -a "$USER" -s GUARDRAILS_TOKEN -w 'xxxxxxxx'
# update later with:  security add-generic-password -U -a "$USER" -s HF_TOKEN -w 'hf_new'
```
Skip either one and its guards are simply recorded NOT EVALUATED — the run still proceeds.

### 2. Sanity-check before scheduling
```bash
cd /Users/veera/dev/prod-eval/docs
bash automation/select_episode.sh          # -> 05-llm-guardrail-bypass
bash automation/weekly_run.sh --shell      # full local run, deterministic path
# or dry the agent path:
bash automation/weekly_run.sh              # -> claude -p, follows RUN.md
```

### 3. Install the LaunchAgent
```bash
cp automation/com.accessquint.weekly-episode.plist ~/Library/LaunchAgents/
launchctl load  ~/Library/LaunchAgents/com.accessquint.weekly-episode.plist
launchctl start com.accessquint.weekly-episode      # run once now to verify
launchctl list | grep weekly-episode                # confirm it's registered
```
Uninstall: `launchctl unload ~/Library/LaunchAgents/com.accessquint.weekly-episode.plist`

> **PATH note:** launchd gives the job a bare environment. The plist sets a PATH
> covering Docker Desktop (`/usr/local/bin`), Homebrew Apple-Silicon
> (`/opt/homebrew/bin`), and system dirs. If `docker`, `claude`, `python3`, or
> `security` aren't found in the log, add their dir to the plist's PATH.

> **Keychain note:** as a per-user LaunchAgent, `security find-generic-password`
> reads your login keychain while you're logged in. The first run may prompt to
> allow access — tick "Always Allow" so future unattended runs don't block.

## Logs
- Per-week transcript: `automation/logs/2026-Www.log`
- launchd stdout/stderr: `automation/logs/launchd.{out,err}.log`
