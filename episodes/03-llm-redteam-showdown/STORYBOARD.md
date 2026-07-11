# Episode 03 — Storyboard
## "I Attacked My Own AI Agent — Which Red-Team Tool Broke It First?"
### LLM red-team showdown: Garak vs PyRIT vs Promptfoo

Single source of truth for the blog and the video. Narration blocks are the exact words for
ElevenLabs (mirrored in `script.yaml`); on-screen actions map to the Docker lab + dashboards.

- **Target length:** 10–12 min video / ~1,900-word blog
- **Hook:** LLM red-teaming just went *agentic* in 2026. In March, **OpenAI acquired Promptfoo**
  specifically to strengthen "agentic security testing." In May, **NVIDIA's Garak shipped an
  Agent-breaker probe** (v0.15.0) that tests the tools an LLM can call. And **Microsoft's PyRIT**
  now powers the Azure AI Foundry "AI Red Teaming Agent," with the Cloud Security Alliance
  publishing (June 2026) that *tool misuse is the test that matters*. The whole category pivoted
  from "jailbreak the chatbot" to "attack the agent." So I pointed all three at the same agent.
- **News pegs:** OpenAI → Promptfoo acquisition (Mar 9, 2026); Garak v0.15.0 Agent-breaker +
  multi-turn GOAT probe (May 2026); PyRIT inside Azure AI Foundry AI Red Teaming Agent + CSA's
  agentic-red-team evaluation (2026).
- **Through-line:** one deliberately vulnerable LLM agent, one benign canary tool it can be
  tricked into misusing, same attack scenarios — only the red-team framework changes.
- **Lab:** 100% local Docker. No VMs. Isolated bridge network, **no internet egress**.

---

## Blog outline (maps 1:1 to video scenes)

1. Cold open — I built an AI agent, then tried to break it three different ways
2. The category & why it's suddenly hot: automated LLM red-teaming went agentic in 2026
3. The threat in plain terms: jailbreaks, prompt injection, and tool misuse (the new one)
4. The lab & the fairness rules: one vulnerable agent, one canary tool, isolated Docker
5. Round 1 — Setup & coverage (what each framework installs and what attacks it ships with)
6. Round 2 — The core test (attack-success rate on the same agent + tool-misuse scenario)
7. Round 3 — Noise & cost (false alarms, run time, tokens/compute to drive the attacks)
8. Scorecard + verdict (who should reach for what, and why you layer them)
9. Reproduce it yourself (repo + commit; benign canary tool only)

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:30)
**On screen:** A friendly AI agent answering a normal question, then a red overlay as a crafted
message makes it call a tool it never should. Title card: *"I built an AI agent. Then I tried to
break it three different ways."*
**Narration:**
> "I built an AI agent — the helpful kind that can actually use tools on your behalf — and then I
> spent a week trying to break it. Not with one trick, but with three of the biggest automated
> red-team frameworks in the world: Garak from NVIDIA, PyRIT from Microsoft, and Promptfoo, which
> OpenAI just bought. Same agent, same weaknesses, same isolated lab. The only question: which one
> breaks it first, and which one tells you the most about *why*?"

### Scene 2 — The category & why it's hot (0:30–1:45)
**On screen:** A timeline animating in three 2026 headlines: "OpenAI acquires Promptfoo (Mar)",
"Garak ships Agent-breaker probe (May)", "PyRIT powers Azure AI Red Teaming Agent". Arrow from
"jailbreak the chatbot" → "attack the agent."
**Narration:**
> "First, why now. For two years, LLM red-teaming meant tricking a chatbot into saying something
> it shouldn't. In 2026 that changed. In March, OpenAI acquired Promptfoo — a red-team tool — and
> said out loud it was about agentic security testing. In May, NVIDIA's Garak shipped an
> Agent-breaker probe that goes after the tools an agent can call. And Microsoft's PyRIT became
> the engine behind Azure's AI Red Teaming Agent, while the Cloud Security Alliance published that
> for agents, tool misuse is the test that matters. The whole field pivoted from 'what can I make
> it say' to 'what can I make it do.' That's a much scarier question."

### Scene 3 — The threats, in plain terms (1:45–2:45)
**On screen:** Three labeled cards animating in: Jailbreak, Prompt Injection, Tool Misuse.
Highlight Tool Misuse — an agent tricked into calling a "send data" tool.
**Narration:**
> "Three failure modes matter here. A jailbreak talks the model out of its own safety rules — the
> classic 'ignore your instructions.' Prompt injection hides new instructions inside content the
> agent reads, like a web page or a document, so the attacker's words become the agent's orders.
> And tool misuse is the agentic one: you don't need the model to *say* anything bad, you just need
> it to *call the wrong tool* — read a file it shouldn't, or fire off a request that leaks data.
> The first two are about words. The third is about actions, and it's why red-teaming had to grow
> up this year."

