#!/usr/bin/env bash
# Assemble the final episode: per scene, mux the recorded clip with its ElevenLabs narration,
# pad/trim video to the audio length, then concat all scenes, burn captions, add intro/outro.
#
# Inputs (produced by earlier steps):
#   build/manifest.json            (scene order + durations + audio paths)
#   build/audio/<scene>.mp3        (ElevenLabs voiceover, your voice id)
#   build/video/<scene>.webm       (Playwright/asciinema recording)
#   build/captions.srt             (from make_captions.py)
# Output:
#   build/<slug>.mp4
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="${1:-$HERE/../build}"
ASSETS="$HERE/../assets"
MAN="$BUILD/manifest.json"
WORK="$BUILD/work"; mkdir -p "$WORK"
command -v ffmpeg >/dev/null || { echo "ffmpeg required"; exit 1; }
command -v jq >/dev/null || { echo "jq required"; exit 1; }

SLUG=$(jq -r '.episode.slug' "$MAN")
RES=$(jq -r '.episode.resolution' "$MAN"); FPS=$(jq -r '.episode.fps // 30' "$MAN")
W=${RES%x*}; H=${RES#*x}

concat_list="$WORK/concat.txt"; : > "$concat_list"

# --- per-scene: normalize video to audio duration, attach narration ---
n=$(jq '.scenes | length' "$MAN")
for i in $(seq 0 $((n-1))); do
  sid=$(jq -r ".scenes[$i].id" "$MAN")
  dur=$(jq -r ".scenes[$i].duration // (.scenes[$i].action.duration_hint // 6)" "$MAN")
  audio="$BUILD/$(jq -r ".scenes[$i].audio" "$MAN")"
  clip=$(ls "$BUILD/video/$sid".* 2>/dev/null | head -1 || true)

  out="$WORK/$sid.mp4"
  if [ -n "$clip" ] && [ -f "$clip" ]; then
    # real recording: loop-pad last frame / trim to audio length, attach narration
    ffmpeg -y -i "$clip" -i "$audio" \
      -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,fps=${FPS},tpad=stop_mode=clone:stop_duration=${dur}" \
      -t "$dur" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "$out"
  else
    # no recording for this scene: fall back to a solid slate so the cut still works
    ffmpeg -y -f lavfi -i "color=c=0x0b0f14:s=${W}x${H}:d=${dur}:r=${FPS}" -i "$audio" \
      -vf "drawtext=text='${sid}':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" \
      -t "$dur" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "$out"
  fi
  echo "file '$out'" >> "$concat_list"
  echo "[assemble] scene $sid ($dur s) -> $out"
done

# --- concat scenes ---
joined="$WORK/joined.mp4"
ffmpeg -y -f concat -safe 0 -i "$concat_list" -c copy "$joined" 2>/dev/null \
  || ffmpeg -y -f concat -safe 0 -i "$concat_list" -c:v libx264 -c:a aac "$joined"

# --- burn captions (soft-fail if none) ---
final="$BUILD/$SLUG.mp4"
if [ -f "$BUILD/captions.srt" ]; then
  ffmpeg -y -i "$joined" -vf "subtitles=$BUILD/captions.srt:force_style='FontSize=22,PrimaryColour=&H00FFFFFF,BorderStyle=3,Outline=1'" \
    -c:v libx264 -pix_fmt yuv420p -c:a copy "$final"
else
  cp "$joined" "$final"
fi

echo "[assemble] DONE -> $final"
