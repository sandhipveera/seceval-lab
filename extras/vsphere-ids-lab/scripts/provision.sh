#!/usr/bin/env bash
# terraform init + apply for the vSphere lab.
source "$(dirname "$0")/lib/common.sh"
require terraform
cd "$REPO_ROOT/terraform"
[ -f terraform.tfvars ] || die "create terraform/terraform.tfvars from the .example first"
log "terraform init"; terraform init -input=false
log "terraform apply"; terraform apply -auto-approve
terraform output
