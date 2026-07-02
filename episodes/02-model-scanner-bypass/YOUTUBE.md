# YouTube Metadata — Episode 02: Model-Scanner Bypass

## Title (A recommended)

- **A.** I Hid Malware in an AI Model — Which Scanner Caught It?
- B. This AI Model Passed the Scanner. It Still Ran My Code.
- C. Beating the AI Model Scanner: picklescan vs 3 Rivals (2025 Bypasses)
- D. AI Models Can Run Malware on Load. I Tested 4 Scanners.

## Description

```
Most AI models ship as pickle files — and pickle isn't data, it's code that runs the moment you
load the model. In December 2025, researchers dropped three critical zero-days in picklescan, the
exact scanner Hugging Face runs on every upload. So I built a malicious model file with a benign
canary payload and ran four scanners against it: picklescan, ModelScan (Protect AI), ModelAudit
(Promptfoo), and fickling (Trail of Bits). Here's exactly what each one caught — plain payload,
blocklist evasion, renamed extension, broken archive — and what walked right past.

Everything runs locally in Docker on an isolated network with no internet egress, using a benign
canary payload. Fully reproducible — clone the repo and check my numbers.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Lab: one benign-canary malicious model + 4 scanners + canary sink, all in isolated Docker
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ All testing is in an isolated lab with a benign canary payload — never a weaponized exploit.
Never build or run malicious model files against systems you don't own.

⏱️ Chapters
0:00  This model passed the scanner — and ran my code
0:30  Why the model FILE is the attack surface (pickle = code)
1:30  Blocklist evasion, renamed/broken archives, deep imports
2:30  The lab & the fairness rules (local Docker, no egress)
3:30  Round 1 — Setup & coverage
5:00  Round 2 — The payload & what each scanner caught
7:30  Round 3 — Noise & cost (false positives, scan time)
8:45  Scorecard & the verdict
10:30 Reproduce it yourself + what's next

#AIsecurity #pickle #picklescan #modelscan #cybersecurity #infosec #LLMsecurity #supplychain #mlsecops #devsecops

Tools: picklescan, ModelScan (Protect AI), ModelAudit (Promptfoo), fickling (Trail of Bits),
Docker. Concepts: pickle deserialization, blocklist evasion, nullifAI, CVE-2025-10155/10156/10157,
model supply-chain security.
```

## Tags
AI security, pickle security, picklescan, ModelScan, ModelAudit, fickling, Protect AI, Promptfoo,
Trail of Bits, malicious model, model supply chain, pickle deserialization, nullifAI, Hugging Face
security, MLSecOps, LLM security, red team, infosec, devsecops, cybersecurity

## Thumbnail
A `pytorch_model.bin` file icon center with a green "SCAN PASSED" checkmark, cracked open to reveal
a red skull / shell prompt leaking out. Big text "MALWARE INSIDE" + a small "CAUGHT?" Use the
`title_cold_open.html` palette (dark + #5ad1a8, red accent for the payload).

## Pinned comment
"Full lab (one benign-canary malicious model + picklescan / ModelScan / ModelAudit / fickling) is
on GitHub — runs in Docker, isolated, no egress, benign payload only:
https://github.com/<you>/seceval-lab. Update your scanners (the Dec 2025 picklescan CVEs are fixed
in 0.0.31) and tell me if yours catch more than mine. Next up: the LLM red-team showdown —
Garak vs PyRIT vs Promptfoo."
