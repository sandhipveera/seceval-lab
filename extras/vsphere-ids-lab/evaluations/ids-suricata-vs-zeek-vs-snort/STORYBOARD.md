# Episode 01 — Storyboard
## "I let an AI deploy & attack 3 IDS tools — Suricata vs Zeek vs Snort"

This is the single source of truth for both the **blog post** and the **video**. The narration
blocks below are the exact text fed to ElevenLabs (`video/script.yaml`), and the on-screen
actions map to the Playwright/terminal recordings. Keep blog and video in lockstep so one
production pass yields both.

- **Target length:** 9–11 min video / ~1,800-word blog
- **Tone:** practical, lab-coat-meets-creator. Show the work; let the evidence talk.
- **Through-line:** same target box, same attack, same snapshot — only the IDS changes.

---

## Blog outline (maps 1:1 to video scenes)

1. The job an IDS does, and who should care (home lab → SMB)
2. Why these three (Suricata, Zeek, Snort) — market position, all open source
3. The lab: one isolated segment, Juice Shop + DVWA targets, the `web-recon-v1` attack
4. Round 1 — Install & setup (time + friction for each)
5. Round 2 — Detection (same attack, normalized alert CSV: TP / FP / misses)
6. Round 3 — Signal quality & resource cost (metrics.csv)
7. Scorecard (fixed rubric) + the verdict: pick A if… / B if… / C if…
8. Reproduce it yourself (repo + commit hash)

---

## Video script & shot list

> Each scene = one narration block + one on-screen action. Durations are targets; the real
> timing comes from the generated voiceover (the assembler pads video to match audio).

### Scene 1 — Cold open (0:00–0:25)
**On screen:** Fast montage — `terraform apply` scrolling, three IDS dashboards lighting up,
a wall of alerts. Title card: *"3 IDS. 1 attack. Same box. Who sees it?"*
**Narration:**
> "An intrusion detection system has one job: notice when something on your network is wrong.
> So I built an isolated lab, pointed the exact same attack at the exact same target three
> times, and swapped only the IDS underneath. Suricata. Zeek. Snort. Here's what each one
> actually saw — no marketing, just the logs."

### Scene 2 — The job to be done (0:25–1:10)
**On screen:** Simple animated diagram (the topology from `docs/LAB_SETUP.md`): controller,
isolated attack segment, targets. Highlight the IDS sitting on the wire.
**Narration:**
> "Quick framing. An IDS sits on your network and inspects traffic for known-bad patterns or
> weird behavior. It doesn't block — it tells you. If you run a home lab, a small business, or
> you're studying for a blue-team role, this is the tool that turns 'I think something's off'
> into an actual alert you can act on. The question is never just 'does it work' — it's 'what
> does it miss, how noisy is it, and what does it cost you to run.'"

### Scene 3 — Why these three (1:10–1:50)
**On screen:** Three logo cards with one-line positioning each. Subtle "open source · free"
stamp on all three.
**Narration:**
> "I picked Suricata, Zeek, and Snort because they're the three you'll actually run into.
> Snort is the original, signature-based and battle-tested. Suricata is the modern multi-
> threaded successor with a rich event format. Zeek isn't really a signature engine at all —
> it's a network analysis framework that describes everything it sees. Same category, three
> very different philosophies. All free, all open source, so you can follow along."

### Scene 4 — The lab & the rules (1:50–2:40)
**On screen:** Terminal: `make up`, then `make targets-up`, then a quick pan over
`docs/SAFETY.md` highlighting "isolated segment, no uplink."
**Narration:**
> "Here's the setup, and it matters for fairness. One vSphere host. An isolated network with
> no path to the internet or my real LAN — everything stays in the lab. Two deliberately
> vulnerable targets: OWASP Juice Shop and DVWA. And one fixed attack script — recon, a
> directory brute-force, then a batch of web exploits. Every IDS gets the same clean VM
> snapshot, the same target, the same attack. The only variable is the tool."

