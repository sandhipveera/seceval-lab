###############################################################################
# Security Evaluation Lab — vSphere provisioning
# Provisions: controller (docker host), attack-range, targets VMs from a template.
###############################################################################

terraform {
  required_version = ">= 1.6"
  required_providers {
    vsphere = {
      source  = "hashicorp/vsphere"
      version = "~> 2.7"
    }
  }
}

provider "vsphere" {
  user                 = var.vsphere_user
  password             = var.vsphere_password
  vsphere_server       = var.vsphere_server
  allow_unverified_ssl = var.allow_unverified_ssl
}

# --- Inventory lookups -------------------------------------------------------
data "vsphere_datacenter" "dc" {
  name = var.datacenter
}

data "vsphere_datastore" "ds" {
  name          = var.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = var.cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_resource_pool" "pool" {
  name          = var.resource_pool
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "mgmt" {
  name          = var.mgmt_network
  datacenter_id = data.vsphere_datacenter.dc.id
}

# Isolated attack segment (no uplink) — see docs/SAFETY.md
data "vsphere_network" "attack" {
  name          = var.attack_network
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = var.template_name
  datacenter_id = data.vsphere_datacenter.dc.id
}

# --- VMs ---------------------------------------------------------------------
# Controller: routable mgmt NIC + attack NIC; runs the product-under-test in Docker.
module "controller" {
  source        = "./modules/lab-vm"
  name          = "${var.lab_prefix}-controller"
  resource_pool = data.vsphere_resource_pool.pool.id
  datastore     = data.vsphere_datastore.ds.id
  template      = data.vsphere_virtual_machine.template
  networks      = [data.vsphere_network.mgmt.id, data.vsphere_network.attack.id]
  num_cpus      = var.controller_cpus
  memory        = var.controller_memory
  disk_gb       = var.controller_disk_gb
  ssh_key       = var.ssh_public_key
}

# Attack range: generators / exploit tooling. Attack NIC only.
module "attack_range" {
  source        = "./modules/lab-vm"
  name          = "${var.lab_prefix}-attack-range"
  resource_pool = data.vsphere_resource_pool.pool.id
  datastore     = data.vsphere_datastore.ds.id
  template      = data.vsphere_virtual_machine.template
  networks      = [data.vsphere_network.attack.id]
  num_cpus      = var.attack_cpus
  memory        = var.attack_memory
  disk_gb       = var.attack_disk_gb
  ssh_key       = var.ssh_public_key
}

# Targets: vulnerable boxes (containers). Attack NIC only.
module "targets" {
  source        = "./modules/lab-vm"
  name          = "${var.lab_prefix}-targets"
  resource_pool = data.vsphere_resource_pool.pool.id
  datastore     = data.vsphere_datastore.ds.id
  template      = data.vsphere_virtual_machine.template
  networks      = [data.vsphere_network.attack.id]
  num_cpus      = var.targets_cpus
  memory        = var.targets_memory
  disk_gb       = var.targets_disk_gb
  ssh_key       = var.ssh_public_key
}
