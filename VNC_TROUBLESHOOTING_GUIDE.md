# VMware VNC Connection Error Troubleshooting Guide

## Problem Description
When creating VMs with Packer and VMware Workstation, you may encounter the error:
```
error connecting to VNC: dial tcp 127.0.0.1:5902: connectex: No connection could be made because the target machine actively refused it.
```

This error occurs because Packer cannot establish a VNC connection to the VM during the build process.

## Root Causes

1. **VMware VNC Configuration**: VMware Workstation may not be properly configured for VNC connections
2. **Windows Firewall**: Firewall may be blocking VNC ports (5900-5905)
3. **VMware Services**: Required VMware services may not be running
4. **Port Conflicts**: Another application may be using the VNC ports
5. **Permissions**: VMware may need administrator privileges

## Solutions Applied

### 1. Updated Packer Configuration
- **File**: `build.pkr.hcl`
- **Changes**:
  - Added VNC configuration parameters
  - Set VNC port range (5900-6000)
  - Disabled VNC password
  - Added VMX settings for VNC

### 2. Created Headless Alternative
- **File**: `build-headless.pkr.hcl`
- **Purpose**: Completely avoids VNC by running in headless mode
- **Benefits**: No VNC dependencies, more reliable for automated builds

### 3. Automatic Fallback
- **File**: `hypervisor_providers/vmware_provider.py`
- **Feature**: Automatically retries with headless configuration if VNC error occurs

### 4. VMware Configuration Script
- **File**: `fix_vmware_vnc.ps1`
- **Functions**:
  - Starts VMware services
  - Configures Windows Firewall (requires admin)
  - Updates VMware preferences
  - Cleans up hanging processes

## Manual Steps to Resolve

### Step 1: Run as Administrator
```powershell
# Run PowerShell as Administrator and execute:
powershell -ExecutionPolicy Bypass -File "fix_vmware_vnc.ps1"
```

### Step 2: Check VMware Services
```powershell
# Check if VMware services are running:
Get-Service -Name "*vmware*" | Select-Object Name, Status
```

### Step 3: Configure Windows Firewall (Manual)
If the script fails due to permissions:
```powershell
# Run as Administrator:
New-NetFirewallRule -DisplayName "VMware VNC Ports" -Direction Inbound -Protocol TCP -LocalPort 5900-5905 -Action Allow
```

### Step 4: Update VMware Preferences
Add these lines to `%APPDATA%\VMware\preferences.ini`:
```ini
RemoteDisplay.vnc.enabled = "TRUE"
RemoteDisplay.vnc.port = "5902"
pref.vmplayer.exit.vmAction = "poweroff"
pref.vmplayer.confirmOnExit = "FALSE"
```

### Step 5: Restart VMware Workstation
Close VMware Workstation completely and restart it as Administrator.

## Testing the Fix

### Option 1: Use Updated Configuration
The system will automatically try the headless version if VNC fails:
```bash
python vm_manager.py create "test-vm" --cpu 2 --ram 2048 --ssd 20 --os-type linux
```

### Option 2: Force Headless Mode
Manually use the headless configuration:
```bash
packer build -var "vm_name=test-vm" build-headless.pkr.hcl
```

## Prevention

### 1. Always Run as Administrator
- Run VMware Workstation as Administrator
- Run PowerShell/Command Prompt as Administrator when using Packer

### 2. Configure Windows Defender
Add VMware directories to Windows Defender exclusions:
- `C:\Program Files (x86)\VMware\`
- Your VM storage directories
- Packer cache directory

### 3. Use Headless Mode for Automation
For automated/unattended builds, prefer the headless configuration:
- More reliable
- No GUI dependencies
- Better for CI/CD pipelines

## Verification Commands

### Check VNC Ports
```powershell
# Check if ports are available:
Test-NetConnection -ComputerName "127.0.0.1" -Port 5902
```

### Check VMware Processes
```powershell
# List VMware processes:
Get-Process -Name "*vmware*"
```

### Test Packer Configuration
```bash
# Validate Packer template:
packer validate build.pkr.hcl
packer validate build-headless.pkr.hcl
```

## Additional Notes

- The headless configuration (`build-headless.pkr.hcl`) is now the recommended approach for automated VM creation
- VNC issues are common in Windows environments due to security restrictions
- Running VMware Workstation as Administrator often resolves most VNC-related issues
- The automatic fallback mechanism ensures builds continue even if VNC fails

## If Issues Persist

1. **Check VMware Logs**: Look in VMware Workstation logs for detailed error messages
2. **Disable Antivirus**: Temporarily disable antivirus to test if it's blocking connections
3. **Use Different Ports**: Modify the VNC port range in the Packer configuration
4. **Contact Support**: If all else fails, consider using a different hypervisor provider

## Success Indicators

After applying these fixes, you should see:
- ✅ VM creation completes without VNC errors
- ✅ Packer builds finish successfully
- ✅ VMs are created in the expected directories
- ✅ No "connection refused" errors in logs