# Episode 06 — Storyboard
## "I Attacked the Gateway Guarding My LLM — Which One Held?"
### AI gateway / LLM-proxy security: LiteLLM vs Portkey vs Bifrost

Single source of truth for the blog and the video. Narration blocks are the exact words for
ElevenLabs (mirrored in `script.yaml`); on-screen actions map to the Docker lab + dashboards.

- **Target length:** 11–12 min video / ~1,800-word blog
- **Hook:** the AI gateway is sold as the security control for LLM traffic — and in 2026 it
  became the attack surface. So this episode tests both directions at once.
- **News pegs (2026, all verified):**
  - **LiteLLM PyPI supply-chain compromise** — versions 1.82.7 / 1.82.8 published 24 Mar 2026,
    live ~40 minutes; three-stage payload (credential harvester across 50+ secret categories,
    Kubernetes lateral-movement kit, persistent backdoor), exfil to a domain registered a day
    earlier; attributed to TeamPCP, who had previously compromised Trivy and Checkmarx KICS.
    LiteLLM is pulled ~3.4M times/day.
  - **CVE-2026-42208** — pre-auth SQL injection in LiteLLM Proxy's API-key verification path
    (unparameterised query reached via the `Authorization` header on any LLM route). CVSS 9.3;
    affects 1.81.16–1.83.6; fixed in 1.83.7-stable (19 Apr 2026); first exploitation attempt
    ~26–36 h after the advisory was indexed; added to CISA KEV 8 May 2026. Chained with
    CVE-2026-42203 (SSTI) and CVE-2026-42271 (command injection in MCP endpoints) → RCE.
  - **Portkey** — fully open-sourced the gateway (Apache 2.0) in March 2026, moving governance,
    observability and its guardrails library out from behind the SaaS; Palo Alto Networks
    announced intent to acquire (30 Apr 2026), expected to close in PANW's fiscal Q4 2026.
- **Through-line:** one vulnerable LLM app, one stub model, the same six attacks and the same
  clean container state — only the gateway changes.
- **Lab:** 100% local Docker. Isolated bridge network, **no internet egress**, stub model
  provider in-network, benign canary secret.
- **Scope note (fair-test rule):** Cloudflare AI Gateway was in the backlog line-up and is **cut**
  — it is a hosted service and cannot run on a no-egress network, so it can't be held to the same
  clean-container-state rule. Flagged the same way Promptfoo was in episode 03.
- **Safety note:** the "gateway as target" axis is **posture, not payloads** — version/patch range
  checks, unauthenticated-reachability probes, and digest-pinning checks. No exploit for
  CVE-2026-42208 or any other advisory is written, shipped, or run.

---

## Blog outline (maps 1:1 to video scenes)

1. What an AI gateway is, and why 2026 turned it into a target
2. Two threats people keep mixing up: what the gateway should stop vs. the gateway as the way in
3. The lab: vulnerable app + stub model + canary sink, all isolated Docker
4. Round 1 — Setup & coverage (and why Cloudflare AI Gateway got cut)
5. Round 2 — Six attacks, and what each gateway caught
6. Round 2b — The gateway as target: posture, not payloads
7. Round 3 — Noise, and the tax on every single request
8. Scorecard, verdict, and reproduce it yourself

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:30)
**On screen:** A clean architecture diagram — app → gateway → model — then the gateway box turns
red and the arrow forks off to an attacker. Title card: *"The box guarding your LLM holds every
key you own."*
**Narration:**
> "Every request your app sends to a model probably goes through one box. An AI gateway. It's
> where you put your keys, your rate limits, your guardrails — it's the thing that's supposed to
> keep the model safe. In twenty twenty-six that box became a target. So I ran two tests at once.
> Can these gateways actually stop a prompt injection and a secret walking out the door? And how
> do they hold up when the attacker aims at the gateway itself? Three gateways, one vulnerable
> app, no marketing."

