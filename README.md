# Security Lab — AI Security Product Evaluations

**Built by [AccessQuint](https://accessquint.com)** · Independent, reproducible, benign-canary evaluations of AI/ML security tooling.

A reproducible content engine for a cybersecurity blog + YouTube series. Each episode is a
hands-on, head-to-head evaluation of the latest AI-security tools, tested **locally in Docker**,
with captured evidence and a public lab anyone can re-run. Voiceover in your own (ElevenLabs)
voice; screen capture + assembly automated.

> New here? Go straight to **[SETUP.md](SETUP.md)** for the step-by-step.

## Featured — Episode 02: 4 AI Model Scanners vs. 1 Hidden Payload

![Detection scorecard: four AI model scanners (picklescan, ModelScan, ModelAudit, fickling) vs. four evasion variants of one benign-canary payload, tested in an isolated lab. ModelAudit and fickling caught all four; picklescan 3/4; ModelScan 2/4; zero false positives on the clean set.](episodes/02-model-scanner-bypass/assets/scorecard.png)

Can a malicious model file pass a scanner and still run code? I hid a **benign** canary payload in a
pickle-based model, wrapped it in four evasion variants, and ran four scanners at it. Two caught
everything; two missed live payloads — and the most interesting failure was a scanner that never even
opened files it didn't recognize by extension. **[Read the full teardown →](episodes/02-model-scanner-bypass/POST.md)**

*Independent research · benign, isolated, no-egress lab · product names are trademarks of their
respective owners, used nominatively; no affiliation or endorsement.*

## Layout

```
README.md            This file
SETUP.md             Step-by-step setup & run order  ← start here
EPISODE_BACKLOG.md   Ordered queue of episodes (traction-ranked)
Makefile             Task runner (make help)
framework/           Reusable across episodes: evaluation template, scorecard rubric, safety
video/               Voiceover (ElevenLabs) + recording (Playwright) + assembly (ffmpeg)
episodes/            One folder per episode (the weekly task delivers here)
  01-mcp-agent-security/
    STATUS.yaml      new | in_production | published  ← pickup signal
    STORYBOARD.md    blog outline + 9-scene video script (source of truth)
    script.yaml      machine-readable twin for the video pipeline
    POST.md          blog draft (numbers as [FILL] until a real run)
    YOUTUBE.md       titles, description, chapters, tags
    lab/             this episode's Docker lab (compose + build contract + scripts)
extras/              Optional: original vSphere/Terraform + IDS episode (not needed for Docker)
```

## How it runs each week

A scheduled task ("weekly-episode-storyboard") pulls the next unchecked item from
`EPISODE_BACKLOG.md`, researches a fresh angle, and **delivers a complete episode package into
`episodes/<NN>-<slug>/` with `STATUS: new`**. Your tooling picks up any episode whose
`STATUS.yaml` says `new`; advance it to `in_production` → `published` as you work it, and the
task will never overwrite it.

## Per episode, your workflow

1. Build the episode's Docker lab and run the evaluation (see the episode's `lab/CLAUDE_CODE_BUILD.md`).
2. Capture results into the episode's `lab/artifacts/` (normalized findings + metrics CSVs).
3. Fill the `[FILL]` placeholders in `POST.md` and the metric/scorecard cards from real artifacts.
4. Generate voiceover + record + assemble the video (`video/`).
5. Publish; flip `STATUS.yaml` to `published`.

## Ground rules (every episode)

- Same fixed 7-criterion scorecard (`framework/SCORECARD.md`).
- Same target, same attack, same clean container state — only the tool under test changes.
- Isolated Docker network with **no internet egress**; **benign/canary payloads only**;
  responsible disclosure; review each tool's license before publishing benchmarks
  (`framework/SAFETY.md`).