### Scene 4 — The lab & the rules (2:45–3:45)
**On screen:** Terminal: `docker compose up` bringing up the vulnerable agent, its benign
canary tool, and a canary sink on an isolated network. Quick pan over `lab/README.md` highlighting
"no egress."
**Narration:**
> "Here's the setup, and fairness is the whole point. Everything runs locally in Docker on one
> isolated network with no path to the internet. I stand up a deliberately weak AI agent — thin
> safety rules and a tool it's allowed to call — plus a benign canary sink standing in for
> 'somewhere data could leak.' When the agent misuses the tool, it just trips the canary; nothing
> actually leaves the machine. Then each framework attacks the exact same agent from the exact
> same clean container state. Same target, same weaknesses — the only variable is the tool doing
> the attacking."

### Scene 5 — Round 1: Setup & coverage (3:45–5:15)
**On screen:** Split terminal: `pip install garak`, `pip install pyrit`, `npx promptfoo redteam`.
A "what each ships with" table fills in: probes/plugins, multi-turn support, agent/tool testing.
**Narration:**
> "Round one — installing each framework and seeing what attacks it brings out of the box. Garak is
> the scanner-style one: dozens of probes for jailbreaks, prompt injection, and leakage, and as of
> this spring an Agent-breaker probe aimed at tools. PyRIT is a toolkit, not a scanner — you compose
> orchestrators, converters, and scorers into multi-turn attack chains, which is exactly what you
> want for agents that hold a conversation. And Promptfoo is the developer-friendly one: a config
> file, dozens of vulnerability plugins, and attack strategies it can combine into thousands of test
> cases, wired for CI. Install times and coverage are on screen; full commands are in the repo."

### Scene 6 — Round 2: The core test (5:15–7:45)
**On screen:** Left: the agent under attack, a crafted multi-turn conversation nudging it toward
the canary tool. Right: each framework's output — attack-success rate, which scenarios landed.
Cut to the **normalized findings table** (attacks fired / succeeded per framework).
**Narration:**
> "Now the real test. I give each framework the same job: break this agent's safety rules, inject
> instructions through the content it reads, and get it to misuse its tool. Then I watch. Garak runs
> its probe battery and reports an attack-success rate per category, now with confidence intervals,
> so a jailbreak that works one time in ten shows up honestly. PyRIT shines on the multi-turn
> stuff — it patiently escalates across several messages, which is how the tool-misuse attack
> actually succeeds. Promptfoo generates a wide spread of variants fast and scores how often the
> agent fails. The interesting gaps are where an attack only lands after several turns, or only when
> it's hidden in a document — and a single-shot probe walks right past it. I normalized every result
> into one table so it's apples to apples. Here's who broke what."

### Scene 7 — Round 3: Noise & cost (7:45–9:00)
**On screen:** False-positive / false-success column highlighted; then a run-time and
tokens-per-run bar chart per framework.
**Narration:**
> "Breaking it isn't the whole story. A framework that screams 'jailbreak' at every refusal wastes
> your week chasing ghosts, and these attacks aren't free — every variant is model calls, which is
> real time and real tokens. Garak was thorough but the longest-running; PyRIT was the most precise
> on multi-turn but the most code to drive; Promptfoo was the fastest to a useful report but leaned
> on a judge model you have to trust. Here's the cost of each — run time, tokens, and how often each
> one cried wolf — measured under the same load."

### Scene 8 — Scorecard & verdict (9:00–10:45)
**On screen:** The seven-criterion scorecard filling in; weighted totals animate; three
"Use X if…" cards.
**Narration:**
> "Same rubric every episode — install, detection, signal quality, performance, usability, docs,
> and value. And like everything in this space, there's no single winner. Reach for Garak when you
> want a fast, broad scan you can run like a vulnerability scanner and drop into CI. Reach for PyRIT
> when you're serious about multi-turn and agent-specific attacks and you have engineers to compose
> them. And reach for Promptfoo when you want that middle ground — declarative config, strong
> reporting, and the fact that OpenAI now stands behind it. Honestly, for a real agent you'd layer
> them: Promptfoo or Garak in CI on every change, PyRIT for the deep pre-launch red-team."

### Scene 9 — Reproduce it / outro (10:45–11:45)
**On screen:** Repo + commit hash, `docker compose up`, the vulnerable-agent config (with the
benign canary tool). End card: next episode teaser (prompt-injection firewalls) + subscribe.
**Narration:**
> "Everything here is reproducible — the vulnerable agent, the canary tool, the exact attack configs
> for all three frameworks, down to the commit hash. It's all benign: the worst the agent can do is
> trip a canary on an isolated network, so you can safely run it yourself and tell me if your
> attack-success rates differ from mine. Next episode, I stop attacking and start defending — I put
> prompt-injection firewalls in front of an agent and try to get past them. If that sounds like your
> kind of trouble, subscribe, and I'll see you in the lab."

---

## Production notes
- **Voiceover:** narration blocks mirror `script.yaml`; ElevenLabs renders one MP3 per scene in
  your voice id.
- **Screen capture:** agent + framework CLIs/reports via Playwright or terminal cast; the lab is
  all local Docker so capture is easy.
- **Assembly:** same `video/` pipeline as prior episodes — pad each clip to its narration, burn
  captions, concat.
- **Ethics:** benign canary tool only; isolated no-egress network; responsible disclosure if a real
  bug surfaces in any framework; show attack techniques conceptually, never ship a weaponized
  exploit or a working jailbreak string.
