// Minimal Packer template for Nutanix (via community plugins)
// NOTE: Nutanix plugin usage varies; treat this as a starting point.

packer {
  required_version = ">= 1.9.0"
  required_plugins {
    nutanix = {
      version = ">= 0.9.0"
      source  = "github.com/nutanix-cloud-native/nutanix" // Adjust to the correct plugin if needed
    }
  }
}

variable "vm_name" { type = string default = "nutanix-ubuntu" }
variable "cpu"     { type = number default = 2 }
variable "ram"     { type = number default = 4096 } // MiB
variable "subnet_uuid" { type = string }
variable "cluster_uuid" { type = string }
variable "image_uuid" { type = string }

source "nutanix-vm" "ubuntu" {
  name             = var.vm_name
  cluster_uuid     = var.cluster_uuid
  subnet_uuid      = var.subnet_uuid
  image_uuid       = var.image_uuid
  cpu              = var.cpu
  memory_mib       = var.ram
  communicator     = "ssh"
  ssh_username     = "ubuntu"
  ssh_password     = "ubuntu"
  ssh_timeout      = "45m"
}

build {
  name    = "nutanix-ubuntu"
  sources = ["source.nutanix-vm.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y qemu-guest-agent cloud-init"
    ]
  }
}