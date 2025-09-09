// Minimal Packer template for VMware Workstation - Ubuntu autoinstall
// Adjust iso_url, iso_checksum, and network/provisioning details as needed.

packer {
  required_version = ">= 1.9.0"
  required_plugins {
    vmware = {
      version = ">= 1.1.2"
      source  = "github.com/hashicorp/vmware"
    }
  }
}

variable "vm_name" {
  type    = string
  default = "ubuntu-autoinstall"
}

variable "cpu" {
  type    = number
  default = 2
}

variable "ram" {
  type    = number
  default = 4096
}

variable "disk_gb" {
  type    = number
  default = 40
}

variable "iso_url" {
  type    = string
  default = "file://C:/Users/saads/OneDrive/Documents/Coding/demo-automation/templates/ubuntu-24.04.2-desktop-amd64.iso"
}

variable "iso_checksum" {
  type    = string
  default = "sha256:D7FE3D6A0419667D2F8EFF12796996328DAA2D4F90CD9F87AA9371B362F987BF"
}

source "vmware-iso" "ubuntu" {
  output_directory  = "createdMachines/${var.vm_name}"
  vm_name           = var.vm_name
  headless          = false
  shutdown_timeout  = "10m"
  ssh_timeout       = "25m"
  shutdown_command  = "echo 'ubuntu' | sudo -S shutdown -P now"

  // Hardware
  cpus              = var.cpu
  memory            = var.ram
  disk_size         = var.disk_gb * 1024 // MB

  communicator      = "ssh"
  ssh_username      = "ubuntu"
  ssh_password      = "ubuntu"
  ssh_port          = 22
  ssh_handshake_attempts = 100
  ssh_wait_timeout  = "15m"

  iso_urls          = [var.iso_url]
  iso_checksum      = var.iso_checksum

  http_directory    = "http"

  boot_wait         = "10s"
  boot_command = [
    "<wait10s>",
    "<down><down><down><enter>",
    "<wait10s>",
    "c<wait5s>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---<enter>",
    "initrd /casper/initrd<enter>",
    "boot<enter>"
  ]

  // VNC Configuration - Fix for VNC connection issues
  vnc_disable_password = true
  vnc_bind_address     = "127.0.0.1"
  vnc_port_min         = 5900
  vnc_port_max         = 6000

  // Persistence-related VMX options
  vmx_data = {
    "scsi0:0.mode"                          = "independent-persistent"
    "scsi0:0.writeThrough"                  = "TRUE"
    "scsi0:0.redo"                          = ""
    "mainMem.useNamedFile"                  = "FALSE"
    "sched.mem.pshare.enable"               = "FALSE"
    "prefvmx.useRecommendedLockedMemSize"   = "TRUE"
    "MemAllowAutoScaleDown"                 = "FALSE"
    "MemTrimRate"                           = "-1"
    // VNC-related VMX settings
    "RemoteDisplay.vnc.enabled"             = "TRUE"
    "RemoteDisplay.vnc.port"                = "5902"
    "RemoteDisplay.vnc.key"                 = "vmware"
  }

  // Networking (adjust if needed)
  network_adapter_type = "e1000e"
}

build {
  name    = "ubuntu-autoinstall"
  sources = [
    "source.vmware-iso.ubuntu"
  ]

  // Basic shell provisioner (optional)
  provisioner "shell" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y qemu-guest-agent cloud-init",
      "sudo systemctl enable qemu-guest-agent || true",
      "sync"
    ]
  }
}