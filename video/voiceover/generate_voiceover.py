#!/usr/bin/env python3
"""
Generate per-scene voiceover MP3s from video/script.yaml using ElevenLabs (your voice id).

- Reads scenes[].narration and the voice block from script.yaml
- Calls the ElevenLabs text-to-speech REST API once per scene
- Writes build/audio/<scene_id>.mp3 and a build/manifest.json with measured durations
  (durations are what the assembler uses to pad each video clip to the narration length)

Env (see video/.env.example):
  ELEVENLABS_API_KEY   required
  ELEVENLABS_VOICE_ID  required (your cloned voice id)

Usage:
  python3 generate_voiceover.py --script ../script.yaml --out ../build
"""
import argparse, json, os, re, sys, wave, contextlib, subprocess, shutil
from pathlib import Path

try:
    import yaml, requests
except ImportError:
    sys.exit("pip install pyyaml requests  (see video/requirements.txt)")

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def expand_env(value: str) -> str:
    """Replace ${VAR} with environment values."""
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), value or "")


def mp3_duration_seconds(path: Path) -> float:
    """Probe duration with ffprobe; fall back to 0 if unavailable."""
    if not shutil.which("ffprobe"):
        return 0.0
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return round(float(out.stdout.strip()), 3)
    except ValueError:
        return 0.0


def synth(scene_id: str, text: str, voice: dict, out_dir: Path) -> Path:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = expand_env(voice.get("voice_id", "")) or os.environ.get("ELEVENLABS_VOICE_ID")
    if not api_key:
        sys.exit("ELEVENLABS_API_KEY not set")
    if not voice_id:
        sys.exit("ELEVENLABS_VOICE_ID not set (your cloned voice id)")

    payload = {
        "text": text.strip(),
        "model_id": voice.get("model_id", "eleven_multilingual_v2"),
        "voice_settings": {
            "stability": voice.get("stability", 0.45),
            "similarity_boost": voice.get("similarity_boost", 0.80),
            "style": voice.get("style", 0.0),
            "use_speaker_boost": True,
        },
    }
    # Optional speaking rate (supported on newer models); harmless if ignored.
    if voice.get("speed", 1.0) != 1.0:
        payload["voice_settings"]["speed"] = voice["speed"]

    url = API.format(voice_id=voice_id)
    headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        sys.exit(f"ElevenLabs error {resp.status_code} for {scene_id}: {resp.text[:300]}")

    out_path = out_dir / f"{scene_id}.mp3"
    out_path.write_bytes(resp.content)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="../script.yaml")
    ap.add_argument("--out", default="../build")
    ap.add_argument("--only", help="comma-separated scene ids to (re)render")
    args = ap.parse_args()

    script = yaml.safe_load(Path(args.script).read_text())
    voice = script.get("voice", {})
    out_root = Path(args.out)
    audio_dir = out_root / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    only = set(s.strip() for s in args.only.split(",")) if args.only else None
    manifest = {"episode": script["episode"], "scenes": []}

    for scene in script["scenes"]:
        sid = scene["id"]
        if only and sid not in only:
            continue
        print(f"[voiceover] {sid} …", flush=True)
        mp3 = synth(sid, scene["narration"], voice, audio_dir)
        dur = mp3_duration_seconds(mp3)
        manifest["scenes"].append({
            "id": sid,
            "audio": str(mp3.relative_to(out_root)),
            "duration": dur,
            "narration": " ".join(scene["narration"].split()),
            "action": scene.get("action", {}),
        })
        print(f"           -> {mp3.name}  ({dur}s)")

    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[voiceover] wrote {out_root/'manifest.json'} ({len(manifest['scenes'])} scenes)")


if __name__ == "__main__":
    main()
