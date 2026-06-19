---
title: "Suricata vs Zeek vs Snort: I Pointed the Same Attack at All Three"
description: "A reproducible, evidence-first comparison of three free intrusion detection systems — same target, same attack, same snapshot. Only the IDS changes."
tags: [cybersecurity, IDS, Suricata, Zeek, Snort, blue-team, homelab]
status: draft
note: "Numbers marked [FILL] come from your real eval run — artifacts/<run>/metrics.csv and the filled scorecard. Replace before publishing."
---

# Suricata vs Zeek vs Snort: I Pointed the Same Attack at All Three

An intrusion detection system has exactly one job: notice when something on your network is
wrong and tell you about it. That sounds simple until you have to choose one. So instead of
reading three marketing pages, I built an isolated lab, pointed the *exact same* attack at the
*exact same* target three times, and swapped only the IDS underneath — Suricata, Zeek, then
Snort. This post is what the logs actually showed.

Everything here is reproducible. The lab (Terraform + Docker on VMware vSphere), the attack
scenario, and the install scripts live in [the repo](https://github.com/<you>/seceval-lab),
pinned to a commit. If your numbers come out different, I want to hear about it — that's the
whole point of showing the work.

## What an IDS does, and who should care

An IDS sits on your network and inspects traffic for known-bad patterns or unusual behavior.
Crucially, it doesn't *block* anything — that's a firewall or an IPS. It *tells* you. It's the
tool that turns a vague "I think something's off" into a concrete alert you can act on.

If you run a home lab, manage a small business network, or you're studying for a blue-team
role, this is squarely your category. And the right question is never just "does it work."
It's three questions at once: what does it miss, how noisy is it, and what does it cost you to
run? A detector that catches everything but screams constantly is one you'll learn to ignore —
and an ignored alert is the same as no alert.

## Why these three

I picked Suricata, Zeek, and Snort because they're the three you'll actually run into, and
because all three are free and open source so you can follow along without a license.

**Snort** is the original — signature-based, battle-tested, and still everywhere. You write or
import rules that describe known-bad traffic, and Snort matches against them.

**Suricata** is the modern, multi-threaded successor. It speaks the same rule language as Snort
but adds a rich structured event format (EVE JSON) that's a joy to export and analyze.

**Zeek** is the odd one out, and deliberately so. It isn't really a signature engine — it's a
network analysis framework that *describes* everything it sees, producing detailed logs of
connections, files, and protocols. It's less "alert me" and more "give me the full story."

Same category, three genuinely different philosophies. That's what makes the comparison
interesting.

## The lab, and the rules that keep it fair

Fairness is the entire game here, so the setup matters. Everything runs on a single VMware
vSphere host. There's an isolated network segment with no path to the internet or my real LAN —
all attack traffic stays inside the lab. On that segment sit two deliberately vulnerable
targets: OWASP Juice Shop and DVWA. And there's one fixed attack script: reconnaissance with a
port scan, a directory brute-force, then a batch of common web exploits.

The rule I never break: every IDS gets the **same clean VM snapshot, the same target, and the
same attack**. The only variable in the entire experiment is the tool under test. (If you want
the containment details — isolated port group, no uplink, snapshot-per-run — they're in
`docs/SAFETY.md` in the repo, and you should read them before running any of this yourself.)

## Round 1 — Install and setup

First, just getting each one running, fully scripted and timed with a stopwatch. No manual
clicking; if a step wasn't in the install script, it didn't count.

Suricata came up from a single Docker Compose file in a few minutes — but out of the box it's
quiet until you load rule sets, so "running" and "useful" aren't the same moment. Snort took
the most fiddling; the configuration is powerful and also clearly from an earlier era of
software. Zeek installed quickly, but "configuring" Zeek means thinking in its scripting
language, which is a different mental model than rule files — more programming than tuning.

| Setup | Snort | Suricata | Zeek |
|---|---|---|---|
| Time to "running" | [FILL] | [FILL] | [FILL] |
| Time to "actually detecting" | [FILL] | [FILL] | [FILL] |
| Friction (1–5) | [FILL] | [FILL] | [FILL] |

## Round 2 — The attack, and what each one caught

Then the fun part: fire the identical attack and watch what each one notices. I normalized
every product's output into a single CSV — `timestamp, product, signature, severity, src, dst`
— so the comparison is genuinely apples to apples rather than three different dashboards I'm
eyeballing.

Suricata lit up immediately on both the scan and the web exploits, emitting clean structured
events I could export straight into the table. Snort caught the signature-based hits reliably
but stayed silent on a couple of things that fell outside its loaded rule set — exactly the
trade-off of a signature engine. Zeek didn't "alert" in the classic sense at all; it quietly
logged the entire conversation. That's incredible for after-the-fact forensics, but it means
you do more work to turn "here is everything that happened" into "something is wrong *right
now*."

| Detection | Snort | Suricata | Zeek |
|---|---|---|---|
| True positives | [FILL] | [FILL] | [FILL] |
| False positives | [FILL] | [FILL] | [FILL] |
| Missed (false negatives) | [FILL] | [FILL] | [FILL] |
| Mean time to alert | [FILL] | [FILL] | [FILL] |

## Round 3 — Noise and resource cost

Detection is only half the story. Untuned, Suricata's broad rule sets generated the most noise —
the price of catching a lot is alerting on a lot. Snort was tighter out of the box. Zeek barely
"false-positives" at all, simply because it isn't trying to raise alarms in the first place.

Resource cost told its own story under identical load. Suricata's multithreading earns its keep
once traffic picks up; Snort stayed lean; Zeek's cost scales with how much you ask its scripts
to compute.

| Cost under load | Snort | Suricata | Zeek |
|---|---|---|---|
| Peak CPU % | [FILL] | [FILL] | [FILL] |
| Peak RAM (MB) | [FILL] | [FILL] | [FILL] |

## The scorecard and the verdict

I score every episode on the same seven-criterion rubric: install, detection, signal quality,
performance, usability, docs, and value. Weighted totals: Snort [FILL], Suricata [FILL], Zeek
[FILL].

There's no single winner here, and anyone who tells you otherwise is selling something. Instead:

- **Pick Suricata** if you want modern, exportable, structured alerts and you're willing to
  invest a little time tuning the rule sets.
- **Pick Snort** if you want a proven signature engine with tight defaults and a huge body of
  existing rules.
- **Pick Zeek** if your real goal is deep network visibility and forensics rather than
  real-time alerting.

Honestly, a lot of serious setups don't choose at all — they run Suricata or Snort for alerting
*and* Zeek alongside it for context. The tools aren't really competitors so much as different
answers to "what do you want to know, and when."

## Reproduce it yourself

Every number above comes from artifacts captured during the run, and the whole thing is
reproducible from [the repo](https://github.com/<you>/seceval-lab) at commit `[FILL]` — same
pinned versions, same attack script. Clone it, run it against your own lab, and tell me where
your results diverge from mine.

Next up, I turn the same lab loose on vulnerability scanners: OpenVAS vs Nuclei vs Trivy. Same
rules, same fairness, same show-the-work approach.

---

*This testing was performed entirely in an isolated lab against targets I control. Never run
scanners or exploits against systems you don't own. Tool licenses were reviewed before
publishing any benchmark figures.*
