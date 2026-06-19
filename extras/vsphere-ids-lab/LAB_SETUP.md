# Lab Setup (vSphere / ESXi + Terraform + Docker)

End-to-end bring-up of the evaluation lab on your local VMware vSphere/ESXi servers.

## Topology

```
                 vCenter / ESXi host
   ┌─────────────────────────────────────────────────┐
   │                                                   │
   │   PG: lab-mgmt (routable, SSH/Terraform in)       │
   │   ┌───────────────┐                               │
   │   │  controller   │  docker host: runs the        │
   │   │   (Ubuntu)    │  product-under-test containers │
   │   └──────┬────────┘                               │
   │          │                                         │
   │   PG: lab-attack (ISOLATED, no uplink)             │
   │   ┌──────┴───────┐     ┌──────────────┐            │
   │   │ attack-range │────▶│   targets    │            │
   │   │ (generators) │     │ JuiceShop... │            │
   │   └──────────────┘     └──────────────┘            │
   └─────────────────────────────────────────────────┘
```

- **lab-mgmt** port group: lets Terraform/SSH reach the controller VM.
- **lab-attack** port group: isolated vSwitch, **no uplink** — see `docs/SAFETY.md`.

## Prerequisites

On your workstation:
- `terraform` >= 1.6
- `govc` (optional, handy for snapshots/inventory)
- SSH key pair for VM access
- Network access to vCenter or the ESXi host API

On vSphere:
- A VM template (Ubuntu 22.04/24.04 cloud image with cloud-init + open-vm-tools + docker
  optionally baked in). Build it once with Packer or clone a prepared VM.
- Two port groups: `lab-mgmt` (routable) and `lab-attack` (isolated).

## Steps

```bash
# 1. Configure credentials & inventory
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
$EDITOR terraform/terraform.tfvars       # vCenter, datacenter, datastore, template, networks

# 2. Provision the lab VMs
make up                                   # terraform init + apply

# 3. Take the clean baseline snapshot (roll back to this before every eval)
make snapshot NAME=clean-baseline

# 4. Bring up shared targets (vulnerable boxes) on the isolated segment
make targets-up

# 5. Run an evaluation
make eval SLUG=ids-suricata-vs-zeek-vs-snort

# 6. Collect artifacts (metrics, screenshots, alert exports)
make capture SLUG=ids-suricata-vs-zeek-vs-snort

# 7. Reset for the next product / next episode
make rollback NAME=clean-baseline

# 8. Tear it all down
make down
```

## Where things live

| Path | Purpose |
|---|---|
| `terraform/` | vSphere VM provisioning (controller, attack-range, targets) |
| `docker/targets/` | Vulnerable target boxes as containers |
| `docker/tools/` | Per-product compose files for the product under test |
| `attack-range/` | Attack scenarios + traffic/exploit generators |
| `scripts/` | Provision, snapshot, capture, teardown helpers |
| `evaluations/<slug>/` | One folder per eval: install.sh, test.sh, README (the template), artifacts |
| `docs/` | Template, scorecard, safety, this file |

See `README.md` for the quickstart and `docs/SAFETY.md` before you run anything.
