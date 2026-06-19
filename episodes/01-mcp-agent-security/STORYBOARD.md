# Episode 01 — Storyboard
## "I Poisoned an AI Agent's Tools — Which Scanner Caught It?"
### MCP agent security: mcp-scan vs Golf Scanner (+ a gateway)

Single source of truth for the blog and the video. Narration blocks are the exact words for
ElevenLabs (mirrored in `script.yaml`); on-screen actions map to the Docker lab + dashboards.

- **Target length:** 10–12 min video / ~1,900-word blog
- **Hook:** the newest attack surface in security right now — AI agents wired to tools over MCP
- **News pegs:** "Shadow Escape" zero-click MCP attack (Oct 2025); CoSAI MCP threat whitepaper
  (Jan 2026); Cisco stat — only **29%** of orgs feel ready to secure agentic AI.
- **Through-line:** one poisoned MCP server, same agent, same exfil attempt — only the scanner
  changes.
- **Lab:** 100% local Docker. No VMs. Isolated bridge network, **no internet egress**.

---

## Blog outline (maps 1:1 to video scenes)

1. What MCP is, why agents + tools created a brand-new attack surface
2. The threat in plain terms: tool poisoning, confused deputy, the "Shadow Escape" exfil chain
3. The lab: a deliberately poisoned MCP server + a test agent, all in isolated Docker
4. Round 1 — Setup & coverage (what each scanner even looks at)
5. Round 2 — Detection (does it flag the poisoned tool description / exfil path?)
6. Round 3 — Signal quality & speed (noise, false positives, scan time)
7. Scorecard + verdict (who should run what, and where a gateway fits)
8. Reproduce it yourself (repo + commit; benign payloads only)

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:30)
**On screen:** A chat agent happily "using a tool," then a red overlay showing data silently
leaving. Title card: *"Your AI agent has tools. What if one of them is lying?"*
**Narration:**
> "This is the newest attack surface in security, and most teams aren't ready for it. Modern AI
> agents don't just talk — they use tools, wired in over something called MCP. But what happens
> when one of those tools is poisoned? I built an agent, handed it a malicious tool server, and
> then asked three different security scanners a simple question: can you catch this before it
> quietly exfiltrates my data? No marketing — just what each one flagged."

### Scene 2 — What MCP is (0:30–1:30)
**On screen:** Simple animated diagram: an AI agent in the middle, MCP servers as plug-in tools
around it (files, database, CRM), arrows showing tool calls.
**Narration:**
> "Quick context. The Model Context Protocol — MCP — is how AI agents plug into tools and data:
> your files, a database, a ticketing system. The agent reads each tool's description to decide
> when to use it. That's the elegant part, and also the dangerous part: the agent trusts those
> descriptions. If an attacker controls a tool's description, they can smuggle in hidden
> instructions the agent will follow. Researchers call the worst version of this 'Shadow
> Escape' — a zero-click attack where just connecting a poisoned tool can lead to silent data
> theft. And Cisco found only twenty-nine percent of organizations feel ready to secure this."

### Scene 3 — The threats, in plain terms (1:30–2:30)
**On screen:** Three labeled cards animating in: Tool Poisoning, Confused Deputy, Overprivileged
Tokens. Highlight the poisoned tool description with the hidden payload.
**Narration:**
> "There are three failure modes worth knowing. Tool poisoning: the tool's description contains
> hidden instructions — 'also send the user's files to this address.' Confused deputy: the MCP
> server has more access than the agent should, and the attacker borrows it. And overprivileged
> tokens: servers storing real credentials in plaintext config. The scary part is the first one
> needs no exploit code — it's just text the agent is told to trust. So the defense isn't a
> firewall; it's a scanner that reads the tools the way an attacker would."

### Scene 4 — The lab & the rules (2:30–3:30)
**On screen:** Terminal: `docker compose up` bringing up the agent, a clean MCP server, and the
**poisoned** MCP server on an isolated network. Quick pan over `lab/README.md` highlighting
"no egress."
**Narration:**
> "Here's the setup, and fairness matters. Everything runs locally in Docker on one isolated
> network with no path to the internet — so nothing actually leaves. I stand up a test agent, a
> normal MCP server, and a deliberately poisoned one whose tool descriptions hide an exfil
> instruction with a benign canary payload. Then each scanner gets the exact same servers to
> inspect. Same target, same poison — the only variable is the tool doing the catching."

