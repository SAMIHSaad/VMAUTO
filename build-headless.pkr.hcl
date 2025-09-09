// Alternative Packer template for VMware Workstation - Ubuntu autoinstall (Headless mode)
// This version avoids VNC issues by using headless mode and alternative communication methods

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
  headless          = true  // Run in headless mode to avoid VNC issues
  shutdown_timeout  = "5m"
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
  ssh_wait_timeout  = "25m"

  iso_urls          = [var.iso_url]
  iso_checksum      = var.iso_checksum

  http_directory    = "http"

  boot_wait         = "10s"
  boot_command = [
    "<wait10s>",
    "<down><down><down><enter>",
    "<wait10s>",
    "c<wait5s>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ quiet splash ---<enter>",
    "initrd /casper/initrd<enter>",
    "boot<enter>"
  ]

  // Skip VNC entirely - use alternative display method
  
  // Optimized VMX options with data persistence priority
  vmx_data = {
    "scsi0:0.mode"                          = "independent-persistent"
    "scsi0:0.writeThrough"                  = "TRUE"   // Ensure data persistence (safer)
    "scsi0:0.redo"                          = ""
    "mainMem.useNamedFile"                  = "FALSE"
    "sched.mem.pshare.enable"               = "FALSE"
    "prefvmx.useRecommendedLockedMemSize"   = "TRUE"
    "MemAllowAutoScaleDown"                 = "FALSE"
    "MemTrimRate"                           = "-1"
    // Disable VNC entirely
    "RemoteDisplay.vnc.enabled"             = "FALSE"
    // Ensure VM starts without GUI dependencies
    "gui.restricted"                        = "TRUE"
    "gui.applyHostDisplayScalingToGuest"    = "FALSE"
    // Performance optimizations
    "tools.syncTime"                        = "TRUE"
    "time.synchronize.continue"             = "TRUE"
    "time.synchronize.restore"              = "TRUE"
    "time.synchronize.resume.disk"          = "TRUE"
    "time.synchronize.shrink"               = "TRUE"
    "time.synchronize.tools.startup"        = "TRUE"
    "time.synchronize.tools.enable"         = "TRUE"
    "time.synchronize.resume.host"          = "TRUE"
    // Prevent CPU halting issues
    "monitor.halt_on_panic"                 = "FALSE"
    "monitor.halt_on_triple_fault"          = "FALSE"
    "cpuid.coresPerSocket"                  = "1"
    "numa.autosize.cookie"                  = "10001"
    "numa.autosize.vcpu.maxPerVirtualNode"  = "1"
    // ACPI and power management
    "acpi.smbiosVersion2.7"                 = "FALSE"
    "powerType.powerOff"                    = "soft"
    "powerType.powerOn"                     = "soft"
    "powerType.suspend"                     = "soft"
    "powerType.reset"                       = "soft"
  }

  // Networking (adjust if needed)
  network_adapter_type = "e1000e"
}

build {
  name    = "ubuntu-autoinstall"
  sources = [
    "source.vmware-iso.ubuntu"
  ]

  // Minimal shell provisioner for faster completion
  provisioner "shell" {
    inline = [
      "echo 'VM provisioning complete'",
      "sync"
    ]
  }
}