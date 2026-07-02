---
title: "I Hid Malware in an AI Model — Which Scanner Caught It?"
description: "A reproducible, Docker-based teardown of AI model-file security. One benign-canary malicious model, four scanners — picklescan, ModelScan, ModelAudit, and fickling. What each caught, and what walked right past it."
tags: [AI security, pickle, model scanner, supply chain, picklescan, ModelScan, ModelAudit, fickling, blue-team]
status: draft
note: "Detection/cost tables + scorecard + canary ground-truth all filled from the real lab run (artifacts/findings.csv, metrics.csv, run_canary_check.sh). Only remaining pre-publish item: set the pinned commit hash after the first git push (repo URL is already set to github.com/sandhipveera/seceval-lab)."
---

# I Hid Malware in an AI Model — Which Scanner Caught It?

An AI model file can pass a security scanner and still run your attacker's code — and this year
that stopped being theoretical. In December 2025, JFrog's security team disclosed **three critical
zero-days in picklescan** (CVE-2025-10155, -10156, and -10157, each rated **CVSS 9.3**), the exact
scanner Hugging Face runs on every model uploaded to the Hub. All three let a malicious model slip
past as "safe" and execute code on load. They were fixed in picklescan **0.0.31**, but the deeper
lesson is that the "unscannable model file" is having a moment, and the tools we lean on are not
all equally hard to fool.

So I built the thing everyone should be worried about, in miniature: one malicious model file
carrying a benign canary payload, plus four different scanners tasked with catching it. Then I asked
the only question that matters — can you find what's hiding inside, even when I try to hide it well?

