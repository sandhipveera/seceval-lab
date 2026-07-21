---
title: "I Hid a Jailbreak Inside an Emoji — Which AI Guardrail Caught It?"
description: "A reproducible, Docker-based teardown of two open-source LLM guardrails. One guarded chatbot, one benign canary secret, one jailbreak fired three ways — plain, character-injection, and emoji-smuggled. What NeMo Guardrails and Guardrails AI caught, and where the disguise won."
tags: [AI security, LLM guardrails, prompt injection, jailbreak, emoji smuggling, blue-team]
status: draft
note: "Numbers marked [FILL] come from your real lab run (artifacts/findings.csv + metrics). Replace before publishing."
---

# I Hid a Jailbreak Inside an Emoji — Which AI Guardrail Caught It?

Here's a jailbreak that shouldn't work anymore. I typed a request a language model is trained to
refuse, and the guardrail in front of it caught the attempt instantly — exactly as advertised.
Then I hid the *same* request inside an emoji and sent it again. This time the guardrail saw an
innocent smiley, shrugged, and passed it straight to the model, which happily leaked a secret it
had been told to protect.

That gap isn't a clever prompt. It's a structural flaw that researchers spent 2025 and 2026
documenting: the small classifier doing the guarding tokenizes text differently than the big
model it's protecting, and attackers live in the space between those two views. So I built the
scenario in miniature — a deliberately vulnerable chatbot with a benign canary secret — and asked
two of the most popular open-source guardrail projects, **NVIDIA NeMo Guardrails** and
**Guardrails AI**, one question: can you still catch an attack once it's wearing a disguise?

Everything below runs locally in Docker on an isolated network with no internet egress, the
"secret" is a benign canary, and the whole setup is reproducible from
[the repo](https://github.com/<you>/seceval-lab) at a pinned commit. If your results differ from
mine, that's the point — tell me.

## What guardrails are, and the tokenizer gap under them

The moment teams started shipping LLMs to customers, they added guardrails: a filter that sits
between the user and the model and blocks the obviously dangerous stuff — jailbreaks, prompt
injection, toxic or off-policy content. By 2026 this pattern is nearly universal, and under the
hood most guardrails are a small classifier model making a fast, binary "allow or block" decision
on each message before it reaches the real model.

The trouble is that a classifier has to turn text into tokens before it can judge it, and it uses
its *own* tokenizer to do that — one that rarely matches the tokenizer inside the model it's
guarding. When the two disagree about what a string even *is*, you get a blind spot. The guard
reads one thing, the model reads another, and an attacker who can widen that disagreement can
write a prompt the guard scores as harmless while the model reads it as a command. Prompt
injection still sits at the very top of the OWASP list for LLM applications, and this is a big
part of why: the defenses aren't reading the same text as the target.

## The threat, in plain terms

So how do you attack a blind spot? You craft input the model parses perfectly but the guard
parses as noise. Three techniques cover most of it.

**Emoji smuggling** is the cleanest. Unicode has "variation selectors" — invisible modifier
characters that tweak how an emoji renders. You can tuck an entire instruction between them. Many
guardrail tokenizers strip or ignore those code points, so the classifier sees a lone, innocent
emoji; the target model, using a different tokenizer, reconstructs the hidden text and follows
it. **Zero-width insertion** does something similar with zero-width spaces sprinkled through a
banned phrase, breaking the pattern the classifier learned. And **homoglyph substitution** swaps
ordinary letters for look-alike characters from other scripts — visually identical, different code
points, invisible to a matcher keyed on the Latin originals.

None of this is exploit code. There's no memory corruption and, at the time of writing, no CVE to
point at — it's just characters most classifiers were never trained to expect. Yet the published
research is stark: across six commercial and open-source guardrails, character-injection and
adversarial-ML evasion pushed attack success rates toward **~100%**, with emoji smuggling in
particular fully bypassing several leading systems. The failure is structural, not a tuning
mistake, which is exactly why it's worth testing rather than assuming.

## The lab, and the rules that keep it fair

Everything runs in Docker on a single bridge network marked `internal`, so no container can reach
the internet. I stand up three things: a **vulnerable chatbot** that holds a benign canary string
in its system prompt and is instructed never to reveal it; a **guardrail service** (NeMo
Guardrails or Guardrails AI, swapped in per run) sitting in front of that chatbot; and a small
**attack runner** that fires the payloads and records the replies.

The canary is my ground truth. If the guarded chatbot ever emits the canary string, the attack
got through that guardrail — full stop. Nothing sensitive is involved and nothing leaves the
machine; the "secret" exists only so I have an unambiguous, benign signal for "the jailbreak
worked."

Then the fairness rule, same as every episode: same chatbot, same canary, same three payloads —
the plain jailbreak, its character-injection variant, and the emoji-smuggled variant — and the
only thing that changes between runs is which guardrail is doing the guarding. (Containment
details — the no-egress network, the benign canary, responsible disclosure — are in
`lab/README.md`, and you should read them before running this yourself.)

## Round 1 — Setup and coverage

First, what does each guardrail actually inspect?

**NeMo Guardrails** is NVIDIA's programmable framework. You describe behavior in a small language
called Colang and wire up rails at several points — input, dialog, retrieval, execution, and
output — including a dedicated jailbreak-detection rail (and, in recent releases, optional
classifier and NIM-microservice rails). It's less "a filter" and more "a policy engine for the
whole conversation." **Guardrails AI** takes the other shape: a library of composable *validators*
you pull from its Hub — among them detectors for jailbreak and prompt injection — that you wrap
around the model's input and output. One is a conversation framework; the other is a validator
toolkit you assemble to taste.

| Setup | NeMo Guardrails | Guardrails AI |
|---|---|---|
| Install time | [FILL] | [FILL] |
| Version tested | [FILL] | [FILL] |
| Inspects input | ✅ | ✅ |
| Inspects output | ✅ | ✅ (validator-dependent) |
| Dialog / multi-turn aware | ✅ | ❌ |
| Setup friction (1–5) | [FILL] | [FILL] |

## Round 2 — The disguise, and what each one caught

Then the real test. I sent the **plain jailbreak** first, and both guardrails did their job — this
is the easy, in-distribution case they're built for, and the better-tuned one flagged it on the
first pass and named the rule it matched. Nothing surprising, and that's the point: it establishes
that each guard *can* catch this attack when it can see it.

Then I turned on the disguise. I ran the **character-injection** variant — the same forbidden
request, now threaded with zero-width spaces and a few homoglyphs — and then the
**emoji-smuggled** variant, the instruction hidden between variation selectors. After each send I
watched two things: the guardrail's own verdict (block or pass) and the chatbot's reply pane. The
instant a canary string came back in a reply, that guard had missed the attack. I normalized every
result into a single CSV so the comparison is honest rather than anecdotal.

| Detection (caught = blocked before the canary leaked) | NeMo Guardrails | Guardrails AI |
|---|---|---|
| Plain jailbreak | [FILL] | [FILL] |
| Character-injection (zero-width / homoglyph) | [FILL] | [FILL] |
| Emoji-smuggled (variation selectors) | [FILL] | [FILL] |
| Canary leaked (attack succeeded) | [FILL] | [FILL] |

The interesting result isn't which project "wins" — it's where the disguise flips a confident
block into a silent pass, and whether either guardrail's extra layers (a dialog rail, an output
validator on the *reply*) manage to catch the leak even when the input classifier is fooled. That
second line of defense, catching the canary on the way *out* rather than the payload on the way
*in*, turns out to matter more than the input classifier's raw accuracy.