### Scene 2 — The category & why it's hot (0:30–1:30)
**On screen:** Animated diagram: many apps → one gateway → many providers; overlay callouts for
keys / logs / prompts concentrating in the middle. Then a 2026 timeline strip: Mar 24 supply
chain · Mar Portkey open-source · Apr CVE-2026-42208 · Apr 30 PANW–Portkey · May 8 CISA KEV.
**Narration:**
> "Here's the category. An AI gateway, or LLM proxy, sits between your application and every model
> provider. One OpenAI-compatible endpoint, and behind it your routing, fallbacks, budgets,
> logging — and increasingly, your guardrails. Which is a lovely idea: one chokepoint, one place
> to enforce policy. It's also a lovely idea for an attacker, because that same chokepoint sees
> every prompt, every response, and holds every provider key you own. Twenty twenty-six proved the
> point. LiteLLM, a proxy pulled roughly three-point-four million times a day, had two poisoned
> versions published to PyPI in March — live for about forty minutes, carrying a credential
> harvester, a Kubernetes lateral-movement kit, and a backdoor. A month later a
> pre-authentication SQL injection in its key-verification path, scored nine-point-three, went
> from advisory to real exploitation attempts in about a day, and landed on CISA's
> known-exploited list in May. Meanwhile Portkey open-sourced its entire gateway in March, and
> Palo Alto Networks moved to acquire it in April. The category is consolidating and getting shot
> at, at the same time."

### Scene 3 — The threats, in plain terms (1:30–2:40)
**On screen:** Two labeled columns animating in — *Threat 1: through the gateway* (prompt
injection, indirect injection, PII/secret egress) and *Threat 2: at the gateway* (supply chain,
pre-auth CVE, exposed admin API, unpinned image). Highlight that the second column is the one
nobody threat-modeled.
**Narration:**
> "So there are two threats here and people keep mixing them up. Threat one is what the gateway is
> meant to catch: someone talks your app into ignoring its instructions, or a secret rides out in
> a response — prompt injection and data egress. That's the guardrail's job. Threat two is the
> gateway as the way in. It holds every key. It usually has an admin API. It's a Python or Node
> service you pulled from a registry and probably pinned loosely. Compromise it and you don't need
> to jailbreak anything — you just read the traffic. The uncomfortable part is that most teams
> bought the gateway for threat one and never threat-modeled threat two. So I'm testing both."

### Scene 4 — The lab & the rules (2:40–3:40)
**On screen:** Terminal: `docker compose up` bringing up the stub model, the vulnerable chat app,
and the canary sink on an internal network. Quick pan over `lab/README.md` highlighting "no
egress" and "one gateway at a time."
**Narration:**
> "The setup, and fairness matters. Everything is local Docker on one network marked internal,
> with no route out — so nothing leaves and no real provider key is involved. In-network I run a
> stub model that speaks the OpenAI API and is deliberately gullible, a vulnerable chat app whose
> system prompt holds a benign canary secret, and a sink that stands in for the attacker's
> collection point. If that canary reaches the sink, the guardrail failed — that's my ground
> truth. Then one gateway at a time, from a clean container state, same app, same attacks, same
> order. Only the gateway changes."

### Scene 5 — Round 1: Setup & coverage (3:40–5:10)
**On screen:** Split terminal: `docker compose --profile litellm up`, then `--profile portkey`,
then `--profile bifrost`. A "what each one covers" grid fills in (guardrails built-in vs hook,
PII redaction, output scanning, admin auth default, license). A struck-through Cloudflare row
with the reason.
**Narration:**
> "Round one — install each one and see what it actually covers. LiteLLM is the default for
> self-hosters: a hundred-plus providers behind one endpoint, budgets, keys, and a guardrails hook
> you configure. Portkey went fully open source in March under Apache two-point-oh, and pushed
> what used to be paid — governance, observability, and its guardrails library — into the box you
> can run yourself; guardrails are first-class there rather than bolted on. Bifrost, from Maxim AI,
> is the performance play, written for very low overhead. I also wanted Cloudflare AI Gateway in
> this, and I cut it — it's a hosted service, so it can't run on a no-egress network, and testing
> it would break the fair-test rule this series lives by. Same reason Promptfoo got flagged in
> episode three. Install times and the coverage grid are on screen."

