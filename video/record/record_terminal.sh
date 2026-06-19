#!/usr/bin/env bash
# Record a terminal "cast" for a scene and convert it to mp4 for the video.
# Terminal scenes in script.yaml use:  action: { type: terminal, cast: <name> }
# This wraps asciinema (record) + agg (render to gif) + ffmpeg (gif -> mp4).
#
# Usage:
#   record_terminal.sh <cast_name> [command...]
#   # interactive (you drive it):   record_terminal.sh install_all
#   # scripted (replays a command):  record_terminal.sh lab_bringup "make up && make targets-up"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build"
CASTS="$BUILD/casts"; VID="$BUILD/video"
mkdir -p "$CASTS" "$VID"
NAME="${1:?cast name}"; shift || true
CMD="${*:-}"

command -v asciinema >/dev/null || { echo "install asciinema (pip install asciinema)"; exit 1; }

CAST="$CASTS/$NAME.cast"
echo "[term] recording $NAME -> $CAST"
if [ -n "$CMD" ]; then
  asciinema rec --overwrite -c "bash -lc '$CMD'" "$CAST"
else
  echo "      (interactive — type 'exit' when done)"
  asciinema rec --overwrite "$CAST"
fi

# Render cast -> gif -> mp4 (agg from the asciinema project; ffmpeg for mp4).
if command -v agg >/dev/null; then
  agg --theme monokai "$CAST" "$VID/$NAME.gif"
  ffmpeg -y -i "$VID/$NAME.gif" -movflags faststart -pix_fmt yuv420p \
    -vf "scale=1920:-2:flags=lanczos" "$VID/$NAME.webm"
  echo "[term] -> $VID/$NAME.webm"
else
  echo "[term] agg not found — keep $CAST and render later (cargo install --git https://github.com/asciinema/agg)"
fi
