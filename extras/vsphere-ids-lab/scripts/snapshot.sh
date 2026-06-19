#!/usr/bin/env bash
# Snapshot / rollback lab VMs via govc. Names a consistent baseline for reproducibility.
# Usage: snapshot.sh create <name> | snapshot.sh rollback <name>
source "$(dirname "$0")/lib/common.sh"
require govc
ACTION="${1:?create|rollback}"; NAME="${2:?snapshot name}"
PREFIX="${LAB_PREFIX:-seceval}"
for vm in "$PREFIX-controller" "$PREFIX-attack-range" "$PREFIX-targets"; do
  case "$ACTION" in
    create)   log "snapshot.create $vm -> $NAME"; govc snapshot.create -vm "$vm" "$NAME" ;;
    rollback) log "snapshot.revert $vm -> $NAME"; govc snapshot.revert -vm "$vm" "$NAME" ;;
    *) die "unknown action $ACTION" ;;
  esac
done
