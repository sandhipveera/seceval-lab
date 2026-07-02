# Episode Backlog — AI Security Series

Ordered by traction potential (newest / least-covered first; "tried-and-tested" tools are
fallbacks only). The weekly task pulls the next unchecked entry, delivers its package into
`episodes/<NN>-<slug>/`, and checks it off. All episodes run **locally in Docker**.

## Active slate (AI security)

- [x] 01 — MCP / agent security teardown: poisoned MCP server vs mcp-scan / Golf Scanner *(delivered)*
- [x] 02 — "I beat the AI model scanner": picklescan 2025 bypasses vs ModelScan / ModelAudit / fickling *(delivered)*
- [ ] 03 — LLM red-team showdown: Garak vs PyRIT vs Promptfoo
- [ ] 04 — Prompt-injection firewalls: LLM Guard vs Vigil vs Rebuff vs Prompt Guard 2

## Fallbacks (only if a fresher matchup slips — saturated / lower lab-fit)

- [ ] F1 — AI SOC explainer / react: what an autonomous SOC analyst actually does
- [ ] F2 — NeMo Guardrails vs Guardrails AI deep-dive (needs a novel test angle, e.g. a live bypass)

## Notes for each build
- Same fixed 7-criterion scorecard rubric (install 15%, detection/efficacy 30%, signal quality
  15%, performance 10%, usability 10%, docs 10%, value 10%).
- Fair-test rule: same target, same attack scenario, same clean container state; only the tool
  under test changes.
- Targets shift from "vulnerable web app" to vulnerable **LLM app / agent / MCP server / model
  file**, all as Docker containers on an isolated network with no egress.
- All quantitative results stay as `[FILL]` until a real lab run produces them.
- "Bypass" episodes: benign payloads only, responsible disclosure, no weaponized exploit shipped.

## Backlog (refill — research fresh before reaching these)
- [ ] AI gateway / LLM proxy security: Bifrost vs LiteLLM guardrails vs Portkey
- [ ] RAG data-poisoning detection
- [ ] AI-SBOM / model provenance: Sigstore model signing, CycloneDX-ML
- [ ] Deepfake / synthetic-media detection tools
