# Episode 02 — Storyboard
## "I Hid Malware in an AI Model — Which Scanner Caught It?"
### Model-file supply chain: picklescan vs ModelScan vs ModelAudit vs fickling

Single source of truth for the blog and the video. Narration blocks are the exact words for
ElevenLabs (mirrored in `script.yaml`); on-screen actions map to the Docker lab + dashboards.

- **Target length:** 10–12 min video / ~1,900-word blog
- **Hook:** in December 2025, JFrog disclosed **three critical zero-days in picklescan**
  (CVE-2025-10155 / -10156 / -10157, each **CVSS 9.3**) — the exact scanner Hugging Face runs on
  every upload — all fixed in **0.0.31**. The "unscannable model file" is having a moment.
- **News pegs:** JFrog's three picklescan CVEs (fixed in 0.0.31, disclosed Dec 2025); the
  academic "Art of Hide and Seek" paper reporting an **89% bypass rate** against the best scanner
  across 22 model-loading paths (Aug 2025); ReversingLabs' **nullifAI** 7z/broken-pickle bypass
  found live on Hugging Face (Feb 2025); Trail of Bits' rewritten **fickling** allowlist scanner
  (Sep 2025); Promptfoo open-sourcing **ModelAudit** and claiming wider coverage than ModelScan.
- **Through-line:** one benign-canary malicious model file, same payload, same clean container —
  only the scanner changes.
- **Lab:** 100% local Docker. No VMs. Isolated bridge network, **no internet egress**.

---

## Blog outline (maps 1:1 to video scenes)

1. Why the model file itself became a hot supply-chain attack surface (pickle = arbitrary code)
2. The threat in plain terms: pickle deserialization, blocklist evasion, broken/renamed archives
3. The lab: one benign-canary malicious model file + four scanners, all in isolated Docker
4. The lab & the rules that keep it fair (same file, same payload, same clean state)
5. Round 1 — Setup & coverage (formats each scanner even looks at)
6. Round 2 — Detection (does it flag the payload — plain, obfuscated, renamed, broken archive?)
7. Round 3 — Noise & cost (false positives on clean models, scan time)
8. Scorecard + verdict (who to run in CI, who to run for depth, and why you layer them)
9. Reproduce it yourself (repo + commit; benign canary only)

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:30)
**On screen:** A model file (`pytorch_model.bin`) being downloaded and loaded; a green
"scan passed" checkmark, then a red overlay showing a shell popping the moment it loads. Title
card: *"This AI model passed the scanner. It still ran my code."*
**Narration:**
> "This AI model file passed the security scanner — and then it ran my code anyway. That's not a
> hypothetical: in December, researchers dropped three critical zero-days in picklescan, the exact
> tool Hugging Face runs on every model you download. So I built a malicious model file with a
> harmless canary payload, and asked four different scanners a simple question: can you catch what's
> hiding inside? No marketing — just what each one flagged, and what walked right past it."

### Scene 2 — The category & why it's hot (0:30–1:30)
**On screen:** Simple diagram: a `.bin` / `.pt` / `.pkl` file cracked open to reveal a pickle
opcode stream with a `REDUCE` calling `os.system`. Caption: "loading the model = running its code."
**Narration:**
> "Here's the uncomfortable part almost nobody tells you. Most AI models are shipped as pickle
> files — Python's built-in serialization format. And pickle isn't just data; it's a tiny program.
> When you load the model, that program runs. So a model file can execute arbitrary code the moment
> it's opened, before a single prediction. Roughly forty-five percent of popular models on Hugging
> Face still use this format. The scanner between you and that code is usually picklescan — which
> is exactly why breaking it is such a big deal right now."

### Scene 3 — The threat, in plain terms (1:30–2:30)
**On screen:** Three labeled cards animating in: Blocklist Evasion, Renamed / Broken Archive,
Deep-Import Bypass. Show a `.pkl` renamed to `.bin`; a 7z-compressed archive; `asyncio.unix_events`
sneaking past a check for `asyncio`.
**Narration:**
> "The bypasses are almost embarrassingly clever. One: picklescan uses a blocklist of dangerous
> functions, so attackers just import a submodule the list doesn't name — the payload's the same,
> the string doesn't match. Two: rename the file, or compress it with 7z instead of zip, and the
> scanner doesn't even recognize it as a model to open. Three: put a broken opcode after your
> payload — it runs first, then the scanner chokes on the error and reports nothing. Same malware,
> four different ways to make the scanner look the other way."

