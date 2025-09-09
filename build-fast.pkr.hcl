# Fast VM Creation - Clone from existing template instead of full installation
# This should complete in under 2 minutes

variable "vm_name" {
  type    = string
  default = "ubuntu-vm"
}

variable "cpu" {
  type    = number
  default = 2
}

variable "ram" {
  type    = number
  default = 2048
}

variable "disk_gb" {
  type    = number
  default = 20
}

variable "template_path" {
  type    = string
  default = "C:/Users/saads/OneDrive/Documents/Virtual Machines/Ubuntu 64-bit (3)/Ubuntu 64-bit (3).vmx"
}

source "vmware-vmx" "ubuntu-fast" {
  source_path       = var.template_path
  output_directory  = "createdMachines/${var.vm_name}"
  vm_name          = var.vm_name
  headless         = true
  shutdown_timeout = "2m"
  ssh_timeout      = "5m"
  shutdown_command = "echo 'ubuntu' | sudo -S shutdown -P now"

  // SSH Configuration
  ssh_username = "ubuntu"
  ssh_password = "ubuntu"
  ssh_port     = 22
  ssh_handshake_attempts = 50
  ssh_wait_timeout = "5m"

  // Fast VMX options - minimal changes for speed with data persistence
  vmx_data = {
    "numvcpus"                              = var.cpu
    "memsize"                               = var.ram
    "scsi0:0.mode"                          = "independent-persistent"
    "scsi0:0.writeThrough"                  = "TRUE"   // Ensure data persistence
    "RemoteDisplay.vnc.enabled"             = "FALSE"
    "gui.restricted"                        = "TRUE"
    "tools.syncTime"                        = "TRUE"
    "ethernet0.connectionType"              = "nat"
    "ethernet0.present"                     = "TRUE"
    "ethernet0.virtualDev"                  = "e1000e"
    // Prevent CPU halting issues
    "monitor.halt_on_panic"                 = "FALSE"
    "monitor.halt_on_triple_fault"          = "FALSE"
    "powerType.powerOff"                    = "soft"
    "powerType.powerOn"                     = "soft"
    "powerType.suspend"                     = "soft"
    "powerType.reset"                       = "soft"
  }
}

build {
  name = "ubuntu-fast"
  sources = [
    "source.vmware-vmx.ubuntu-fast"
  ]

  // Minimal provisioning for speed
  provisioner "shell" {
    inline = [
      "echo 'Fast VM clone complete - $(date)'",
      "hostname ${var.vm_name}",
      "echo '${var.vm_name}' | sudo tee /etc/hostname",
      "sync"
    ]
  }
}