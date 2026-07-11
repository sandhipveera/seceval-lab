# YouTube Metadata — Episode 03: LLM Red-Team Showdown (Garak vs PyRIT vs Promptfoo)

## Title (A recommended)

- **A.** I Attacked My Own AI Agent — Which Red-Team Tool Broke It First? *(Recommended)*
- B. Garak vs PyRIT vs Promptfoo: I Red-Teamed an AI Agent With All 3
- C. OpenAI Bought a Red-Team Tool. I Tested It Against NVIDIA's and Microsoft's.
- D. Breaking AI Agents: 3 Red-Team Frameworks vs 1 Vulnerable Agent (Tested in Docker)

## Description

```
LLM red-teaming went agentic in 2026. In March, OpenAI acquired Promptfoo. In May, NVIDIA's Garak
shipped an "Agent-breaker" probe. And Microsoft's PyRIT became the engine behind Azure's AI Red
Teaming Agent. The whole field moved from "jailbreak the chatbot" to "attack the agent."

So I built a deliberately vulnerable AI agent — thin safety rules, one tool it can be tricked into
misusing — and pointed all three frameworks at it. Same agent, same weaknesses, same isolated lab.
Here's which one broke it first, and which one told me the most about why.

Everything runs locally in Docker on an isolated network with no internet egress, using a benign
canary tool. Fully reproducible — clone the repo and check my attack-success rates.

🔗 Repo + reproduce it: https://github.com/sandhipveera/seceval-lab
🧪 Lab: vulnerable LLM agent + canary tool + canary sink, all in isolated Docker
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ All testing is in an isolated lab with a benign canary tool. Never run jailbreak, injection, or
exfiltration techniques against systems or models you don't own.

⏱️ Chapters
0:00  I built an AI agent, then tried to break it
0:30  Why LLM red-teaming went agentic in 2026
1:45  Jailbreak, prompt injection & tool misuse
2:45  The lab & the fairness rules (local Docker, no egress)
3:45  Round 1 — Setup & coverage
5:15  Round 2 — The attack & what each framework broke
7:45  Round 3 — Noise & cost (time, tokens, false alarms)
9:00  Scorecard & the verdict
10:45 Reproduce it yourself + what's next

#AIsecurity #LLMredteaming #aiagents #promptinjection #jailbreak #cybersecurity #infosec #LLMsecurity #redteam #devsecops

Tools: Garak (NVIDIA), PyRIT (Microsoft), Promptfoo (OpenAI), Docker. Concepts: jailbreak, prompt
injection, tool misuse, agentic red-teaming, attack-success rate.
```

## Tags
AI security, LLM red teaming, red team, Garak, PyRIT, Promptfoo, NVIDIA Garak, Microsoft PyRIT,
OpenAI Promptfoo, AI agent security, prompt injection, jailbreak, tool misuse, agentic AI, LLM
security, attack success rate, devsecops, cybersecurity

## Thumbnail
A friendly AI agent icon center; three attack bolts labeled GARAK / PYRIT / PROMPTFOO striking it
from three sides; big text "WHICH ONE BREAKS IT?" with a small "TESTED IN DOCKER" tag. Use the
`title_cold_open.html` palette (dark + #5ad1a8, red accent for the attack). Add three small vendor
marks (NVIDIA / Microsoft / OpenAI) as nominative logos along the bottom.

## Pinned comment
"Full lab (vulnerable AI agent + canary tool + all three frameworks' attack configs) is on GitHub —
runs in Docker, isolated, no egress, benign canary only: https://github.com/sandhipveera/seceval-lab. Run
it and tell me if your attack-success rates beat mine. Next up: I switch to defense and try to beat
prompt-injection firewalls (LLM Guard vs Vigil vs Rebuff vs Prompt Guard 2)."
