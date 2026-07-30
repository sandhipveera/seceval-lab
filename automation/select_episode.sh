#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# select_episode.sh — print the slug of THIS WEEK'S target episode, or nothing.
#
# Target = the highest-numbered episode that is:
#   * RUNNABLE  — its lab has a RUN.md AND a docker-compose.yml
#                 ("run only the one with RUN.md" — empty slates are skipped)
#   * UNRUN     — its POST.md still contains [FILL] placeholders. This is the
#                 reliable signal: STATUS.yaml lags, and artifacts/ is gitignored
#                 (so absent on a fresh clone even when the episode is done).
#
# Prints exactly the slug (e.g. 05-llm-guardrail-bypass) and exits 0, or prints
# nothing and exits 0 when there is no unrun runnable episode this week.
# ---------------------------------------------------------------------------
set -uo pipefail
REPO="${REPO:-/Users/veera/dev/prod-eval/docs}"
EPDIR="$REPO/episodes"

choice=""
# Highest number first. -V sorts 06 above 05; -r reverses to descending.
while IFS= read -r d; do
  slug=$(basename "$d")
  lab="$d/lab"
  [ -f "$lab/RUN.md" ] || continue                 # must have a run guide
  [ -f "$lab/docker-compose.yml" ] || continue     # must have a lab to bring up

  # Unrun = the blog draft still has [FILL] placeholders waiting on real numbers.
  if grep -q '\[FILL\]' "$d/POST.md" 2>/dev/null; then
    choice="$slug"; break
  fi
done < <(ls -1d "$EPDIR"/[0-9]*/ 2>/dev/null | sort -rV)

[ -n "$choice" ] && echo "$choice"
exit 0
