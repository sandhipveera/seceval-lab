# vCenter / ESXi connection
variable "vsphere_user" {
  type = string
}
variable "vsphere_password" {
  type      = string
  sensitive = true
}
variable "vsphere_server" {
  type = string
}
variable "allow_unverified_ssl" {
  type    = bool
  default = true
}

# Inventory placement
variable "datacenter" {
  type = string
}
variable "cluster" {
  type = string
}
variable "resource_pool" {
  type = string
}
variable "datastore" {
  type = string
}
variable "template_name" {
  type = string
}

# Networking
variable "mgmt_network" {
  type        = string
  description = "Routable port group for SSH/Terraform"
}
variable "attack_network" {
  type        = string
  description = "ISOLATED port group, no uplink (see SAFETY.md)"
}

# Naming + access
variable "lab_prefix" {
  type    = string
  default = "seceval"
}
variable "ssh_public_key" {
  type = string
}

# Sizing
variable "controller_cpus" {
  type    = number
  default = 4
}
variable "controller_memory" {
  type    = number
  default = 8192
}
variable "controller_disk_gb" {
  type    = number
  default = 60
}
variable "attack_cpus" {
  type    = number
  default = 2
}
variable "attack_memory" {
  type    = number
  default = 4096
}
variable "attack_disk_gb" {
  type    = number
  default = 40
}
variable "targets_cpus" {
  type    = number
  default = 2
}
variable "targets_memory" {
  type    = number
  default = 4096
}
variable "targets_disk_gb" {
  type    = number
  default = 40
}
