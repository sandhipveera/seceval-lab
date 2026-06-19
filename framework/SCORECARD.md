# Scorecard Rubric (fixed across every episode)

Score each product 1–5 on each criterion. Keep the criteria and weights identical for the
whole series — that consistency is what makes your scores trustworthy and comparable.

| # | Criterion | Weight | What 1 looks like | What 5 looks like |
|---|---|---|---|---|
| 1 | Ease of install/setup | 15% | Hours of yak-shaving, broken docs | One script, minutes, great docs |
| 2 | Detection / core efficacy | 30% | Misses obvious attacks | Catches everything, few false positives |
| 3 | Signal quality (low noise) | 15% | Alert fatigue, tons of FPs | Clean, actionable alerts |
| 4 | Performance / resource cost | 10% | Hogs CPU/RAM | Light, scales on modest hardware |
| 5 | Usability / UX / dashboards | 10% | CLI-only, confusing | Clear UI, good workflow |
| 6 | Docs & community | 10% | Sparse, stale | Excellent docs, active community |
| 7 | Value (vs price/tier) | 10% | Overpriced for what it does | Strong value, fair pricing |

**Weighted total** = Σ(score × weight). Report the number AND a one-line justification per
criterion. Never give a score you can't defend with an observed artifact.

## Worked example (format only)

```
Suricata
1. Install ............ 4  (single compose file, ~6 min)
2. Detection ......... 5  (caught 18/18 scenario alerts)
3. Signal quality .... 3  (noisy without tuning rulesets)
4. Performance ....... 4  (peak 38% CPU, 410MB RAM)
5. Usability ......... 2  (no native UI; needs EveBox/Kibana)
6. Docs/community .... 5
7. Value ............. 5  (free, open source)
Weighted total: 4.15 / 5
```
