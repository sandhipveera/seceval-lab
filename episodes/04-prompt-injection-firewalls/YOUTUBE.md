# YouTube Metadata — Episode 04: Prompt-Injection Firewalls

## Title (A recommended)

- **A. (Recommended)** I Smuggled a Prompt Injection Past 4 AI Firewalls — Which One Caught It?
- B. 4 Prompt-Injection Firewalls vs 1 Sneaky Attack (LLM Guard, Vigil, Rebuff, Prompt Guard 2)
- C. Your AI Firewall Is a Classifier — And I Can Fool It. I Tested 4.
- D. Can Any AI Firewall Stop Prompt Injection? I Tested 4 (Docker Lab)

## Description

```
Prompt injection is still OWASP's #1 LLM risk in 2026, and the fix everyone bolts on is a
firewall in front of the model. But almost all of these firewalls are ML classifiers under the
hood — and this year's research showed how brittle that can be (one study hit up to 100% evasion
with simple character tricks). So I built a vulnerable AI app, wrote one injection that tries to
exfiltrate data, and ran four firewalls against it: LLM Guard, Vigil, Rebuff, and Meta's brand-new
Prompt Guard 2. Same app, same attack — only the guard changes. Here's exactly what each one
caught, and what walked right past.

I escalate the attack in three levels: a plain direct injection, then obfuscation (spaced trigger
words, look-alike characters, base64), then indirect injection hidden inside a document the app
reads. Then I measure the boring-but-critical stuff: false positives on benign prompts, and the
latency each guard adds to every call.

Everything runs locally in Docker on an isolated network with no internet egress, using benign
canary payloads. Fully reproducible — clone the repo and check my numbers.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Lab: vulnerable LLM app + injection battery + canary sink, all in isolated Docker
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ All testing is in an isolated lab with benign payloads. Never run injection or exfil techniques
against systems you don't own.

⏱️ Chapters
0:00  Four firewalls, one injection — who blinks?
0:30  Why prompt-injection firewalls are 2026's most bolted-on defense
1:30  Direct vs indirect injection (and why obfuscation beats classifiers)
2:30  The lab & the fairness rules (local Docker, no egress)
3:30  Round 1 — Setup & coverage (what each firewall actually is)
5:00  Round 2 — The injection battery: plain, obfuscated, indirect
7:30  Round 3 — Noise & cost (false positives + added latency)
8:45  Scorecard & the verdict
10:30 Reproduce it yourself + what's next

#AIsecurity #promptinjection #LLMsecurity #aiagents #cybersecurity #infosec #guardrails #redteam #appsec #devsecops

Tools: LLM Guard, Vigil, Rebuff, Meta Prompt Guard 2, Docker. Concepts: prompt injection (direct
& indirect), classifier evasion, obfuscation, over-defense / false positives, OWASP LLM01.
```

## Tags
AI security, prompt injection, indirect prompt injection, LLM security, prompt injection firewall,
guardrails, LLM Guard, Vigil, Rebuff, Prompt Guard 2, Meta Prompt Guard, classifier evasion,
jailbreak detection, OWASP LLM01, agentic AI, red team, blue team, infosec, devsecops, cybersecurity

## Thumbnail
Four firewall "shields" in a row (one labeled with each tool), three glowing green and one cracked
red as a payload slips through it; big text "1 INJECTION vs 4 FIREWALLS" + a small "WHO CAUGHT IT?"
Use the `title_cold_open.html` palette (dark + #5ad1a8, red accent for the attack that gets through).

## Pinned comment
"Full lab (vulnerable LLM app + injection battery + canary sink) is on GitHub — runs in Docker,
isolated, no egress, benign payloads: https://github.com/<you>/seceval-lab. Run it and tell me if
your firewalls catch more than mine — with these classifiers, they might. Next up: AI gateways &
LLM proxies — do the things guarding your whole model fleet actually hold?"