### Scene 4 — The lab & the rules (2:30–3:30)
**On screen:** Terminal: `docker compose up` bringing up the canary sink and the four scanner
containers on an isolated network. Quick pan over `lab/README.md` highlighting "no egress" and
"benign canary."
**Narration:**
> "Here's the setup, and fairness matters. Everything runs locally in Docker on one isolated
> network with no path to the internet — so nothing actually leaves. I build one malicious model
> file whose payload does exactly one thing: touch an in-network canary. If the canary logs a hit,
> the code ran. Then every scanner inspects the exact same file, in the same clean container state.
> Same model, same payload — the only variable is the tool doing the catching."

### Scene 5 — Round 1: Setup & coverage (3:30–5:00)
**On screen:** Split terminal: `pip install` for picklescan, ModelScan, ModelAudit, and fickling,
then `--version` for each. A "what each one inspects" table fills in (formats, opcode analysis,
allowlist vs blocklist).
**Narration:**
> "Round one — getting each scanner running and seeing what it even looks at. picklescan is the
> lightweight default, a blocklist of dangerous imports. ModelScan, from Protect AI, scans several
> serialization formats and is what a lot of pipelines standardized on. ModelAudit, Promptfoo's
> newer open-source scanner, claims the widest coverage — dozens of formats and opcode-level
> analysis. And fickling, from Trail of Bits, flips the model entirely: instead of a blocklist of
> bad things, it uses an allowlist of known-safe imports and blocks everything else. Install times
> and coverage are on screen; full commands are in the repo."

### Scene 6 — Round 2: The payload & detection (5:00–7:30)
**On screen:** Left: the malicious model file variants (plain, deep-import, renamed `.bin`, broken
archive). Right: each scanner's verdict per variant. Cut to the **normalized findings table**
(caught / missed per scanner, per variant).
**Narration:**
> "Now the real test. I run every scanner against the same file, then against three evasive
> variants — a deep-import that dodges the blocklist, a pickle renamed to a PyTorch extension, and a
> broken archive. The plain payload is the easy case; most tools catch that. The interesting story
> is the evasions. A blocklist that checks for an exact import name gets walked past by a submodule
> it never listed. A scanner that trusts the file extension parses the renamed file wrong and
> reports nothing. And the allowlist approach behaves very differently — it doesn't care what the
> import is called, only whether it's on the safe list. I normalized every result into one table so
> it's apples to apples. Here's who caught what."

### Scene 7 — Round 3: Noise & cost (7:30–8:45)
**On screen:** False-positive column highlighted (scanners flagging a legitimate clean model);
then a scan-time bar chart per tool across file sizes.
**Narration:**
> "Detection isn't the whole story. A scanner that screams at every legitimate model trains you to
> ignore it — and an allowlist that blocks unfamiliar-but-safe imports can do exactly that. So I ran
> each tool against a set of clean, benign models and counted the false alarms, and I timed every
> scan across small and large files. Deeper analysis costs time; a stricter allowlist costs
> friction. Here's the price of each, measured under the same load."

### Scene 8 — Scorecard & verdict (8:45–10:30)
**On screen:** The seven-criterion scorecard filling in; weighted totals animate; four
"Use X if…" cards.
**Narration:**
> "Same rubric every episode — install, detection, signal quality, performance, usability, docs,
> and value. And like everything in this space, there's no single winner. picklescan is the fast
> default, but this year proved a blocklist alone is not enough — patch it and don't rely on it
> solo. ModelScan is a solid pipeline standard with broad format support. ModelAudit goes widest and
> deepest and is the one I'd reach for when I actually want to find things. And fickling's allowlist
> is the strongest posture against unknown tricks, at the cost of tuning. For anything you didn't
> build yourself, the honest answer is layer them, and update relentlessly."

### Scene 9 — Reproduce it / outro (10:30–11:30)
**On screen:** Repo + commit hash, `docker compose up`, the benign model-file builder (with the
canary payload highlighted). End card: next episode teaser (LLM red-team showdown) + subscribe.
**Narration:**
> "Everything here is reproducible — the malicious model file, the evasive variants, the scanner
> commands, down to the commit hash. It's all benign: the payload just trips a canary on an
> isolated network, so nothing leaves your machine and you can safely run it yourself and tell me if
> your results differ. Next episode I put the LLM red-team frameworks head to head — Garak versus
> PyRIT versus Promptfoo — and see which one actually breaks a model. If that sounds like your kind
> of trouble, subscribe, and I'll see you in the lab."

---

## Production notes
- **Voiceover:** narration blocks mirror `script.yaml`; ElevenLabs renders one MP3 per scene in
  your voice id.
- **Screen capture:** scanner CLIs + the findings dashboard via Playwright or terminal cast; the
  lab is all local Docker so capture is easy.
- **Assembly:** same `video/` pipeline as episode 01 — pad each clip to its narration, burn
  captions, concat.
- **Ethics:** benign canary payload only; isolated no-egress network; responsible disclosure if a
  real bug surfaces; show the technique conceptually, never ship a weaponized exploit.
