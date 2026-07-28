#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# weekly_run.sh — launchd entrypoint. Runs THIS WEEK'S episode lab locally.
#
# Flow:
#   1. Load HF_TOKEN + GUARDRAILS_TOKEN from the macOS login Keychain (non-fatal
#      if absent — token-less guards run, the rest are recorded NOT EVALUATED).
#   2. Pick the newest runnable-unrun episode (select_episode.sh — RUN.md only).
#   3. Run it, one of two ways:
#        default  -> AGENT driver: `claude -p` follows the lab's RUN.md, applies
#                    the honesty rules, writes a summary, then stops.
#        --shell  -> SHELL driver: run the lab's deterministic run_all.sh.
#
# Everything is logged to automation/logs/YYYY-Www.log for an audit trail.
# This job NEVER pushes, publishes, fills POST.md, or merges branches.
# ---------------------------------------------------------------------------
set -uo pipefail

REPO="${REPO:-/Users/veera/dev/prod-eval/docs}"
AUTODIR="$REPO/automation"
LOGDIR="$AUTODIR/logs"
MODE="agent"
[ "${1:-}" = "--shell" ] && MODE="shell"

mkdir -p "$LOGDIR"
STAMP="$(date +%Y-W%V)"                 # ISO week, e.g. 2026-W30
LOG="$LOGDIR/$STAMP.log"
say(){ printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"; }

say "===== weekly_run start (mode=$MODE, repo=$REPO) ====="

# --- 1) Tokens from Keychain (each stored as a generic password, service = the var name) ---
load_kc(){ security find-generic-password -s "$1" -w 2>/dev/null; }
HF_TOKEN="$(load_kc HF_TOKEN)";                 export HF_TOKEN
GUARDRAILS_TOKEN="$(load_kc GUARDRAILS_TOKEN)"; export GUARDRAILS_TOKEN
say "tokens: HF_TOKEN=${HF_TOKEN:+present}${HF_TOKEN:-MISSING}  GUARDRAILS_TOKEN=${GUARDRAILS_TOKEN:+present}${GUARDRAILS_TOKEN:-MISSING}"

# --- 2) Select this week's target ---
SLUG="$(REPO="$REPO" bash "$AUTODIR/select_episode.sh")"
if [ -z "$SLUG" ]; then
  say "no unrun runnable episode this week — nothing to do."
  say "===== weekly_run done ====="
  exit 0
fi
LAB="$REPO/episodes/$SLUG/lab"
say "target episode: $SLUG"
say "current git branch: $(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

# Note (do NOT auto-switch): if a <slug>-wip branch exists and the tree is dirty,
# switching could clobber work. RUN.md tells the agent which branch it needs; the
# agent switches only when the tree is clean. The shell path runs on whatever is
# checked out and logs it, so results are always attributable to a known branch.

# --- 3) Run ---
if [ "$MODE" = "shell" ]; then
  say "shell driver: bash $LAB/run_all.sh"
  bash "$LAB/run_all.sh" 2>&1 | tee -a "$LOG"
  say "shell driver exit=${PIPESTATUS[0]}"
else
  if ! command -v claude >/dev/null 2>&1; then
    say "ERROR: 'claude' CLI not on PATH — cannot run agent driver. Re-run with --shell, or fix PATH in the plist."
    exit 1
  fi
  PROMPT="You are running the weekly Security-Lab episode on Veera's Mac. Target episode: episodes/$SLUG.
Open episodes/$SLUG/lab/RUN.md and follow it EXACTLY. Honesty rules are non-negotiable:
if a guard/tool won't build or its model won't load, it is NOT EVALUATED — never record catch/miss
numbers for something that didn't actually run, and never hand-edit artifacts. HF_TOKEN and
GUARDRAILS_TOKEN are already exported into your environment (may be empty — if so, run the tools that
don't need them and mark the rest NOT EVALUATED). If a single tool fights you for more than ~3 fix
attempts, move on and report it NOT EVALUATED. Only switch to a *-wip branch if RUN.md says to AND
'git status' is clean. Benign payloads only; keep labnet no-egress. Do NOT push, publish, fill
POST.md, or merge branches. When artifacts/findings.csv and artifacts/metrics.csv exist, report:
which tools ran vs NOT EVALUATED (one line each + why), the findings table, metrics highlights, exact
versions/models, and any build fix you made. Then stop."
  say "agent driver: claude -p (following $SLUG/lab/RUN.md)"
  ( cd "$REPO" && claude -p "$PROMPT" --permission-mode acceptEdits ) 2>&1 | tee -a "$LOG"
  say "agent driver exit=${PIPESTATUS[0]}"
fi

say "===== weekly_run done ====="
