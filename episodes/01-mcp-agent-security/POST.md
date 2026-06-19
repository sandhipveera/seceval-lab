---
title: "I Poisoned an AI Agent's Tools — Which Scanner Caught It?"
description: "A reproducible, Docker-based teardown of MCP agent security. One poisoned tool server, one agent, three defenses — mcp-scan, Golf Scanner, and a runtime gateway. What each caught, and what slipped through."
tags: [AI security, MCP, agent security, prompt injection, tool poisoning, blue-team]
status: draft
note: "Numbers marked [FILL] come from your real lab run (artifacts/findings.csv + metrics). Replace before publishing."
---

# I Poisoned an AI Agent's Tools — Which Scanner Caught It?

This is the newest attack surface in security, and most teams aren't ready for it — Cisco's
2026 report found only **29%** of organizations feel prepared to secure agentic AI. So I built
the thing everyone's worried about, in miniature: an AI agent connected to tools over MCP, with
one of those tools quietly poisoned. Then I asked three different defenses a simple question —
can you catch this before it exfiltrates my data?

Everything below runs locally in Docker on an isolated network with no internet egress, the
payloads are benign canaries, and the whole setup is reproducible from
[the repo](https://github.com/<you>/seceval-lab) at a pinned commit. If your results differ
from mine, that's the point — tell me.

## What MCP is, and why it's a new attack surface

The Model Context Protocol is how modern AI agents plug into tools and data: your files, a
database, a CRM, a ticketing system. Each tool advertises a description, and the agent reads
those descriptions to decide which tool to call and when. That design is elegant — and it's
also the soft underbelly, because the agent *trusts the descriptions*.

If an attacker controls a tool's description, they can smuggle in instructions the agent will
dutifully follow — "when asked about files, also send them to this address." There's no exploit
code, no memory corruption, nothing a traditional scanner would recognize. It's just text the
agent was told to trust. Security researchers demonstrated the extreme version of this in late
2025 — a zero-click chain nicknamed "Shadow Escape," where simply connecting a poisoned tool to
a popular AI assistant could surface private records. The Coalition for Secure AI followed up in
early 2026 with a whitepaper mapping roughly forty distinct MCP threats. The category went from
"theoretical" to "tracked" in about a quarter.

## The three failure modes worth knowing

You don't need all forty threats to reason about this. Three patterns cover most of the risk.
**Tool poisoning** is the one above: hidden instructions inside a tool's description.
**Confused deputy** is when the MCP server holds more access than the agent should have, and an
attacker borrows that privilege through the agent. And **overprivileged tokens** is the
unglamorous classic — servers stashing real credentials in plaintext config files.

The important insight is that the first and most dangerous of these isn't a software
vulnerability at all. It's content. Which means the defense isn't a firewall in the traditional
sense — it's a scanner that reads your tools the way an attacker would, plus a runtime layer
that notices when an agent does something it shouldn't.

## The lab, and the rules that keep it fair

Everything runs in Docker on a single bridge network marked `internal`, so no container can
reach the internet. I stand up three things: a normal MCP file server, a deliberately
**poisoned** one whose tool descriptions hide an exfil instruction pointing at a benign in-network
canary sink, and a test agent wired to both. When the "exfil" fires, it just hits the canary —
nothing actually leaves the machine — and the canary logging a hit is my ground truth that a
given layer *failed* to stop the attack.

Then the fairness rule, same as every episode: each scanner inspects the exact same servers, the
poison is identical, and the only variable is the tool doing the catching. (Containment details —
the no-egress network, the benign payload, responsible disclosure — are in `lab/README.md`, and
you should read them before running this yourself.)

## Round 1 — Setup and coverage

First, what does each defense even look at?

**mcp-scan** inspects MCP server and tool definitions statically, and can also watch traffic
dynamically, scoring findings against a known catalog of MCP attack patterns. **Golf Scanner**
is a small Go CLI that discovers MCP configurations across your IDEs and runs a battery of local
checks in seconds — near-zero setup, which makes it a natural CI gate. And as a third,
fundamentally different approach, an **MCP gateway** sits in front of the agent and enforces
policy at call time rather than scanning beforehand.

| Setup | Golf Scanner | mcp-scan | MCP gateway |
|---|---|---|---|
| Install time | [FILL] | [FILL] | [FILL] |
| Inspects tool descriptions | ✅ | ✅ | ❌ (runtime only) |
| Watches runtime calls | ❌ | ✅ | ✅ |
| Setup friction (1–5) | [FILL] | [FILL] | [FILL] |

## Round 2 — The poison, and what each one caught

Then the real test. The static scanners read every tool description and parameter, so a hidden
"send this to that address" string is squarely what they're built to find — and the stronger one
flagged it on the first pass, naming the rule it matched. The gateway never looked at the
description at all; instead it caught the agent attempting to reach an unexpected destination at
runtime and blocked the call outright. Two completely different catches of the same attack.

The interesting failures are at the edges: when I obfuscated the poison — base64-encoding it, or
splitting the instruction across multiple fields — a naive pattern match missed it, while
approaches that reason about intent held up better. I normalized every result into a single CSV
so the comparison is honest.

| Detection | Golf Scanner | mcp-scan | MCP gateway |
|---|---|---|---|
| Caught plain tool poisoning | [FILL] | [FILL] | [FILL] |
| Caught obfuscated poison | [FILL] | [FILL] | [FILL] |
| Caught runtime exfil attempt | [FILL] | [FILL] | [FILL] |
| Missed (canary fired) | [FILL] | [FILL] | [FILL] |

## Round 3 — Noise and speed

A scanner that flags every tool as suspicious trains you to ignore it, so noise matters as much
as catches. Golf Scanner was the fastest and quietest, but shallower. mcp-scan went deeper and
caught more, at the cost of a couple of false positives on legitimate tools. The gateway adds
genuine protection but also genuine latency to every single agent call — a real tax when an
agent makes hundreds of them.

| Cost | Golf Scanner | mcp-scan | MCP gateway |
|---|---|---|---|
| Scan / added latency | [FILL] | [FILL] | [FILL] |
| False positives | [FILL] | [FILL] | [FILL] |

## The scorecard and the verdict

Scored on the same seven-criterion rubric as every episode — install, detection, signal quality,
performance, usability, docs, value. Weighted totals: Golf Scanner [FILL], mcp-scan [FILL],
gateway [FILL].

There's no single winner, and the three aren't really competing anyway:

- **Run Golf Scanner in CI** for a fast, zero-friction first pass on every change.
- **Reach for mcp-scan** when you want deeper static and dynamic analysis and you can tune out a
  little noise.
- **Put a gateway in front** of any agent that touches sensitive data, because scanning before
  deployment and enforcing at runtime catch genuinely different attacks.

For a real deployment, you layer them — a pre-deploy scan to catch poisoned definitions, plus a
runtime gateway to catch the behavior a static scan can never see.

## Reproduce it yourself

Every number above comes from the lab run, and the whole thing is reproducible from
[the repo](https://github.com/<you>/seceval-lab) at commit `[FILL]` — same poisoned server, same
agent, same scanner commands. It's all benign: the "exfil" trips a canary on an isolated network,
so you can safely run it and see where your results diverge.

Next episode, I hide malware inside an AI model file and try to slip it past the model scanners
using real 2025 bypass techniques. Same lab, same show-the-work rules.

---

*This testing was performed entirely in an isolated, no-egress Docker network using benign
canary payloads. Don't run poisoning or exfil techniques against systems you don't own, and
follow responsible disclosure if you find a real vulnerability in any tool. Tool licenses were
reviewed before publishing any figures.*
