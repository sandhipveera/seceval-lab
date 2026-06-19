# Claude Code Prompt — Video Production

Paste this after the main lab is built and you've run an evaluation. It tells Claude Code to
finish the video pipeline and produce Episode 01 from the storyboard + captured artifacts.

---

```
Produce the video for evaluations/ids-suricata-vs-zeek-vs-snort using the pipeline in video/.
The storyboard (evaluations/<slug>/STORYBOARD.md) and video/script.yaml are the source of
truth — narration text must stay identical between them.

Stack (already scaffolded, finish/run it):
- ElevenLabs TTS in MY cloned voice. The voice id comes from ELEVENLABS_VOICE_ID in video/.env;
  script.yaml references it as ${ELEVENLABS_VOICE_ID}. Never hard-code or commit the key/id.
- Playwright (Chromium) records browser scenes: IDS dashboards (EveBox etc.) and local HTML
  title/diagram cards in video/assets/.
- asciinema records terminal scenes; render to mp4 with agg + ffmpeg.
- ffmpeg assembles: pad/trim each clip to its narration duration (from build/manifest.json),
  burn captions.srt, concat with intro/outro.

Do this:
1. Generate the remaining scene asset cards as 1920x1080 dark-theme HTML in video/assets/
   (topology.html, contenders.html, metrics.html, scorecard.html, outro.html), matching the
   look of the included title_cold_open.html. metrics.html and scorecard.html should render
   REAL data — read the eval's artifacts/<run>/metrics.csv and the filled scorecard, and draw
   them with inline Chart.js (CDN). No fabricated numbers.
2. Run voiceover generation (make voiceover) to produce build/audio/*.mp3 + manifest + captions.
3. Record browser scenes (make record). For s6_detection, drive the real EveBox dashboard with
   an interaction routine so alerts are visibly populating; if the live dashboard isn't up, fall
   back to a recorded session capture.
4. Record the terminal scenes for real: lab bring-up and the three install.sh runs, timed.
5. Assemble (make video) and verify build/<slug>.mp4 plays, audio is in my voice, picture is
   synced to narration, and captions are correct.

Constraints:
- Only use my own voice for cloning; respect ElevenLabs terms for monetized content.
- All on-screen data must come from real captured artifacts — never invent metrics or alerts.
- Keep .env and any secrets out of git.

Verification before you call it done:
- build/<slug>.mp4 exists, ~9–11 min, 1920x1080.
- Each scene's audio length matches its video length (no drift); spot-check 3 scenes.
- Caption text matches narration; timing aligns within ~0.5s.
- metrics.html / scorecard.html numbers equal the source CSV / scorecard.

Then give me: the final mp4 path, a thumbnail frame suggestion, the blog post exported from the
storyboard, and a YouTube title + description + chapter timestamps derived from the scene cuts.
```

---

## What you provide
- `video/.env` with `ELEVENLABS_API_KEY` and your `ELEVENLABS_VOICE_ID`
- A completed run of the IDS eval so `artifacts/<run>/metrics.csv` + filled scorecard exist
- Local tools: `ffmpeg`, `ffprobe`, `jq`, `node`+Playwright, `python3`, `asciinema`, `agg`
