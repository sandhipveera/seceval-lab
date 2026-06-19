#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
require terraform
cd "$REPO_ROOT/terraform"
warn "destroying lab VMs"; terraform destroy -auto-approve
