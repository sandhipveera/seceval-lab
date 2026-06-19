# Safety, Containment & Legal Guardrails

Read this before running anything. Attack tooling that escapes the lab can damage real
systems and create legal liability. These rules are non-negotiable for this project.

## Network containment

- **Isolated lab network only.** All target boxes and attack generators live on a dedicated
  vSphere port group / VLAN with **no route to your home/corp LAN or the internet** (except a
  tightly controlled update path, ideally via a snapshot taken *before* tooling is installed).
- Use an **isolated vSwitch** or a port group with no uplink for the "hot" attack segment.
- Never point a scanner, exploit, or traffic generator at any IP you do not own. The attack
  range targets are the *only* legitimate destinations.
- Egress-filter the lab: default-deny outbound. If a tool needs to phone home for licensing,
  whitelist that single endpoint explicitly and note it in the eval.

## VM hygiene

- Every test starts from a **clean snapshot** (`scripts/snapshot.sh`) and rolls back after.
- Treat all lab VMs as disposable and untrusted. Don't reuse credentials from real systems.
- Don't store real secrets, customer data, or production configs anywhere in the lab.

## Legal / licensing

- **Verify each product's license before publishing benchmarks.** Some commercial EULAs
  restrict publishing performance comparisons ("benchmark clauses"). Record the license and
  any restrictions in the eval front matter.
- Only test software you are licensed to run. For paid tools, use official trial/community
  tiers and stay within their terms.
- Vulnerable target images (Juice Shop, DVWA, Metasploitable) are intentionally insecure —
  never expose them to any untrusted network.

## Disclosure in your content

- State clearly that all testing happens in an isolated lab and that viewers must not run the
  attacks against systems they don't own.
- If you find a real 0-day in a product during testing, follow responsible disclosure — notify
  the vendor before publishing.

## Pre-flight checklist (confirm every run)

- [ ] Attack segment has no uplink to LAN/internet
- [ ] Working from a fresh snapshot
- [ ] Targets are the only scan/exploit destinations
- [ ] Product license reviewed; benchmark clause checked
- [ ] No real secrets/data present in lab
