# Episode Backlog — AI Security Series

Ordered by traction potential (newest / least-covered first; "tried-and-tested" tools are
fallbacks only). The weekly task pulls the next unchecked entry, delivers its package into
`episodes/<NN>-<slug>/`, and checks it off. All episodes run **locally in Docker**.

## Active slate (AI security)

- [x] 01 — MCP / agent security teardown: poisoned MCP server vs mcp-scan / Golf Scanner *(delivered)*
- [x] 02 — "I beat the AI model scanner": picklescan 2025 bypasses vs ModelScan / ModelAudit / fickling *(delivered)*
- [x] 03 — LLM red-team showdown: Garak vs PyRIT vs Promptfoo *(delivered)*
- [x] 04 — Prompt-injection firewalls: LLM Guard vs Vigil vs Rebuff vs Prompt Guard 2 *(delivered)*
- [x] 05 — LLM guardrail bypass: NeMo Guardrails vs Guardrails AI (emoji-smuggling / tokenizer-gap evasion) *(delivered — promoted from fallback F2)*

## Fallbacks (only if a fresher matchup slips — saturated / lower lab-fit)

- [ ] F1 — AI SOC explainer / react: what an autonomous SOC analyst actually does *(skipped again for ep06, same reasons as ep05: explainer/react format doesn't fit the head-to-head Docker + 7-criterion scorecard, and the "agentic SOC 2026" space is saturated with vendor guides. Traction rule applied — promoted runway A-06 instead, which fits the format and had a live 2026 hook. Recommend retiring or reformatting F1 into a head-to-head.)*
- [x] F2 — NeMo Guardrails vs Guardrails AI deep-dive (needs a novel test angle, e.g. a live bypass) *(delivered as ep05 — fresh hook: 2025–26 emoji-smuggling / variation-selector evasion, ~100% ASR from guard/model tokenizer misalignment)*

## Notes for each build
- Same fixed 7-criterion scorecard rubric (install 15%, detection/efficacy 30%, signal quality
  15%, performance 10%, usability 10%, docs 10%, value 10%).
- Fair-test rule: same target, same attack scenario, same clean container state; only the tool
  under test changes.
- Targets shift from "vulnerable web app" to vulnerable **LLM app / agent / MCP server / model
  file**, all as Docker containers on an isolated network with no egress.
- All quantitative results stay as `[FILL]` until a real lab run produces them.
- "Bypass" episodes: benign payloads only, responsible disclosure, no weaponized exploit shipped.

## Runway — refill slate (research fresh before building; ordered by 2026 traction)

The franchise is the **reproducible Docker head-to-head + 7-criterion scorecard**, NOT any one product.
Three interchangeable fuel sources feed it, so the series doesn't run dry when tool matchups thin out:
(A) product matchups, (B) technique/bypass episodes — no new product needed, (C) the incident
case-study stream. Plus an evergreen repurposing lane once the catalog ages.

### A. Product matchups (next up)
- [x] 06 — AI gateway / LLM-proxy security: LiteLLM guardrails vs Portkey vs Bifrost *(delivered — promoted into the active slate over fallback F1. Fresh hook: the gateway became the attack surface in 2026 — LiteLLM PyPI supply-chain compromise (Mar, ~40 min window) + CVE-2026-42208 pre-auth SQLi, CVSS 9.3, CISA KEV in May; Portkey fully open-sourced (Mar) then Palo Alto acquisition intent (Apr). Cloudflare AI Gateway **cut**: hosted SaaS, can't run no-egress without breaking the fair-test rule. Adds a second axis — read-only posture checks on the gateway itself, no exploits shipped)*
- [ ] 07 — Commercial AI firewalls: Lakera Guard vs Prompt Security vs Protect AI Guardian vs Robust Intelligence *(use self-host / trial tiers; some are SaaS-gated — flag like Promptfoo)*
- [ ] 08 — PII / secrets redaction before the model: Microsoft Presidio vs LLM Guard Anonymize vs Nightfall vs Private-AI
- [ ] 09 — Model provenance / signing / AI-SBOM: Sigstore model signing vs CycloneDX-ML vs safetensors + model cards
- [ ] 10 — Jailbreak/injection **classifier bake-off**: Prompt Guard 2 vs Lakera vs deepset-injection vs ProtectAI deberta *(pure detector head-to-head)*
- [ ] 11 — Agent sandboxing / tool isolation: gVisor vs Firecracker vs seccomp vs E2B-style sandboxes for agent tool calls
- [ ] 12 — RAG / vector-DB poisoning: detection + defense
- [ ] 13 — LLM output validation / structured-output guards: Guardrails AI vs Instructor vs Outlines
- [ ] 14 — LLM DLP / data-egress controls at the gateway
- [ ] 15 — AI-generated-code security: Semgrep AI vs Snyk vs CodeQL scanning LLM-authored code
- [ ] 16 — Deepfake / voice-clone / synthetic-media detection tools

### B. Technique / bypass episodes (a fresh attack vs the defenses — no new product required)
- [ ] T1 — Indirect / second-order prompt injection via a poisoned retrieved doc (webpage/PDF) vs the injection firewalls
- [ ] T2 — Tokenizer-gap evasion beyond emoji: variation selectors / zero-width / homoglyphs (follow-on to ep05)
- [ ] T3 — Multi-turn "crescendo" jailbreaks vs single-turn guards
- [ ] T4 — MCP tool-description / rug-pull tool attacks 2.0 vs runtime gateways
- [ ] T5 — Data exfil via markdown-image/link rendering in chat UIs

### C. Incident case-study stream (weekly AccessQuint LinkedIn — effectively inexhaustible)
New named breach / agentic incident as it lands (JadePuffer and Klue were both such). Each maps to the
authority-in-the-artifact thesis. Fresh incidents refill this weekly with zero product dependency.

### D. Evergreen / repurposing (once the catalog ages ~6–8 weeks)
- "Same tool, one year later" — re-run the scorecard as tools update (they move fast); an evergreen refresh.
- Recycle aged posts into new formats — carousel, poll, "5 lessons," myth-buster — and repost to a
  *different* group. Old enough that audience overlap is low, so it reads as new reach.
- Every episode already fans out to ~5 assets (native post, carousel, poll, 2–3 group cross-posts),
  so output stretches well past input.
