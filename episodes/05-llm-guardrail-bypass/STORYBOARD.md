# Episode 05 — Storyboard
## "I Hid a Jailbreak Inside an Emoji — Which AI Guardrail Caught It?"
### LLM guardrails: NVIDIA NeMo Guardrails vs Guardrails AI

Single source of truth for the blog and the video. Narration blocks are the exact words for
ElevenLabs (mirrored in `script.yaml`); on-screen actions map to the Docker lab + dashboards.

- **Target length:** 10–12 min video / ~1,900-word blog
- **Hook:** the freshest crack in AI safety right now — guardrails that fail not because the
  attack is clever, but because the guard's tokenizer and the model's tokenizer disagree.
- **News pegs:** 2025–2026 evasion research (arXiv 2504.11168) reporting character-injection and
  adversarial-ML attacks pushing evasion toward **~100%** against six major guardrails; Mindgard's
  "emoji smuggling" via Unicode **variation selectors** (guard tokenizer strips them, the model
  reads them); NeMo Guardrails **0.21.0** (May 2026) plus new NVIDIA jailbreak-detection NIM
  microservices; prompt injection still sits at **OWASP LLM01**.
- **Through-line:** one guarded chatbot, one benign canary secret, one jailbreak fired three ways
  (plain → character-injection → emoji-smuggled) — only the guardrail changes.
- **Lab:** 100% local Docker. No VMs. Isolated bridge network, **no internet egress**.

---

## Blog outline (maps 1:1 to video scenes)

1. What AI guardrails are, and the tokenizer gap that turned them into a new attack surface
2. The threat in plain terms: emoji smuggling, zero-width spaces, homoglyphs
3. The lab: a deliberately vulnerable chatbot + a benign canary secret, all in isolated Docker
4. Round 1 — Setup & coverage (what each guardrail actually inspects)
5. Round 2 — Detection (plain jailbreak vs character-injection vs emoji-smuggled)
6. Round 3 — Signal quality & speed (false positives, added latency)
7. Scorecard + verdict (who should run what, and the fix neither vendor prints)
8. Reproduce it yourself (repo + commit; benign canary only)

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:30)
**On screen:** A chat UI. A blocked request flashes red ("BLOCKED by guardrail"). Then the same
request, now wrapped in a smiling emoji, sails through green and the bot replies with a secret.
Title card: *"Same attack. One emoji. Guardrail blind."*
**Narration:**
> "Here's a jailbreak that shouldn't work anymore. I typed a request an AI is trained to refuse —
> and its guardrail caught it instantly. Then I hid the exact same request inside an emoji, and
> the guardrail waved it straight through to the model. That's not a clever prompt; it's a gap
> between two tokenizers. I put a benign secret behind a guarded chatbot and asked two of the
> biggest open-source AI guardrails — NVIDIA's NeMo Guardrails and Guardrails AI — one question:
> can you still catch an attack once it's wearing a disguise? No marketing — just what each one
> blocked."

### Scene 2 — The category & why it's a hot attack surface (0:30–1:30)
**On screen:** Simple animated diagram: user → **guardrail** (small classifier) → LLM. Zoom in
on the guardrail showing its own tokenizer; a second tokenizer sits inside the LLM. Highlight the
mismatch between them.
**Narration:**
> "Quick context. As soon as we started putting language models in front of customers, we bolted
> on guardrails — a filter that sits between the user and the model and blocks the obviously bad
> stuff: jailbreaks, prompt injection, toxic content. In 2026 that filter is everywhere, and it's
> usually a small classifier model making a fast yes-or-no call. But here's the catch researchers
> exposed this year: that classifier runs its own tokenizer before it decides, and that tokenizer
> doesn't always see text the same way the big model does. When those two disagree, you get a
> blind spot — and a whole new attack surface that lives in the gap between the guard and the
> thing it's guarding."

### Scene 3 — The threat, in plain terms (1:30–2:30)
**On screen:** Three labeled cards animating in: Emoji Smuggling (variation selectors),
Zero-Width Insertion, Homoglyph Swap. Show a string that looks like a single innocent emoji
expanding to reveal hidden instructions underneath.
**Narration:**
> "So how do you attack a blind spot? You write a prompt the model reads perfectly but the guard
> reads as gibberish. The cleanest version is emoji smuggling: you tuck your instructions between
> Unicode variation selectors — invisible modifier characters meant to tweak how an emoji looks.
> The guard's tokenizer strips them and sees an innocent emoji; the model reconstructs the hidden
> text and follows it. Same idea with zero-width spaces and homoglyphs — letters that look
> identical but carry different code points. Researchers reported these tricks pushing attack
> success rates to nearly one hundred percent against major guardrails. No exploit code, no CVE —
> just characters most systems were never taught to expect."

