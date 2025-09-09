# VM Persistence Fix Guide

## Problem Summary
Linux VMs created with this automation were losing all files after poweroff or restart. This was caused by several issues in the VM creation and configuration process.

## Root Causes Identified

### 1. Packer Build Failures
- **Issue**: "unexpected EOF" errors during VM creation
- **Cause**: Incorrect boot commands and timing issues
- **Impact**: VMs not properly installed, running from live ISO

### 2. Disk Persistence Configuration
- **Issue**: VMs not configured for persistent storage
- **Cause**: Missing or incorrect VMX settings
- **Impact**: Changes lost on restart

### 3. Cloud-init Configuration Issues
- **Issue**: Suboptimal storage layout and missing persistence settings
- **Cause**: Using 'direct' layout instead of 'lvm', missing sync commands
- **Impact**: Poor disk management and data loss

### 4. Ansible Provisioning Errors
- **Issue**: Syntax errors in YAML files
- **Cause**: Malformed YAML with triple quotes
- **Impact**: Provisioning failures

## Solutions Implemented

### 1. Fixed Packer Configuration (`build.pkr.hcl`)

#### Boot Command Improvements
```hcl
boot_command = [
  "<wait10s>",
  "<down><down><down><enter>",  # Navigate to "Try or Install Ubuntu"
  "<wait10s>",
  "c<wait5s>",
  "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---",
  "<enter>",
  "initrd /casper/initrd",
  "<enter>",
  "boot",
  "<enter>"
]
```

#### Enhanced VMX Settings for Persistence
```hcl
vmx_data = {
  "scsi0:0.mode" = "independent-persistent"
  "scsi0:0.writeThrough" = "TRUE"
  "scsi0:0.redo" = ""
  "mainMem.useNamedFile" = "FALSE"
  "sched.mem.pshare.enable" = "FALSE"
  "prefvmx.useRecommendedLockedMemSize" = "TRUE"
  "MemAllowAutoScaleDown" = "FALSE"
  "MemTrimRate" = "-1"
}
```

#### Improved Shutdown Process
```hcl
shutdown_command = "echo 'ubuntu' | sudo -S sync && echo 'ubuntu' | sudo -S shutdown -P now"
ssh_timeout = "45m"
shutdown_timeout = "45m"
```

### 2. Fixed Cloud-init Configuration (`http/user-data`)

#### Better Storage Layout
```yaml
storage:
  layout:
    name: lvm          # Changed from 'direct' to 'lvm'
    match:
      size: largest
```

#### Added Persistence Commands
```yaml
runcmd:
  - sync
  - echo 'vm.swappiness=10' >> /etc/sysctl.conf
  - echo 'vm.dirty_ratio=5' >> /etc/sysctl.conf
  - echo 'vm.dirty_background_ratio=2' >> /etc/sysctl.conf
  - sysctl -p

late-commands:
  - sync
  - 'curtin in-target --target=/target -- sync'
```

### 3. Fixed Ansible Configuration (`ansible/provision_vm.yml`)

#### Corrected YAML Syntax
- Removed malformed triple quotes
- Fixed indentation issues
- Ensured proper YAML structure

#### Enhanced Persistence Features
- Periodic disk sync service
- Improved kernel writeback settings
- Shutdown sync hooks
- Persistent journald storage

### 4. Created Test Script (`test_vm_build.ps1`)

A comprehensive testing script that:
- Checks prerequisites
- Builds VMs with proper logging
- Validates persistence settings
- Provides detailed feedback

## Usage Instructions

### 1. Test the Fixed Configuration
```powershell
# Run the test script to verify everything works
.\test_vm_build.ps1 -VmName "test-persistence" -Verbose
```

### 2. Build a Production VM
```powershell
# Build with specific name
packer build -var "vm_name=my-persistent-vm" build.pkr.hcl
```

### 3. Verify VM Persistence
After the VM is created and running:

1. **Create test files**:
   ```bash
   echo "This should persist" > /home/ubuntu/test.txt
   sudo echo "System file test" > /etc/test-persistence
   ```

2. **Shutdown the VM**:
   ```bash
   sudo shutdown -h now
   ```

3. **Restart the VM** and verify files exist:
   ```bash
   cat /home/ubuntu/test.txt
   sudo cat /etc/test-persistence
   ```

## Key Configuration Changes Summary

| Component | Change | Purpose |
|-----------|--------|---------|
| **Packer Boot** | Added navigation commands | Properly select Ubuntu installation |
| **VMX Settings** | Added persistence flags | Ensure disk writes are permanent |
| **Cloud-init** | Changed to LVM layout | Better disk management |
| **Cloud-init** | Added sync commands | Force disk writes |
| **Ansible** | Fixed YAML syntax | Enable proper provisioning |
| **Timeouts** | Increased to 45 minutes | Allow for complete installation |
| **Shutdown** | Added sync before shutdown | Ensure all data is written |

## Troubleshooting

### If VMs Still Lose Data

1. **Check VMX file** in `permanent_vms/[vm-name]/`:
   ```
   scsi0:0.mode = "independent-persistent"
   scsi0:0.writeThrough = "TRUE"
   ide0:0.present = "FALSE"
   ```

2. **Verify disk usage** inside VM:
   ```bash
   df -h
   lsblk
   mount | grep -v tmpfs
   ```

3. **Check if running from ISO**:
   ```bash
   mount | grep iso9660
   # Should return nothing if properly installed
   ```

### Common Issues

- **"unexpected EOF"**: Usually timing issues, increase wait times
- **SSH timeout**: VM taking too long to boot, check ISO and hardware settings
- **Files still lost**: Check VMX settings and ensure VM isn't running from live ISO

## Verification Checklist

- [ ] Packer build completes without errors
- [ ] VM boots from disk (not ISO)
- [ ] VMX file has correct persistence settings
- [ ] Test files survive reboot
- [ ] System logs are persistent
- [ ] Network configuration survives reboot

## Next Steps

1. Test with your specific workloads
2. Create snapshots after initial setup
3. Monitor disk usage and performance
4. Consider automated backup solutions

This fix addresses the core persistence issues and should ensure that your Linux VMs maintain all data and configurations across reboots and power cycles.