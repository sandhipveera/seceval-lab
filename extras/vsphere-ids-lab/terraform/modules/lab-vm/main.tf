resource "vsphere_virtual_machine" "vm" {
  name             = var.name
  resource_pool_id = var.resource_pool
  datastore_id     = var.datastore
  num_cpus         = var.num_cpus
  memory           = var.memory
  guest_id         = var.template.guest_id
  scsi_type        = var.template.scsi_type

  dynamic "network_interface" {
    for_each = var.networks
    content {
      network_id   = network_interface.value
      adapter_type = var.template.network_interface_types[0]
    }
  }

  disk {
    label            = "disk0"
    size             = var.disk_gb
    thin_provisioned = true
  }

  clone {
    template_uuid = var.template.id
    customize {
      linux_options {
        host_name = var.name
        domain    = "lab.local"
      }
      # Mgmt NIC uses DHCP; isolated NICs get static lab addressing post-boot.
      network_interface {}
    }
  }

  # Push SSH key + bootstrap docker via cloud-init / guest customization extra config
  extra_config = {
    "guestinfo.ssh_authorized_key" = var.ssh_key
  }
}