### Scene 5 — Round 1: Install (2:40–4:10)
**On screen:** Split-screen sped-up terminal of all three `install.sh` runs; a timer chip
ticks in the corner for each. End on a small "setup time" bar chart.
**Narration:**
> "Round one — just getting each one running, fully scripted, timed with a stopwatch.
> Suricata came up from a single compose file in a few minutes, but out of the box it's quiet
> until you load rule sets. Snort took the most fiddling — the config is powerful and also
> from another era. Zeek installed fast but 'configuring' it means thinking in its scripting
> language, which is a different mental model entirely. Numbers are on screen; full commands
> are in the repo."

### Scene 6 — Round 2: The attack & detection (4:10–6:30)
**On screen:** Left pane: `make eval` firing `web-recon-v1` (nmap → ffuf → nuclei). Right pane:
each IDS dashboard (EveBox for Suricata, Zeek `notice.log` tailing, Snort alerts) lighting up
in turn. Then cut to the **normalized alert table** (TP / FP / miss per product).
**Narration:**
> "Now the fun part. I fire the identical attack and watch what each one catches. Suricata
> lit up immediately on the scan and the web exploits — clean, structured events I could
> export straight to a table. Snort caught the signature-based hits but stayed silent on a
> couple of things outside its rule set. Zeek didn't 'alert' in the classic sense — it
> quietly logged the entire conversation, which is incredible for forensics but means you do
> more work to turn it into 'something is wrong right now.' I normalized everything into one
> CSV so it's apples to apples — here's the tally."

### Scene 7 — Round 3: Noise & cost (6:30–7:50)
**On screen:** The false-positive column highlighted; then `metrics.csv` rendered as CPU/RAM
bars per product under load.
**Narration:**
> "Detection is only half the story. An IDS that screams at everything is one you'll learn to
> ignore. Untuned, Suricata's broad rule sets generated the most noise; Snort was tighter out
> of the box; Zeek barely 'false-positives' because it isn't trying to. And resource cost —
> here's CPU and memory under the same load. Suricata's multithreading earns its keep on
> busier links; Snort stayed lean; Zeek's cost scales with how much you ask its scripts to do."

### Scene 8 — Scorecard & verdict (7:50–9:30)
**On screen:** The seven-criterion scorecard from `docs/SCORECARD.md` filling in, weighted
totals animating. Then three "Pick X if…" cards.
**Narration:**
> "Scored on the same rubric every episode — install, detection, signal quality, performance,
> usability, docs, and value. There's no single winner, and anyone who tells you otherwise is
> selling something. Pick Suricata if you want modern, exportable alerts and you're willing to
> tune. Pick Snort if you want a proven signature engine and tight defaults. Pick Zeek if your
> real goal is deep network visibility and forensics, not just alerts. Honestly, a lot of
> serious setups run Suricata or Snort for alerting and Zeek alongside for context."

### Scene 9 — Reproduce it / outro (9:30–10:30)
**On screen:** The GitHub repo, the commit hash, `make new-eval`. End card with the next
episode teaser (vuln scanners) and subscribe prompt.
**Narration:**
> "Everything here is reproducible — same repo, pinned versions, the exact attack script,
> down to the commit hash on screen. Clone it, run it, and tell me if your numbers differ;
> that's the whole point. Next episode I turn the same lab loose on vulnerability scanners —
> OpenVAS versus Nuclei versus Trivy. If you want to see how that shakes out, subscribe, and
> I'll see you in the lab."

---

## Production notes

- **Voiceover:** narration blocks above are mirrored verbatim in `video/script.yaml`; ElevenLabs
  renders one MP3 per scene using your voice ID.
- **Screen capture:** web dashboards via Playwright (`video/record/record_scenes.js`); terminal
  scenes via asciinema → mp4 (`video/record/record_terminal.sh`).
- **Assembly:** `video/assemble/build_video.sh` pads each clip to its narration length, burns
  captions, and concatenates with intro/outro.
- **B-roll to capture during the real run:** the `terraform apply`, each dashboard's "first
  alert" moment, and the metrics graphs — grab these live so the visuals are real, not faked.
