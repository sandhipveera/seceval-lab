# YouTube Metadata — Episode 01: MCP Agent Security

## Title (A recommended)

- **A.** I Poisoned an AI Agent's Tools — Which Scanner Caught It?
- B. Your AI Agent's Tools Can Be Poisoned. I Tested 3 Defenses.
- C. Hacking AI Agents: MCP Tool Poisoning vs 3 Security Scanners
- D. The New AI Attack Nobody's Ready For (MCP Tool Poisoning, Tested)

## Description

```
AI agents don't just chat anymore — they use tools, wired in over MCP. But the agent trusts each
tool's description, and that's the problem. I built an agent, poisoned one of its tools to
exfiltrate data, and ran three different defenses against it: mcp-scan, Golf Scanner, and a
runtime MCP gateway. Here's exactly what each one caught — and what slipped through.

Everything runs locally in Docker on an isolated network with no internet egress, using benign
canary payloads. Fully reproducible — clone the repo and check my numbers.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Lab: poisoned MCP server + test agent + canary sink, all in isolated Docker
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ All testing is in an isolated lab with benign payloads. Never run poisoning or exfil
techniques against systems you don't own.

⏱️ Chapters
0:00  Your AI agent's tools might be lying
0:30  What MCP is (and the new attack surface)
1:30  Tool poisoning, confused deputy & overprivileged tokens
2:30  The lab & the fairness rules (local Docker, no egress)
3:30  Round 1 — Setup & coverage
5:00  Round 2 — The poison & what each scanner caught
7:30  Round 3 — Noise & speed
8:45  Scorecard & the verdict
10:30 Reproduce it yourself + what's next

#AIsecurity #MCP #aiagents #promptinjection #cybersecurity #infosec #LLMsecurity #redteam #appsec #devsecops

Tools: mcp-scan, Golf Scanner, MCP gateway, Docker. Concepts: tool poisoning, Shadow Escape,
confused deputy, MCP security (CoSAI threat model).
```

## Tags
AI security, MCP, model context protocol, AI agent security, tool poisoning, prompt injection,
LLM security, Shadow Escape, mcp-scan, Golf Scanner, MCP gateway, agentic AI, red team, blue
team, infosec, devsecops, OWASP LLM, cybersecurity

## Thumbnail
AI agent icon center; a glowing red "tool" plugged in dripping a hidden payload; big text
"POISONED TOOL" + a small "CAUGHT?" Use the `title_cold_open.html` palette (dark + #5ad1a8, red
accent for the attack).

## Pinned comment
"Full lab (poisoned MCP server + agent + scanners) is on GitHub — runs in Docker, isolated, no
egress, benign payloads: https://github.com/<you>/seceval-lab. Run it and tell me if your
scanners catch more than mine. Next up: beating the AI model scanner with real 2025 bypasses."