Everything below runs locally in Docker on an isolated network with no internet egress, the payload
is a benign canary, and the whole setup is reproducible from
[the repo](https://github.com/sandhipveera/seceval-lab) at a pinned commit. If your results differ from
mine, that's the point — tell me.

## Why the model file itself became an attack surface

Here's the uncomfortable part almost nobody tells you until it's too late. Most machine-learning
models are shipped as **pickle** files — Python's built-in object-serialization format. PyTorch's
`.bin` and `.pt` files are pickle under the hood; so are countless `.pkl` and `.model` artifacts.
And pickle is not a data format in the way JSON is a data format. A pickle is effectively a tiny
program: it contains opcodes, and one of them, `REDUCE`, calls an arbitrary callable with arbitrary
arguments. When you `torch.load()` a model, that program runs — *before* the model makes a single
prediction.

That means a model file can execute code the instant it's opened. Download a checkpoint from a
public hub, load it to "just check it works," and you may have already lost. Roughly **45%** of the
most popular models on Hugging Face still use pickle (per CCS 2025 research), so this isn't a fringe
concern — it's the default distribution format for a huge slice of the ecosystem. The thin layer of
protection between you and that embedded code is usually **picklescan**, which is precisely why
breaking picklescan has become such a big deal.

## The threat, in plain terms

You don't need a deep understanding of pickle bytecode to reason about the bypasses. Three patterns
cover most of what's actually being used against scanners in the wild.

**Blocklist evasion.** picklescan works from a blocklist of known-dangerous callables — things like
`os.system` and `posix.system`. But a blocklist only catches names it already knows. JFrog's
CVE-2025-10157 abused exactly this: import a *submodule* the list never enumerated (for example
`asyncio.unix_events` instead of `asyncio`) and the dangerous call executes while the string never
matches the blocklist. The academic paper *"The Art of Hide and Seek"* (Aug 2025) took this to its
logical conclusion, reporting an **89% bypass rate** against the best-performing scanner across 22
distinct model-loading paths, with a technique the authors call Exception-Oriented Programming.

**Renamed or broken archives.** picklescan has to recognize a file as a model before it can open it.
CVE-2025-10155 exploited a renamed pickle given a PyTorch extension: the scanner tried the
PyTorch-specific parser, hit an error, and returned *without* falling back to plain pickle analysis —
so the payload sailed through. ReversingLabs' **nullifAI** models, found live on Hugging Face in
February 2025, did the archive version: they used **7z** compression instead of the expected zip, so
picklescan couldn't even open the container. CVE-2025-10156 was the CRC variant — PyTorch happily
loads a corrupted archive that Python's `zipfile` refuses, so the malicious code runs but the scanner
chokes.

**Payload-then-break.** The nastiest of the classic tricks: put your payload at the *start* of the
pickle stream and a broken opcode right after it. The payload executes first; then the scanner hits
the error, reports a parse failure, and never mentions the malware it already walked past.

The insight is that most of these aren't exotic exploits. They're the natural failure modes of a
scanner that reasons about *names* and *file types* rather than *intent*. Which is exactly what makes
a head-to-head worth running.

## The lab, and the rules that keep it fair

Everything runs in Docker on a single bridge network marked `internal`, so no container can reach the
internet. I build **one** malicious model file whose embedded payload does exactly one thing: send a
request to an in-network **canary sink**. When the payload runs, the canary logs a hit — that hit is
my ground truth that the code executed. Nothing weaponized, nothing that leaves the host: the "attack"
is a benign tripwire.

From that one base file I generate a small family of variants — a plain payload, a **deep-import**
variant that dodges a naive blocklist, a **renamed** variant (pickle wearing a `.bin` extension), and
a **broken-archive** variant — so I can test each scanner against both the easy case and the evasive
ones. Then the fairness rule, same as every episode: each scanner inspects the *exact same files*, in
the *same clean container state*, and the only variable is the tool doing the catching. (Containment
details — the no-egress network, the benign canary, responsible disclosure — are in `lab/README.md`,
and you should read them before running this yourself.)

## Round 1 — Setup and coverage

First, what does each scanner even look at?

**picklescan** is the lightweight default and the one Hugging Face runs: a blocklist of dangerous
imports, fast and minimal. **ModelScan** (Protect AI) scans across several serialization formats
(pickle, HDF5/Keras, some others) and is what a lot of MLOps pipelines standardized on. **ModelAudit**
(Promptfoo, open-sourced in 2025) advertises the widest coverage — 40-plus formats, opcode-level
pickle analysis, built-in CVE rules, and SARIF output for CI. And **fickling** (Trail of Bits, with a
rewritten scanner shipped September 2025) flips the whole model: instead of a blocklist of bad
imports, it uses an **allowlist** of known-safe ones and treats everything else as suspect.

| Setup | picklescan | ModelScan | ModelAudit | fickling |
|---|---|---|---|---|
| Install | pip (pinned 0.0.31) | pip (0.8.5) | pip (0.2.4) | pip (0.1.3) + Python 3.11¹ |
| Approach | blocklist | blocklist + formats | opcode + rules | allowlist |
| Formats inspected | pickle-based only | pickle, HDF5/Keras, TF SavedModel | 40+ (pickle, safetensors, GGUF, ONNX, HDF5…) | pickle-based only |
| Opcode-level analysis | ❌ | partial | ✅ | ✅ |
| Setup friction (1–5) | 1 | 1 | 2 | 3¹ |

¹ fickling 0.1.3 imports the stdlib `distutils`, removed in Python 3.12, so this scanner pins to Python 3.11 (or needs a `setuptools<81` shim). The others install cleanly on 3.12.

## Round 2 — The payload, and what each one caught

Then the real test. I run all four scanners against the plain malicious file, then against the three
evasive variants, and I record a verdict per variant per scanner.

The plain payload is the easy case, and most tools catch it — a blocklist that names `os.system` will
flag `os.system`. The interesting story is the evasions. A blocklist that checks for an exact import
name gets walked past by a submodule it never listed (the CVE-2025-10157 pattern). A scanner that
trusts the file extension parses the renamed file with the wrong loader and reports nothing (the
CVE-2025-10155 pattern). And the allowlist approach behaves very differently from all of them — it
doesn't care what the dangerous import is *called*; it only cares whether the import is on the
known-safe list, so an unfamiliar callable is suspect by default whether or not anyone has enumerated
it as dangerous.

I normalized every result into a single CSV so the comparison is honest rather than vibes.

| Detection (caught / missed) | picklescan | ModelScan | ModelAudit | fickling |
|---|:---:|:---:|:---:|:---:|
| Plain payload (`builtins.eval`) | ✅ caught | ✅ caught | ✅ caught | ✅ caught |
| Same global via `STACK_GLOBAL` opcode | ✅ caught | ✅ caught | ✅ caught | ✅ caught |
| Renamed extension (`.pkl`→`.bin`) | ✅ caught | ❌ **not scanned** | ✅ caught | ✅ caught |
| Broken / non-zip archive | ❌ **mis-parse** | ❌ **not scanned** | ✅ caught | ✅ caught |
| **Total (of 4 variants)** | **3/4** | **2/4** | **4/4** | **4/4** |

Two details make this an honest test rather than a rigged one. First, the payload routes through
`builtins.eval` — a *known-bad* global every serious scanner blocklists — so the plain case is a fair
true-positive baseline, not a trick built on an unrecognized custom symbol. Every tool catches it, as
it should. Second, the same known-bad global delivered via the `STACK_GLOBAL` opcode (instead of the
classic textual `GLOBAL` line) is *also* caught by all four — modern parsers walk both opcode forms,
so that particular evasion no longer buys an attacker anything here.

The real misses are structural. ModelScan flagged `eval` as **CRITICAL** whenever it actually opened
the file — but it routes by extension and **never scanned** the `.bin`-renamed file or the
broken-archive file at all (`total_scanned=0` in its own report). picklescan inspects regardless of
extension or opcode form, but **mis-parses** the broken-archive container and reports nothing for it.
Only ModelAudit (behavioral binary-pattern + reference scan) and fickling (allowlist) caught all four,
because neither depends on extension routing or a cleanly-parseable container.

*(Note: results assume patched, current versions of each tool. The point isn't to re-fire the disclosed
CVEs — those are fixed — it's to see how each detection *philosophy* holds up against the *class* of
evasion those CVEs represent. The `deep_import` variant here exercises the `STACK_GLOBAL` opcode-form
delivery, not the CVE-2025-10157 submodule trick, which is patched and not reproduced.)*

> **Ground truth (canary check).** Loading each file in the isolated loader confirmed all four
> malicious variants actually execute code — the canary sink logged a hit for `plain`, `deep_import`,
> `renamed`, *and* `broken_archive` — while all three clean models stayed silent. That's the important
> part: the files ModelScan never scanned (`.bin`-renamed, broken-archive) and the one picklescan
> mis-parsed are **genuinely live**, so those "safe"/skipped verdicts are true misses on working
> payloads, not false alarms about dead files.

## Round 3 — Noise and cost

A scanner that screams at every legitimate model trains you to ignore it, so false positives matter as
much as catches — and this is where an allowlist can bite back, flagging perfectly safe but unfamiliar
imports as suspicious. I ran every tool against a set of clean, benign models (a couple of small real
checkpoints and some synthetic ones) and counted the false alarms, then timed each scan across small
and large files. Deeper opcode analysis costs wall-clock time; a stricter allowlist costs review
friction.

| Cost | picklescan | ModelScan | ModelAudit | fickling |
|---|---|---|---|---|
| Scan time (small / large²) | ~0.03 ms / 0.3 ms | 89 ms / 124 ms | 454 ms / 463 ms | 52 ms / 54 ms |
| False positives on clean models | 0 / 3 | 0 / 3 | 0 / 3 | 0 / 3 |
| Peak RAM under load³ | 23 MB | 35 MB | 119 MB | 34 MB |

² All model files in this lab are tiny (59–205 bytes), so "large" is nominal — the scan-time gap
reflects each tool's fixed startup/analysis overhead, not size scaling. picklescan is effectively
instant; ModelAudit's deeper opcode + pattern analysis is ~10× slower but still sub-second.

³ Peak resident memory is each scanner's own `getrusage` high-water mark (process + children),
recorded in-process so the figure is race-free and comparable across tools. picklescan is the
lightest; ModelAudit's broader format/opcode analysis costs the most.

## The scorecard and the verdict

Scored on the same seven-criterion rubric as every episode — install (15%), detection/efficacy (30%),
signal quality (15%), performance (10%), usability (10%), docs (10%), value (10%). Weighted totals:
**ModelAudit 8.6, fickling 8.4, picklescan 8.3, ModelScan 7.3** (out of 10). Detection, false-positive,
and performance sub-scores come straight from the artifacts above; the install, usability, docs, and
value sub-scores are my judgment calls from working with each tool.

There's no single winner, and the four aren't really interchangeable:

- **picklescan** is the fast, ubiquitous default and the quickest here by orders of magnitude — but it
  mis-parsed the broken-archive file and reported nothing, a reminder that a blocklist is only as good
  as its ability to actually open the file. Patch it to the latest release and never rely on it alone.
- **ModelScan** flagged the `eval` payload as CRITICAL every time it *opened* a file, but it silently
  skipped both the `.bin`-renamed and broken-archive files (`total_scanned=0`) — so its real weakness
  here isn't its blocklist, it's extension-based routing that lets files slip by unscanned. Solid
  center of gravity for a Protect AI shop, but confirm what it's actually scanning.
- **ModelAudit** goes the widest and deepest and caught all four — the one I'd reach for when I actually
  want to *find* things, especially with opcode-level analysis and CI-friendly SARIF output. It's the
  slowest and heaviest (≈119 MB, sub-second), which is a fine trade for a pre-production gate.
- **fickling**'s allowlist also caught all four and is the strongest posture against tricks nobody has
  enumerated yet — at the cost of a rougher install (Python 3.11 / distutils) and the usual allowlist
  risk of flagging legitimate-but-unusual imports (zero false positives on this clean set, but tune for
  yours).

For any model you didn't build yourself, the honest answer is to **layer them** — a fast blocklist
scan as a CI gate, a deeper opcode/allowlist scan before anything touches production, and a hard rule
to update relentlessly, because this category's threat model shifts every few weeks.

## Reproduce it yourself

Every number above comes from the lab run, and the whole thing is reproducible from
[the repo](https://github.com/sandhipveera/seceval-lab) at commit `[FILL]` — same malicious model file, same
evasive variants, same scanner commands. It's all benign: the payload trips a canary on an isolated
network, so nothing leaves your machine and you can safely run it and see where your results diverge.

Next episode, I put the LLM red-team frameworks head to head — Garak versus PyRIT versus Promptfoo —
and see which one actually breaks a model. Same lab, same show-the-work rules.

---

*This testing was performed entirely in an isolated, no-egress Docker network using a benign canary
payload — never a weaponized exploit. Don't build or run malicious model files against systems you
don't own, and follow responsible disclosure if you find a real vulnerability in any scanner (as
JFrog, ReversingLabs, and the "Hide and Seek" researchers did). Review each tool's license before
publishing any benchmark figures.*
