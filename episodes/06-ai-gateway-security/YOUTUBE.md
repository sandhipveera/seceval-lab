# YouTube Metadata — Episode 06: AI Gateway Security

## Title (A recommended)

- **A. ✅ Recommended** — I Attacked the Gateway Guarding My LLM — Which One Held?
- B. Your AI Gateway Is the Attack Surface (LiteLLM vs Portkey vs Bifrost)
- C. 3 AI Gateways vs 6 Attacks — And Who Guards the Gateway?
- D. The Box Guarding Your LLM Holds Every Key You Own. I Tested 3.

*Why A: matches the series' first-person + question formula that worked on ep01/ep02, carries the
2026 news hook implicitly, and puts the head-to-head in the second half where the thumbnail text
can finish the thought.*

## Description

```
Every request your app sends to a model goes through one box — an AI gateway. It holds your keys,
your rate limits, and increasingly your guardrails. In 2026 that box became the target: LiteLLM
shipped two backdoored versions to PyPI in March, then a pre-auth SQL injection (CVSS 9.3) hit
CISA's Known Exploited list in May. Meanwhile Portkey open-sourced its whole gateway and Palo Alto
Networks moved to acquire it.

So I ran two tests at once. Six attacks THROUGH three self-hostable gateways — LiteLLM, Portkey
and Bifrost — and then a posture pass AT the gateways themselves. Here's exactly what each one
caught, what it charged me in latency, and what slipped through.

Everything runs locally in Docker on an isolated network with no internet egress, against a stub
model provider, using benign canary payloads. Fully reproducible — clone the repo and check my
numbers.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Lab: vulnerable LLM app + gullible stub model + canary sink + one gateway at a time
⚖️ Scored on the same 7-criterion rubric every episode
🚫 Cloudflare AI Gateway was cut — it's hosted, so it can't run on a no-egress network without
   breaking the fair-test rule.

⚠️ All testing is in an isolated lab with benign payloads and a stub model. The gateway-as-target
section is read-only posture checking (version, reachability, digest pinning) — no exploit for any
disclosed CVE was written or run. Never run these techniques against systems you don't own.

⏱️ Chapters
0:00  The box guarding your LLM holds every key you own
0:30  What an AI gateway is — and why 2026 made it a target
1:30  Two threats: through the gateway vs at the gateway
2:40  The lab & the fairness rules (local Docker, no egress)
3:40  Round 1 — Setup & coverage (and why Cloudflare got cut)
5:10  Round 2 — Six attacks & what each gateway caught
7:50  Round 3 — Noise & the tax on every request
9:05  Scorecard & the verdict
10:45 Reproduce it yourself + what's next

#AIsecurity #LLMsecurity #promptinjection #aigateway #litellm #cybersecurity #infosec #devsecops #supplychainsecurity #appsec

Tools: LiteLLM, Portkey Gateway, Bifrost (Maxim AI), Docker. Concepts: AI gateway / LLM proxy
security, prompt injection, indirect injection, PII redaction, guardrails, supply-chain
compromise, CVE-2026-42208, digest pinning.
```

## Tags

AI security, AI gateway, LLM gateway, LLM proxy, LiteLLM, Portkey, Bifrost, prompt injection,
indirect prompt injection, guardrails, PII redaction, LLM security, supply chain attack, CVE-2026-42208,
CISA KEV, agentic AI, devsecops, infosec

## Thumbnail

Dark background, the ep01 palette (base dark + `#5ad1a8`, red accent for the attack). Center: a
single glowing gateway box with three provider arrows fanning out the back and a keyring visibly
hanging off it. A red arrow bypasses the app entirely and stabs the box itself. Big text
**"WHO GUARDS THE GATEWAY?"** with a small **"3 TESTED"** tag in the corner. Face in the lower-left
third if using one, looking at the red arrow rather than the camera.

## Pinned comment

"Full lab (vulnerable LLM app + gullible stub model + canary sink + LiteLLM/Portkey/Bifrost
configs) is on GitHub — runs in Docker, isolated, no egress, benign payloads, zero real API keys:
https://github.com/<you>/seceval-lab. To be clear about method: the gateway-as-target section is
posture only — version, reachability and digest pinning — no CVE exploit is shipped or run. Run it
and tell me if your gateway catches the obfuscated injection, because that's the case I expect to
be most contested. Next up: the commercial AI firewalls — Lakera Guard vs Prompt Security vs
Protect AI Guardian — does paying change the answer?"
