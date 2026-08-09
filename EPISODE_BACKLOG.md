# Episode Backlog — AI Security Series

Ordered by traction potential (newest / least-covered first). The weekly task pulls the next
entry, delivers its package into `episodes/<NN>-<slug>/`, and checks it off. All episodes run
**locally in Docker**.

> Note: specific tool matchups and hooks for **unreleased** episodes are kept out of this public
> file and revealed at launch. Delivered episodes list their matchup once the episode is live.

## Delivered

- [x] 01 — MCP / agent security teardown: poisoned MCP server vs mcp-scan / Golf Scanner
- [x] 02 — "I beat the AI model scanner": picklescan 2025 bypasses vs ModelScan / ModelAudit / fickling
- [x] 03 — LLM red-team showdown: Garak vs PyRIT vs Promptfoo
- [x] 04 — Prompt-injection firewalls: LLM Guard vs Vigil vs Rebuff vs Prompt Guard 2

## In production

- [x] 05 — LLM guardrails head-to-head *(delivered)* — NeMo Guardrails vs Guardrails AI vs Llama Guard 4; fresh hook: the guardrail became the attack surface in 2026 (NeMo CVEs fixed in 2.7.3 + Cato CTRL model-file RCE)
- [x] 06 — AI gateway / LLM-proxy security *(delivered)* — LiteLLM vs Portkey vs Bifrost; fresh hook: the gateway became the attack surface in 2026 (LiteLLM PyPI supply-chain compromise + CVE-2026-42208 pre-auth SQLi on CISA KEV; Portkey open-sourced + PANW acquisition intent)
- [x] 07 — Commercial AI firewalls *(delivered)* — pivoted to open-source self-hostable agent firewalls: Pipelock vs Meta LlamaFirewall vs Invariant Gateway; fresh hook: every commercial firewall this was going to feature (Lakera, Prompt Security, Protect AI Guardian) got acquired in 2025 and can't run on a no-egress lab, so the story is the OSS challengers defending the agent's outbound-traffic exfil boundary
- [x] 08 — PII / secrets redaction before the model *(delivered)* — Presidio (now Data Privacy Stack) vs OpenAI Privacy Filter vs GLiNER2-PII vs LLM Guard's secrets lane; fresh hook: the redaction layer stopped being a regex problem in one quarter of 2026 (OpenAI open-weighted Privacy Filter 23 Apr; Fastino's GLiNER2-PII topped the SPY benchmark in May; Presidio left Microsoft and its images moved to ghcr.io) — measured not on benchmark F1 but on what actually reaches a stub model that logs every token it receives

## Notes for each build
- Same fixed 7-criterion scorecard rubric (install 15%, detection/efficacy 30%, signal quality
  15%, performance 10%, usability 10%, docs 10%, value 10%).
- Fair-test rule: same target, same attack scenario, same clean container state; only the tool
  under test changes.
- Targets are vulnerable **LLM apps / agents / MCP servers / model files**, all as Docker
  containers on an isolated network with no egress.
- All quantitative results stay as `[FILL]` until a real lab run produces them.
- "Bypass" episodes: benign payloads only, responsible disclosure, no weaponized exploit shipped.

## Runway — themes (specific matchups chosen and revealed at launch)

The franchise is the **reproducible Docker head-to-head + 7-criterion scorecard**, NOT any one
product. Three interchangeable fuel sources keep it from running dry: (A) product matchups,
(B) technique/bypass episodes, (C) the incident case-study stream — plus an evergreen repurposing
lane once the catalog ages.

### A. Product-matchup themes (next up)
- ~~Commercial AI firewalls~~ *(delivered as ep07 — pivoted to OSS self-hostable agent firewalls; the commercial ones all got acquired in 2025 and can't run on a no-egress lab)*
- ~~PII / secrets redaction before the model~~ *(delivered as ep08 — Presidio vs OpenAI Privacy Filter vs GLiNER2-PII vs LLM Guard)*
- Model provenance / signing / AI-SBOM  ← **next up** (teased in ep08 outro)
- Jailbreak / injection classifier bake-off
- Agent sandboxing / tool isolation
- RAG / vector-DB poisoning: detection + defense
- LLM output validation / structured-output guards
- LLM DLP / data-egress controls at the gateway
- AI-generated-code security scanning
- Deepfake / voice-clone / synthetic-media detection

### B. Technique / bypass themes (a fresh attack vs the defenses — no new product required)
- Indirect / second-order prompt injection via a poisoned retrieved doc
- Tokenizer-gap evasion (variation selectors / zero-width / homoglyphs)
- Multi-turn "crescendo" jailbreaks vs single-turn guards
- MCP tool-description / rug-pull attacks vs runtime gateways
- Data exfil via markdown-image/link rendering in chat UIs

### C. Incident case-study stream (weekly AccessQuint LinkedIn — effectively inexhaustible)
A new named breach / agentic incident as it lands, each mapped to the authority-in-the-artifact
thesis. Fresh incidents refill this weekly with zero product dependency.

### D. Evergreen / repurposing (once the catalog ages ~6–8 weeks)
- "Same tool, one year later" — re-run the scorecard as tools update; an evergreen refresh.
- Recycle aged posts into new formats (carousel, poll, "5 lessons," myth-buster) and repost to a
  *different* group, where audience overlap is low, so it reads as new reach.
- Every episode fans out to ~5 assets (native post, carousel, poll, 2–3 group cross-posts), so
  output stretches well past input.