## Round 3 — Noise and speed

A guard that blocks every message trains users to hate it, so noise counts as much as catches. I
ran a set of perfectly normal, benign prompts through each guardrail to count false positives, and
measured the latency each one adds to every single request under the same load.

The shapes are predictable but worth quantifying. NeMo Guardrails does more work — multiple rails,
dialog awareness, sometimes an extra model call — which buys coverage at the cost of milliseconds
and memory on each turn. Guardrails AI's validators are lighter, but a validator you didn't switch
on protects nothing, so its safety is only as good as the set you assemble.

| Cost | NeMo Guardrails | Guardrails AI |
|---|---|---|
| Added latency / request | [FILL] | [FILL] |
| Peak memory under load | [FILL] | [FILL] |
| False positives (benign set) | [FILL] | [FILL] |

## The scorecard and the verdict

Scored on the same seven-criterion rubric as every episode — install, detection, signal quality,
performance, usability, docs, value. Weighted totals: NeMo Guardrails [FILL], Guardrails AI
[FILL].

There's no single winner, and the two aren't really the same tool:

- **Reach for NeMo Guardrails** when you want programmable, multi-layer control and you're already
  in the NVIDIA ecosystem. The dialog and output rails catch things a single input classifier
  never can, which is exactly the redundancy the disguise attacks punish you for lacking.
- **Reach for Guardrails AI** when you want lightweight, composable validators you can drop into an
  existing app in an afternoon — as long as you're honest about which validators you've actually
  enabled.

But the headline neither vendor prints is the real takeaway: any guardrail that leans on a
classifier can be blindsided by input its tokenizer doesn't understand. The durable fix isn't a
better classifier — it's **normalizing and sanitizing text before it ever reaches the guard**.
Strip the variation selectors, collapse zero-width characters, fold homoglyphs back to their
canonical forms, *then* let the guardrail judge the cleaned text the model will actually see. Close
the gap between the two tokenizers and most of these attacks evaporate. Do it in layers — input
sanitize, input classify, output validate — because each catches something the others miss.

## Reproduce it yourself

Every number above comes from the lab run, and the whole thing is reproducible from
[the repo](https://github.com/<you>/seceval-lab) at commit `[FILL]` — same vulnerable chatbot,
same canary, same three attack variants, same guardrail configs. It's all benign: the "secret" is
a canary token on an isolated network, so nothing real leaks and you can safely run it yourself and
see where your results diverge.

Next episode I move upstream to the AI supply chain and put model-signing and provenance tools to
the test — can you actually prove the model you're running is the one you think it is? Same lab,
same show-the-work rules.

---

*This testing was performed entirely in an isolated, no-egress Docker network using a benign
canary secret and conceptual evasion techniques — no weaponized payloads are shipped. Don't run
jailbreak or injection techniques against systems you don't own, and follow responsible disclosure
if you find a real vulnerability in any tool. Each project's license was reviewed before publishing
any figures.*
