# Permanent VM Creation Guide

This guide explains how to create permanent virtual machines using the updated workflow.

## Prerequisites

- VMware Workstation installed.
- Packer installed.
- Ansible installed.

## Workflow

The process of creating a permanent VM is now fully automated. When you run the Packer build, the following steps are executed:

1. **Temporary VM Creation:** Packer creates a temporary virtual machine based on the configuration in the `.pkr.hcl` files.

2. **Provisioning:** Ansible is used to provision the temporary VM.

3. **Permanent VM Creation:** A post-processor script (`register_permanent_vm.ps1`) is executed. This script performs the following actions:
    - Copies the VM files from the temporary output directory to the `permanent_vms` directory.
    - Registers the VM with VMware Workstation.

## How to Use

1. **Run the Packer build:**

   ```bash
   packer build build.pkr.hcl
   ```

2. **Find your permanent VM:**

   Once the build is complete, you will find your permanent VM in the `permanent_vms` directory. It will also be registered in VMware Workstation, so you can open it directly from the VMware library.
