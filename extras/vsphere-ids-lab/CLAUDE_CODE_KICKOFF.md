# Claude Code Kickoff Prompt

Paste the block below into Claude Code from the root of an empty repo (or this scaffold) to
build out the full lab. It's written to be self-contained: it states the goal, the
environment, the constraints, and the exact deliverables, and it tells Claude Code to plan
and confirm before touching your vSphere servers.

> Tip: run it in a fresh git repo. Keep `docs/SAFETY.md` authoritative — if any instruction
> ever conflicts with safety/containment, safety wins.

---

## The prompt

```
You are setting up and operating a reproducible SECURITY PRODUCT EVALUATION LAB for me. The
lab's purpose is to deploy security products, test them against a fixed attack range, capture
evidence, and produce fair head-to-head comparisons that I'll publish as blog posts and
YouTube videos. Reproducibility and safety are the two non-negotiables.

ENVIRONMENT (mine, on-prem):
- Local VMware vSphere/ESXi servers managed via vCenter. I have admin API access.
- Provisioning tool: Terraform (hashicorp/vsphere provider). VM lifecycle = Terraform.
- Security tools + vulnerable targets run as Docker containers inside lab VMs.
- I run Claude Code from my workstation, which can reach vCenter and the lab VMs over SSH.
- There is a routable `lab-mgmt` port group and an ISOLATED `lab-attack` port group that has
  NO uplink to my LAN or the internet. All attack traffic stays on lab-attack.

HARD CONSTRAINTS (do not violate, ever):
1. Containment: never run a scan, exploit, or traffic generator against anything except the
   defined target boxes on the isolated lab-attack segment. Never add an uplink to lab-attack
   or route attack traffic to my real network/internet. If a tool "needs" internet, stop and
   ask me; do not weaken isolation.
2. Everything scripted: no manual install steps. If it isn't in a script, it didn't happen.
3. Reproducible by commit: every evaluation must record the repo git hash, exact tool/image
   versions (pinned tags + digests, never bare `latest`), and the exact attack scenario used.
4. Fair tests: in a head-to-head, every product faces the SAME target box and SAME scenario
   from the SAME clean VM snapshot.
5. Evidence over opinion: every score/claim must trace to a captured artifact (metrics CSV,
   alert export, screenshot). No eyeballing.
6. Secrets never committed: terraform.tfvars, state files, keys are gitignored.
7. Before any `terraform apply`, `terraform destroy`, or running attack tooling, show me the
   plan and WAIT for my explicit confirmation.

WHAT TO BUILD (deliverables):
A) Repo scaffold:
   - terraform/ : vSphere provider + a reusable lab-vm module. Provision three VMs from an
     Ubuntu cloud-init template: `controller` (docker host for products-under-test; mgmt +
     attack NICs), `attack-range` (generators; attack NIC only), `targets` (vulnerable boxes;
     attack NIC only). Variables for vCenter/datacenter/cluster/datastore/template/networks
     and per-VM sizing. Provide terraform.tfvars.example.
   - docker/targets/ : compose for vulnerable boxes (OWASP Juice Shop, DVWA, a
     Metasploitable-style services box) on an isolated bridge.
   - docker/tools/ : per-product compose files for the product under test (start with one
     example, e.g. Suricata + a log viewer).
   - attack-range/ : declarative YAML scenarios + a generator (`run_attack.sh`) that parses a
     scenario and runs each step (nmap/ffuf/nuclei/etc.) inside the attack-range container,
     writing logs tagged by run id. Implement the YAML step executor (the scaffold has a stub).
   - scripts/ : provision.sh, snapshot.sh (govc create/rollback), teardown.sh, and
     capture/ (capture_metrics.sh = docker stats -> CSV; capture_screenshots.sh = headless
     chromium; collect_artifacts.sh = bundle per eval).
   - evaluations/_TEMPLATE/ : eval.yaml, install.sh, test.sh, and README copied from
     docs/EVALUATION_TEMPLATE.md.
   - docs/ : EVALUATION_TEMPLATE.md, SCORECARD.md (fixed rubric), SAFETY.md (containment),
     LAB_SETUP.md.
   - Makefile with: up, down, snapshot, rollback, targets-up, targets-down, new-eval, eval,
     capture, help.
   - README.md (quickstart) and CLAUDE.md (operating guide / prime directives).

B) Make the pipeline actually runnable end to end for ONE example evaluation
   (IDS: Suricata vs Zeek vs Snort) so I can see it work:
   - install.sh deploys all three IDS as containers on the controller, sniffing the attack
     interface; record wall-clock install time for each.
   - test.sh: start metric capture, fire the `web-recon-v1` scenario from attack-range against
     the Juice Shop / DVWA targets, then export each IDS's alerts (eve.json / Zeek logs /
     Snort unified2) into artifacts/<run_id>/.
   - A small parser that normalizes each product's alerts into a common CSV
     (timestamp, product, signature, severity, src, dst) so I can compare true/false positives.
   - Fill the Results table + Scorecard in the eval README from the captured artifacts.

C) Verification (do this before telling me it's done):
   - Re-run install.sh + test.sh from a fresh snapshot; confirm idempotent and exit 0.
   - Confirm artifacts/<run>/metrics.csv and per-product alert exports exist and are non-empty.
   - Spot-check that at least two numbers in the README match the artifacts.
   - Run the scenario twice; confirm results are stable within stated variance.
   - Confirm the SAFETY.md pre-flight checklist passes (isolated segment, fresh snapshot,
     targets are the only destinations).

HOW TO PROCEED:
1. First, read docs/SAFETY.md and CLAUDE.md if present. Then propose a short PLAN of the file
   tree and the order you'll build in. Wait for my OK.
2. Build the scaffold and commit in logical chunks with clear messages.
3. For anything that touches vSphere or runs attack tooling, show the command/plan and wait
   for my confirmation before executing.
4. When the example IDS evaluation runs clean and verification passes, summarize: what was
   built, how to run a new eval (`make new-eval SLUG=...`), and what I need to provide
   (vCenter creds, template name, port group names, SSH key).

Ask me for the vCenter/template/network details when you reach the point of needing them —
don't invent them. Start by proposing the plan.
```

---

## After it runs

Things you'll need to hand Claude Code when it asks:

- vCenter server + credentials (it will put them in `terraform.tfvars`, which is gitignored)
- Datacenter / cluster / resource pool / datastore names
- The Ubuntu cloud-init **template name** on your vSphere (build one with Packer if you don't
  have it — ask Claude Code to generate a Packer template too)
- Port group names for `lab-mgmt` (routable) and `lab-attack` (isolated)
- Your SSH public key

## Follow-on prompts (reuse the series)

- "Scaffold a new evaluation: `make new-eval SLUG=vuln-openvas-vs-nuclei-vs-trivy`, then build
  install/test for scanning the target boxes and normalize findings to a common CSV."
- "From `evaluations/<slug>/artifacts/<run>`, draft the blog post and a 8–10 minute video
  script using the filled template, with a cold open on 'the job to be done'."
- "Generate a Packer template for the Ubuntu 22.04 cloud-init base image this lab expects."
```
