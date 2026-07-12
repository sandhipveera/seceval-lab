<!-- EP03 LinkedIn publish kit — post ONLY once the blog page + repo are LIVE (git push done).
     Format: long-form ARTICLE on Veera's PERSONAL profile.
     Target time: Tue 2026-07-14, 9:30 AM ET. -->

# Episode 03 — LinkedIn publish kit

## Article headline (paste into the LinkedIn Article title field)

I Attacked My Own AI Agent — Which Red-Team Tool Broke It First?

## Article body

Use `assets/linkedin_article.html` — render it and paste the formatted text into the LinkedIn
Article editor, then drop the scorecard image where the `[[ INSERT SCORECARD IMAGE ]]` note sits.

---

## ⚠️ Scheduling note (important)

LinkedIn's native scheduler works for **feed posts only** — **Articles cannot be scheduled**; they
publish immediately when you hit Publish. So "Tue 9:30am ET" is handled as a **reminder** to publish
the article manually at that time. (If you'd rather have it auto-post, we switch the format to a feed
text post — say the word and I'll reshape the copy.)

---

## Companion feed post (optional — post right after publishing the Article, to drive reach)

I spent this week getting three LLM red-team frameworks to attack the same deliberately-weak AI agent — Garak, PyRIT, and Promptfoo — to answer one question: which one catches an agent being talked into **misusing its tools** before an auditor does?

Only one of the three landed a real hit. One flagged three "breaks" that were all scoring artifacts. And the third couldn't run its best attacks at all without phoning home to a cloud service.

Same target, same canary, 100% local and reproducible — I show all the work, including the twist where the frontier model I hired as the attacker *refused to attack*.

Full teardown + the scorecard 👇 (article on my profile)

Which of these are you running today — and would it have caught the tool-misuse?

#AISecurity #LLMSecurity #RedTeam #AIagents #PromptInjection

---

## Notes
- Post order: (1) git push so the repo link resolves, (2) publish the Article, (3) optionally the
  companion feed post pointing to it.
- Teases the result WITHOUT front-loading which tool won — the gap drives the read.
- Reply to every comment in the first 60–90 minutes.
- The "attacker that wouldn't attack" sidebar is the shareable hook — expect it to be quoted.
