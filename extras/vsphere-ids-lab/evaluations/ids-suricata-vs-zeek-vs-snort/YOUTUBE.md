# YouTube Metadata — Episode 01

## Title (pick one; A is the recommended thumbnail-friendly default)

- **A.** I Let an AI Deploy & Attack 3 IDS Tools — Suricata vs Zeek vs Snort
- B. Suricata vs Zeek vs Snort: Same Attack, Same Box, Who Wins?
- C. 3 Intrusion Detection Systems, 1 Real Attack — Tested in an Isolated Lab
- D. Which Free IDS Actually Catches the Attack? (Suricata vs Zeek vs Snort)

## Description

```
I built one isolated lab, fired the exact same attack at the exact same target three times,
and swapped only the IDS underneath — Suricata, Zeek, and Snort. No marketing claims, just the
logs: what each one caught, what it missed, how noisy it was, and what it cost to run.

Everything is reproducible. The full lab (Terraform + Docker on vSphere), the attack scenario,
and the install scripts are on GitHub — clone it and check my numbers yourself.

🔗 Repo + reproduce it: https://github.com/<you>/seceval-lab
🧪 Targets: OWASP Juice Shop + DVWA on an isolated segment (no internet, no real LAN)
⚖️ Scored on the same 7-criterion rubric every episode

⚠️ Everything here runs in an isolated lab. Never point scanners or exploits at systems you
don't own.

⏱️ Chapters
0:00  3 IDS, 1 attack — the setup
0:25  What an IDS actually does (and who needs one)
1:10  Why Suricata, Zeek & Snort
1:50  The lab & the fairness rules
2:40  Round 1 — Install & setup (timed)
4:10  Round 2 — The attack & what each one caught
6:30  Round 3 — Noise & resource cost
7:50  Scorecard & the verdict
9:30  Reproduce it yourself + what's next

#cybersecurity #IDS #suricata #zeek #snort #blueteam #homelab #infosec #netsec #soc

Tools: Suricata, Zeek, Snort, OWASP Juice Shop, DVWA, Terraform, Docker, VMware vSphere.
Chapters generated from the scene cuts in the storyboard.
```

## Tags
cybersecurity, intrusion detection, IDS, Suricata, Zeek, Snort, blue team, SOC, network
security, homelab, infosec, IDS comparison, Suricata vs Snort, network monitoring, OWASP Juice
Shop, DVWA, Terraform, Docker, vSphere

## Thumbnail
Split-third frame: Suricata / Zeek / Snort logos over a wall of alerts, big text
"WHO SEES IT?" with a red attack arrow. Use the `title_cold_open.html` palette.

## Pinned comment
"Full lab + attack script + install scripts: https://github.com/<you>/seceval-lab — run it and
tell me if your numbers differ. Next up: vuln scanners (OpenVAS vs Nuclei vs Trivy)."