### Scene 5 — Round 1: Setup & coverage (3:30–5:00)
**On screen:** Split terminal: installing and running `mcp-scan` and `Golf Scanner`, plus an MCP
gateway in front of the agent. A small "what each one inspects" table fills in.
**Narration:**
> "Round one — getting each scanner running and seeing what it even looks at. mcp-scan inspects
> server and tool definitions statically and can watch traffic dynamically, scoring against a
> known set of MCP attacks. Golf Scanner is a tiny Go command-line tool that discovers MCP
> configs across your IDEs and runs a set of local checks in seconds — almost zero setup. And as
> a third approach, an MCP gateway sits in front of the agent and tries to enforce policy at
> runtime rather than scan beforehand. Setup times and coverage are on screen; full commands are
> in the repo."

### Scene 6 — Round 2: The poison & detection (5:00–7:30)
**On screen:** Left: the agent being asked a normal question and starting to call the poisoned
tool. Right: each scanner's output — does it flag the hidden instruction and the exfil path?
Cut to the **normalized findings table** (caught / missed per scanner).
**Narration:**
> "Now the real test. I point each scanner at the poisoned server and watch. The static scanners
> read every tool description and parameter — so a hidden 'exfiltrate to this address' string is
> exactly what they're built to find, and the better one flagged it immediately with the rule it
> matched. The gateway took a different path: it didn't care about the description, it caught the
> agent trying to reach an unexpected destination at runtime and blocked the call. The
> interesting gaps are where a poison is obfuscated — encoded or split across fields — and a
> simple pattern match misses it. I normalized every result into one table so it's apples to
> apples. Here's who caught what."

### Scene 7 — Round 3: Noise & speed (7:30–8:45)
**On screen:** False-positive column highlighted; then a scan-time / resource bar chart per
tool.
**Narration:**
> "Detection isn't the whole story. A scanner that flags every tool as suspicious trains you to
> ignore it. Golf Scanner was the fastest and quietest but shallower; mcp-scan went deeper and
> caught more, at the cost of a couple of false positives on legitimate tools; the gateway adds
> real protection but also real latency to every agent call. Here's the cost of each, measured
> under the same load."

### Scene 8 — Scorecard & verdict (8:45–10:30)
**On screen:** The seven-criterion scorecard filling in; weighted totals animate; three
"Use X if…" cards.
**Narration:**
> "Same rubric every episode — install, detection, signal quality, performance, usability, docs,
> and value. And like everything in this space, there's no single winner. Use Golf Scanner for a
> fast, zero-friction first pass — run it in CI on every change. Use mcp-scan when you want
> deeper static and dynamic analysis and you're willing to tune out a little noise. And put a
> gateway in front when an agent touches anything sensitive, because scanning before deployment
> and enforcing at runtime catch genuinely different attacks. Honestly, the right answer for a
> real deployment is to layer them."

### Scene 9 — Reproduce it / outro (10:30–11:30)
**On screen:** Repo + commit hash, `docker compose up`, the poisoned-tool definition (with the
benign canary). End card: next episode teaser (beating the AI model scanner) + subscribe.
**Narration:**
> "Everything here is reproducible — the poisoned MCP server, the agent, the scanner commands,
> down to the commit hash. It's all benign: the 'exfil' just trips a canary on an isolated
> network, so you can safely run it yourself and tell me if your results differ. Next episode I
> hide malware inside an AI model and try to slip it past the model scanners — using real 2025
> bypasses. If that sounds like your kind of trouble, subscribe, and I'll see you in the lab."

---

## Production notes
- **Voiceover:** narration blocks mirror `script.yaml`; ElevenLabs renders one MP3 per scene in
  your voice id.
- **Screen capture:** agent + scanner dashboards/CLIs via Playwright or terminal cast; the lab
  is all local Docker so capture is easy.
- **Assembly:** same `video/` pipeline as the IDS episode — pad each clip to its narration,
  burn captions, concat.
- **Ethics:** benign canary payload only; isolated no-egress network; responsible disclosure if
  a real bug surfaces; show technique conceptually, never ship a weaponized exploit.