### Scene 6 — Round 2: The attacks & detection (5:10–7:50)
**On screen:** Left: the six attacks firing at the app in sequence. Right: each gateway's verdict
per attack (blocked / redacted / passed), then the canary sink's log. Cut to the **normalized
findings table**. Then the posture pass: version check, unauthenticated admin probe, digest-pinning
check — all read-only.
**Narration:**
> "Now the actual test. Six scenarios against each gateway. A direct injection telling the model
> to reveal its system prompt. An indirect one, hidden in a document the app retrieves. A request
> carrying fake personal data, to see if it gets redacted before it reaches the model. A response
> carrying the canary secret, to see if anything catches it on the way out. An obfuscated variant
> of the injection — base sixty-four and lookalike characters, the tokenizer-gap trick from
> episode five. And a clean set, to see what gets flagged that shouldn't. Then the second axis:
> the gateway as target. I do not ship exploits, so this is posture, not payloads — is the admin
> surface reachable without credentials from another container on the network, is the running
> version inside the patched range for the twenty twenty-six advisories, and are the image and its
> dependencies pinned by digest, which is the only thing that would have saved you in March.
> Everything normalizes into one findings table. Here's who caught what."

### Scene 7 — Round 3: Noise & cost (7:50–9:05)
**On screen:** False-positive column on the clean set highlighted; then p50 / p95 added-latency
bars, throughput, and memory per gateway — guardrails off vs on, side by side.
**Narration:**
> "Detection isn't the whole story. A guardrail that blocks legitimate traffic gets turned off
> within a week — so false positives on the clean set matter as much as catches. And this box is
> on the hot path for every single request, so its overhead is a tax you pay forever, not once. I
> measured added latency at the median and the tail, throughput under the same load, and memory
> per container, with guardrails off and then on — because the honest number is the cost of the
> protection, not the cost of the proxy. Here's what each one charged me."

### Scene 8 — Scorecard & verdict (9:05–10:45)
**On screen:** The seven-criterion scorecard filling in; weighted totals animate; three "Use X
if…" cards; a final card reading *"A gateway is infrastructure, not a security product."*
**Narration:**
> "Same seven criteria as every episode — install, detection, signal quality, performance,
> usability, docs, and value. And the same conclusion I keep arriving at: no single winner,
> because these three are optimizing for different things. Take LiteLLM if breadth of providers
> and cost control is the actual job, and treat its guardrails as a bonus — but pin it by digest,
> put its admin API behind auth, and watch its advisories like you'd watch a load balancer's. Take
> Portkey if you want guardrails to be the point rather than a hook, and the open-source release
> means you can now run that without the SaaS. Take Bifrost when the overhead is the deciding
> constraint and you're bringing your own policy layer. And whichever you pick, the real lesson of
> twenty twenty-six is that the gateway is infrastructure, not a security product you install and
> forget. It needs patching, pinning, and a blast radius."

### Scene 9 — Reproduce it / outro (10:45–11:45)
**On screen:** Repo + commit hash, `docker compose --profile <gateway> up`, the attack set file,
the canary definition. End card: next episode teaser (commercial AI firewalls) + subscribe.
**Narration:**
> "All of it reproduces — the vulnerable app, the stub model, the attack set, the gateway configs,
> down to the commit. It's benign by construction: the canary trips a sink on an isolated network,
> the posture checks read versions and reachability rather than firing exploits, and nothing here
> is weaponized. Run it and tell me where your numbers differ from mine — especially on the
> obfuscated case, because that's where I expect the most disagreement. Next episode I take the
> commercial AI firewalls — Lakera Guard, Prompt Security, Protect AI Guardian — and see whether
> paying changes the answer. Subscribe, and I'll see you in the lab."

---

## Production notes
- **Voiceover:** narration blocks mirror `script.yaml`; ElevenLabs renders one MP3 per scene in
  your voice id.
- **Screen capture:** gateway dashboards/CLIs + the attack runner via Playwright or terminal cast;
  the lab is all local Docker so capture is easy.
- **Assembly:** same `video/` pipeline — pad each clip to its narration, burn captions, concat.
- **Ethics:** benign canary payload only; isolated no-egress network; the gateway-as-target axis is
  read-only posture checking, never exploitation; responsible disclosure if a real bug surfaces;
  show technique conceptually, never ship a weaponized exploit.
- **Licensing:** review LiteLLM, Portkey (Apache 2.0) and Bifrost licenses for benchmark-publication
  terms before the numbers go public.