### Scene 4 — The lab & the rules (2:30–3:30)
**On screen:** Terminal: `docker compose up` bringing up the vulnerable chatbot, the guardrail
service, and a small attack runner on an isolated network. Quick pan over `lab/README.md`
highlighting "no egress" and the benign canary string.
**Narration:**
> "Here's the setup, and fairness is the whole point. Everything runs locally in Docker on one
> isolated network with no path to the internet. I stand up a deliberately vulnerable chatbot
> with a benign secret in its system prompt — a canary string it's told never to reveal — and put
> a guardrail in front of it. Then I fire the same attack three ways: the plain jailbreak, a
> character-injection version, and the emoji-smuggled version. The canary leaking is my ground
> truth that the attack got through. Same app, same secret, same three payloads — the only
> variable is which guardrail is doing the guarding."

### Scene 5 — Round 1: Setup & coverage (3:30–5:00)
**On screen:** Split terminal: installing and configuring NeMo Guardrails (a `config.yml` +
Colang rails) on the left, Guardrails AI (pulling validators from the Hub) on the right. A small
"what each one inspects" table fills in.
**Narration:**
> "Round one — getting each guardrail running and seeing what it actually inspects. NeMo
> Guardrails is NVIDIA's programmable framework: you write rails in a little language called
> Colang, and it can check inputs, dialog, and outputs, with a dedicated jailbreak-detection
> rail. Guardrails AI takes a different shape — a library of composable validators you pull from
> its Hub, including detectors for jailbreak and prompt injection that you wrap around the model's
> input and output. One is a conversation framework, the other a validator toolkit. Install times
> and exactly what each one guards are on screen; full commands are in the repo."

### Scene 6 — Round 2: The disguise & detection (5:00–7:30)
**On screen:** Left: the chatbot receiving the plain jailbreak (blocked), then the
character-injection and emoji variants. Right: each guardrail's verdict — block or pass — and the
reply pane, watching for the canary. Cut to the **normalized findings table** (caught / missed per
guardrail per variant).
**Narration:**
> "Now the real test. I send the plain jailbreak first, and both guardrails do their job — this
> is the easy case they're built for, and the better-tuned one flagged it with the rule it
> matched. Then I turn on the disguise. I run the character-injection version, then the
> emoji-smuggled one, and watch whether each guard still sees the attack or passes it to the model
> untouched. The moment a canary string comes back in the reply, that guard missed it. I
> normalized every result — plain, character-injection, emoji — into one table so it's genuinely
> apples to apples. Here's who caught what, and where the disguise won."

### Scene 7 — Round 3: Noise & cost (7:30–8:45)
**On screen:** False-positive column highlighted on a set of benign prompts; then an
added-latency / memory bar chart per guardrail.
**Narration:**
> "Detection isn't the whole story. A guard that blocks every message trains your users to hate
> it, so I also measured false positives on a set of perfectly normal prompts, plus the latency
> each one adds to every single request. NeMo Guardrails does more — multiple rails, dialog
> awareness — and that costs milliseconds and memory on each call. Guardrails AI's validators are
> lighter but only as strong as the ones you choose to switch on. Here's the added latency and the
> false-positive count for each, measured under the same load."

### Scene 8 — Scorecard & verdict (8:45–10:30)
**On screen:** The seven-criterion scorecard filling in; weighted totals animate; two "Use X if…"
cards, then a third card: "The fix: normalize before you guard."
**Narration:**
> "Same rubric every episode — install, detection, signal quality, performance, usability, docs,
> and value. And there's no single winner. Reach for NeMo Guardrails when you want programmable,
> multi-layer control and you're already in the NVIDIA ecosystem — the dialog rails catch things a
> single classifier can't. Reach for Guardrails AI when you want lightweight, composable
> validators you can drop into an existing app in an afternoon. But the honest headline is the one
> neither vendor prints: any guardrail that leans on a classifier can be blindsided by input its
> tokenizer doesn't understand, so you normalize and sanitize text before it ever reaches the
> guard — strip the invisible characters, then let the guardrail do its job."

### Scene 9 — Reproduce it / outro (10:30–11:30)
**On screen:** Repo + commit hash, `docker compose up`, the three attack variants side by side
(with the benign canary visible). End card: next episode teaser (proving the model you run is the
model you think) + subscribe.
**Narration:**
> "Everything here is reproducible — the vulnerable chatbot, the canary secret, the three attack
> variants, down to the commit hash. It's all benign: the 'secret' is just a canary token on an
> isolated network, so nothing real leaks and you can safely run it yourself and tell me if your
> guardrails hold up better than mine. Next episode I move upstream to the AI supply chain and put
> model-signing and provenance tools to the test — can you actually prove the model you're running
> is the one you think it is? If that sounds like your kind of trouble, subscribe, and I'll see
> you in the lab."

---

## Production notes
- **Voiceover:** narration blocks mirror `script.yaml`; ElevenLabs renders one MP3 per scene in
  your voice id.
- **Screen capture:** chatbot UI + guardrail CLIs/logs via Playwright or terminal cast; the lab
  is all local Docker so capture is easy.
- **Assembly:** same `video/` pipeline as prior episodes — pad each clip to its narration, burn
  captions, concat.
- **Ethics:** benign canary secret only; isolated no-egress network; responsible disclosure if a
  real bug surfaces; show the evasion technique conceptually, never ship a weaponized exploit.
