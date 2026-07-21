# YouTube Metadata — Episode 05: LLM Guardrail Bypass

## Title (A recommended)

- **A.** I Hid a Jailbreak Inside an Emoji — Which AI Guardrail Caught It? *(Recommended)*
- B. This Emoji Bypasses AI Guardrails. I Tested NeMo Guardrails vs Guardrails AI.
- C. AI Guardrails Have a Blind Spot — I Smuggled a Jailbreak Right Through It
- D. NeMo Guardrails vs Guardrails AI: I Broke Both With Invisible Characters

## Description

```
AI guardrails are supposed to block jailbreaks and prompt injection before they ever reach the
model. But the guard is a small classifier with its own tokenizer — and it doesn't always read
text the way the model does. Live in that gap and you can hide an attack in plain sight. I put a
benign canary secret behind a guarded chatbot and ran the same jailbreak three ways — plain, then
disguised with zero-width characters and homoglyphs, then smuggled inside an emoji — against two
of the biggest open-source guardrails: NVIDIA NeMo Guardrails and Guardrails AI. Here's exactly
what each one caught, and where the disguise won.

Everything runs locally in Docker on an isolated network with no internet egress, using a benign
canary secret. Fully reproducible — clone the repo and check my numbers.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Lab: vulnerable chatbot + canary secret + attack runner, all in isolated Docker
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ All testing is in an isolated lab with a benign canary and conceptual evasion techniques.
Never run jailbreak or injection techniques against systems you don't own.

⏱️ Chapters
0:00  Same attack, one emoji, guardrail blind
0:30  What guardrails are (and the tokenizer gap under them)
1:30  Emoji smuggling, zero-width & homoglyphs
2:30  The lab & the fairness rules (local Docker, no egress)
3:30  Round 1 — Setup & coverage
5:00  Round 2 — The disguise & what each guardrail caught
7:30  Round 3 — Noise & speed
8:45  Scorecard & the verdict (the fix neither vendor prints)
10:30 Reproduce it yourself + what's next

#AIsecurity #LLMsecurity #promptinjection #jailbreak #aiguardrails #cybersecurity #infosec #NeMoGuardrails #GuardrailsAI #redteam

Tools: NVIDIA NeMo Guardrails, Guardrails AI, Docker. Concepts: emoji smuggling, Unicode
variation selectors, zero-width injection, homoglyphs, tokenizer misalignment, prompt injection
(OWASP LLM01).
```

## Tags
AI security, LLM security, LLM guardrails, NeMo Guardrails, Guardrails AI, prompt injection,
jailbreak, emoji smuggling, Unicode variation selectors, zero-width characters, homoglyph attack,
tokenizer misalignment, agentic AI, red team, blue team, infosec, devsecops, OWASP LLM Top 10

## Thumbnail
Split frame: left side a chat bubble stamped "BLOCKED" in red; right side the same bubble wearing
a big 😀 emoji, stamped "PASSED" in green, with a leaking canary tag behind it. Big text
"HIDDEN IN AN EMOJI" + a small "CAUGHT?" Use the `title_cold_open.html` palette (dark + #5ad1a8,
red accent for the blocked case).

## Pinned comment
"Full lab (vulnerable chatbot + canary secret + attack runner + both guardrail configs) is on
GitHub — runs in Docker, isolated, no egress, benign canary only:
https://github.com/<you>/seceval-lab. Run it and tell me if your guardrails hold up better than
mine. Next up: the AI supply chain — can you actually prove the model you're running is the one you
think it is? Model signing & provenance, tested."
