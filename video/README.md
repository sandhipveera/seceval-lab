# Video Production Pipeline

Turns one `script.yaml` into a finished episode: **ElevenLabs** narrates each scene in *your*
voice, **Playwright** records the web dashboards, **asciinema** records terminal scenes, and
**ffmpeg** syncs picture to narration, burns captions, and concatenates.

The storyboard (`evaluations/<slug>/STORYBOARD.md`) is the human-readable source; `script.yaml`
is its machine-readable twin (narration text is identical).

## Pipeline

```
script.yaml ──► generate_voiceover.py ──► build/audio/<scene>.mp3  + build/manifest.json
                                                     │ (per-scene durations)
                          ┌──────────────────────────┼───────────────────────────┐
                          ▼                           ▼                           ▼
              record_scenes.js (Playwright)   record_terminal.sh (asciinema)   make_captions.py
              build/video/<scene>.webm        build/video/<scene>.webm         build/captions.srt
                          └──────────────────────────┼───────────────────────────┘
                                                     ▼
                                          build_video.sh (ffmpeg)
                                          build/<slug>.mp4
```

Key idea: **the voiceover is recorded first** and its measured duration (in `manifest.json`)
drives how long each video clip is padded/trimmed — so audio and picture always line up.

## One-time setup

```bash
cd video
cp .env.example .env          # add ELEVENLABS_API_KEY + your ELEVENLABS_VOICE_ID
pip install -r requirements.txt
npm install && npx playwright install chromium
# terminal scenes also need: asciinema (pip) + agg (cargo install --git github.com/asciinema/agg)
# system: ffmpeg, ffprobe, jq
```

Your **voice id**: in `script.yaml` the voice block reads `voice_id: "${ELEVENLABS_VOICE_ID}"`,
so just set it in `.env`. (Find/create your cloned voice in the ElevenLabs Voice Lab; the id is
the string in the voice's URL / API list.)

## Run it (from `video/`)

```bash
# 1. Narration in your voice + manifest with real durations
python3 voiceover/generate_voiceover.py --script ./script.yaml --out ./build

# 2. Captions timed to the narration
python3 assemble/make_captions.py ./build

# 3. Record web dashboards / title cards
node record/record_scenes.js --manifest ./build/manifest.json --out ./build/video

# 4. Record terminal scenes (run the real lab commands so the footage is real)
record/record_terminal.sh lab_bringup "make -C .. up && make -C .. targets-up"
record/record_terminal.sh install_all   # interactive: run the three install.sh, then exit

# 5. Assemble final mp4 (synced to narration, captions burned in)
assemble/build_video.sh ./build
# -> build/<slug>.mp4
```

Or use the repo Make targets: `make voiceover`, `make record`, `make video` (see root Makefile).

## Notes

- **Scene types** in `script.yaml`: `browser` (Playwright records a URL — dashboard or a local
  HTML card in `assets/`) and `terminal` (asciinema cast → mp4).
- **Interaction routines:** `record_scenes.js` has named routines (e.g. `evebox_walkthrough`)
  referenced by `action.script` to make a dashboard *do something* on camera. Add your own.
- **Title/diagram cards:** drop HTML in `assets/` (e.g. `topology.html`, `scorecard.html`) and
  point a scene's `action.url` at `file://${ASSETS}/<card>.html`. A `title_cold_open.html`
  sample is included.
- **Re-render one scene:** `generate_voiceover.py --only s6_detection`, then re-record/assemble.
- **Keep `.env` out of git** (already gitignored). Never commit your API key or voice id.
- ElevenLabs commercial use + voice cloning consent: only clone/use a voice you're entitled to
  (your own). Check current ElevenLabs terms before publishing monetized content.
