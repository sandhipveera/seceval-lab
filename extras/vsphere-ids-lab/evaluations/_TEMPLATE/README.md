# Security Product Evaluation — Template

> Copy this file into `evaluations/<slug>/README.md` for every new product or head-to-head.
> One filled-in copy = one blog post + one video script. Keep the section order identical
> across episodes so the series stays recognizable and comparisons stay fair.

---

## 0. Front matter (fill before testing)

| Field | Value |
|---|---|
| Eval slug | `e.g. ids-suricata-vs-zeek-vs-snort` |
| Category | `IDS / EDR / Vuln scanner / SIEM / WAF / SAST / ...` |
| Products under test | |
| Versions | |
| Date tested | |
| Lab commit hash | `git rev-parse --short HEAD` — for reproducibility |
| Target box(es) | `e.g. OWASP Juice Shop, Metasploitable2` |
| Attack scenario(s) | `link to attack-range/scenarios/*.yml` |
| Tester | |

---

## 1. The job to be done

What problem does this category solve, and **who is this for** (home lab, SMB, enterprise SOC)?
2–3 sentences. This frames the whole review and is your video cold-open.

## 2. Why these products

Why this shortlist? Market position, popularity, price tier, open-source vs commercial.
Note anything you deliberately excluded and why.

## 3. Setup & install

For **each** product, record honestly:

- Install method (script in `evaluations/<slug>/install.sh`)
- Time from zero to "ready to test" (wall-clock)
- Friction / gotchas / docs quality (1–5)
- Default config sanity (secure by default? noisy? )

> The install must be fully scripted. If you typed it by hand, it doesn't count — put it in the script.

## 4. Test methodology

State this **before** results so the review is credible:

- Identical target box and identical attack scenario across all products
- Exact payloads / PCAPs / scan profiles used (committed in repo)
- How many runs, and how you handle variance
- What "detection" or "success" means for this category (define the pass/fail line)

## 5. Results

The evidence section. Pull from captured artifacts, don't eyeball.

| Metric | Product A | Product B | Product C |
|---|---|---|---|
| True positives | | | |
| False positives | | | |
| Missed (false negatives) | | | |
| Mean time to alert | | | |
| Setup time | | | |
| Peak CPU % | | | |
| Peak RAM (MB) | | | |
| Disk footprint (MB) | | | |

Attach: screenshots (`artifacts/<run>/screenshots/`), alert exports, raw metric CSVs.

## 6. Resource cost

How heavy is each product at idle and under load? Is it realistic for the target audience's
hardware? Pull from `scripts/capture/capture_metrics.sh` output.

## 7. Pros / cons

For each product, 3–5 bullets each way. Be specific and tied to what you observed — not
marketing copy.

## 8. Scorecard

Score each product 1–5 on the fixed criteria in `docs/SCORECARD.md`. Same criteria every
episode. Show the weighted total.

## 9. Verdict — who should pick what

No single "winner." Map products to audiences: "Pick A if… / Pick B if… / Avoid C when…"

## 10. Reproduce it yourself

Link to the exact commit, the install scripts, and the attack scenario. Invite viewers to
re-run. This reproducibility is your differentiator — most reviewers can't show their work.

---

### Artifact checklist (must exist before publishing)

- [ ] `install.sh` runs clean on a fresh snapshot
- [ ] `test.sh` runs the scenario and exits 0
- [ ] `artifacts/<run>/metrics.csv` captured
- [ ] Screenshots captured for each product
- [ ] Scorecard filled with justification per score
- [ ] SAFETY.md containment checklist confirmed (lab network only)
