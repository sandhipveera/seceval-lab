#!/usr/bin/env python3
"""Build a single SRT from build/manifest.json (one cue per scene, timed to narration)."""
import json, sys
from pathlib import Path

def ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"

def main():
    build = Path(sys.argv[1] if len(sys.argv) > 1 else "../build")
    man = json.loads((build / "manifest.json").read_text())
    out = build / "captions.srt"
    t = 0.0
    lines = []
    for i, sc in enumerate(man["scenes"], 1):
        dur = sc.get("duration") or sc.get("action", {}).get("duration_hint", 5)
        lines += [str(i), f"{ts(t)} --> {ts(t + dur)}", sc["narration"], ""]
        t += dur
    out.write_text("\n".join(lines))
    print(f"[captions] wrote {out} ({len(man['scenes'])} cues, {t:.0f}s total)")

if __name__ == "__main__":
    main()
