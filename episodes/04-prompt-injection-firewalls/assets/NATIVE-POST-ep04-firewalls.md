<!-- NATIVE FEED POST (personal profile) — NOT an Article. Paste into "Start a post".
     Attach: the Ep.04 abstract hero as native image, or the 5-slide carousel PDF as a document.
     Link in FIRST COMMENT only. Post Tue–Thu ~8–10am PT; reply to every comment in the first 90 min. -->

# Native post body (~2,000 chars — under the 3,000 limit)

I set out to test four of the best-known prompt-injection firewalls against one vulnerable AI app — LLM Guard, Rebuff, Vigil, and Meta's Prompt Guard 2.

Only two of them would even run.

Prompt Guard 2 sits behind Meta's Llama license — my access request was still "pending," so I couldn't even download the model. Vigil wouldn't build in a clean offline container after three rounds of dependency surgery and six separate blockers. That's finding #1, and it's the one no vendor puts on a slide: half the best-known field doesn't install cleanly.

For the two that ran, I sent an escalating battery — plain injection, then spaced/homoglyph/base64 obfuscation, then an indirect attack hidden inside a document the app retrieves. Both LLM Guard and Rebuff caught all six. On detection alone, a perfect tie.

Then I ran the test that actually matters: the benign set. Harmless prompts that just happen to contain scary words like "ignore" or "password reset."

→ LLM Guard over-blocked 2 of 6 (33%), at 449ms per call.
→ Rebuff over-blocked 4 of 6 (67%), at 3.7 SECONDS per call — peaking near 9s.

A guard that blocks two-thirds of your innocent traffic at 3.7 seconds a request isn't a firewall. It's a denial-of-service on your own users. Without the false-positive test, I'd have called it a tie and been completely wrong.

The uncomfortable lesson: a single classifier is a speed bump, not a wall. Detection scores all look great until you measure what they block by mistake and how long they take. So you layer — a fast, low-false-positive gate at the door, output checks behind the model, canary tokens to catch leaks, and least-privilege so a caught injection can't reach anything worth stealing.

The firewall is never your only line — and it's never as easy to deploy as the README claims.

Full teardown + the reproducible lab (it caught six of its own bugs along the way) 👇

#AISecurity #promptinjection #LLMsecurity #appsec

---

# First comment (post immediately after)

Full write-up + the fully reproducible lab (same vulnerable app, same battery, all firewall configs, benign canary, isolated Docker): github.com/sandhipveera/seceval-lab (@98f511f). Clone it and check my numbers — these classifiers are very input-sensitive, so I'd expect some to differ.

---

# Carousel slide plan (abstract house style)
1. COVER — Ep.04 hero (four gates, two dark) + "4 prompt-injection firewalls. Only 2 would even run."
2. TWO NEVER STARTED — Prompt Guard 2 (Meta license, pending) / Vigil (won't build offline, 6 blockers).
3. THE BATTERY — both survivors caught all 6 (plain, obfuscated, base64, indirect doc). A perfect tie... on detection.
4. THE TIE-BREAKER — FP + latency: LLM Guard 33% / 449ms vs Rebuff 67% / 3.7s. One is deployable, one isn't.
5. VERDICT — LLM Guard 8.1, Rebuff 6.7; PG2 + Vigil not evaluated. Layer them; the firewall is never the only line.

# Checklist
1. Paste body → attach carousel PDF (document) or the hero image.
2. Post Tue–Thu ~8–10am PT.
3. First comment with repo link immediately.
4. Reply to every comment in the first 90 min.
5. A day later, cross-post the question version into ONE group (CISO2CISO / Information Security Community).
