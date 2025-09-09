# Ubuntu Automated Installation Configuration

This configuration provides fully automated Ubuntu 24.04 installation with the following features:

## ✅ Automated Features

### 1. **Auto-created Account**
- **Username**: `ubuntu`
- **Password**: `ubuntu`
- **Sudo access**: Enabled (passwordless)

### 2. **AZERTY Keyboard Layout**
- Automatically configured during installation
- Set system-wide for both console and X11
- No manual keyboard selection required

### 3. **Auto-select "Try or Install Ubuntu"**
- Boot command automatically selects installation option
- No manual GRUB menu interaction needed
- Proceeds directly to automated installation

### 4. **Skip Configuration Steps**
- All interactive prompts disabled
- Automatic network configuration (DHCP)
- Automatic disk partitioning (uses entire disk)
- No timezone, user creation, or package selection prompts

## 🚀 Usage

### Quick Start
```powershell
# Run the test script
.\test-ubuntu-build.ps1

# Or build directly
packer build -var="vm_name=ubuntu-automated" build.pkr.hcl
```

### Manual Build
```powershell
# Validate configuration
packer validate build.pkr.hcl

# Build with custom VM name
packer build -var="vm_name=my-ubuntu-vm" build.pkr.hcl
```

## 🔧 Configuration Files

### `build.pkr.hcl`
- Main Packer configuration
- VMware-specific settings
- Boot command for automated installation
- SSH communication settings

### `http/user-data`
- Cloud-init autoinstall configuration
- User account creation
- Keyboard layout settings
- Package installation list
- System configuration commands

### `http/meta-data`
- Cloud-init metadata (currently empty)

## 🛠️ Troubleshooting

### Boot Command Issues

If the automated boot selection doesn't work, try these alternative boot commands in `build.pkr.hcl`:

#### Option 1: Current (F6 method)
```hcl
boot_command = [
  "<wait10s>",
  "<enter><wait5s>",
  "<f6><wait5s>",
  "<esc><wait5s>",
  " autoinstall ds=nocloud-net;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---",
  "<enter>"
]
```

#### Option 2: GRUB Command Line
```hcl
boot_command = [
  "<wait10s>",
  "c<wait5s>",
  "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---<enter>",
  "initrd /casper/initrd<enter>",
  "boot<enter>"
]
```

#### Option 3: Direct Selection
```hcl
boot_command = [
  "<wait10s>",
  "<down><down><enter><wait5s>",
  "<f6><wait5s>",
  "<esc><wait5s>",
  " autoinstall ds=nocloud-net;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ ---",
  "<enter>"
]
```

### Common Issues

#### 1. **ISO Path Error**
- Update the `iso_path` variable in `build.pkr.hcl`
- Ensure the Ubuntu 24.04 ISO file exists at the specified path

#### 2. **SSH Connection Timeout**
- Check if the autoinstall completed successfully
- Verify the ubuntu user was created with correct password
- Ensure SSH server is installed and running

#### 3. **Keyboard Layout Not Applied**
- Check the `late-commands` section in `user-data`
- Verify `localectl` commands are executed properly
- May require manual verification after installation

#### 4. **VMware Tools Issues**
- The configuration installs `open-vm-tools` automatically
- If issues persist, check the provisioning section

## 📋 Installation Process

1. **Boot**: VM boots from Ubuntu ISO
2. **Auto-select**: Boot command selects "Try or Install Ubuntu"
3. **Download**: Cloud-init configuration downloaded from Packer HTTP server
4. **Install**: Automated installation begins
   - Partitions disk automatically
   - Creates ubuntu user
   - Installs packages
   - Configures AZERTY keyboard
   - Sets up SSH
5. **Provision**: Ansible playbooks run (if configured)
6. **Complete**: VM ready for use

## 🔐 Security Notes

- Default password is `ubuntu` - change in production
- SSH password authentication is enabled
- Ubuntu user has passwordless sudo access
- Consider adding SSH key authentication for production use

## 📦 Installed Packages

- `openssh-server` - SSH access
- `curl`, `wget` - Download utilities
- `vim` - Text editor
- `net-tools` - Network utilities
- `ansible` - Automation tool

## 🎯 Expected Results

After successful build:
- VM with Ubuntu 24.04 installed
- AZERTY keyboard layout configured
- SSH access with ubuntu/ubuntu credentials
- French locale (fr_FR.UTF-8)
- Ready for additional provisioning

## 📞 Support

If you encounter issues:
1. Check the Packer logs for detailed error messages
2. Verify the ISO file path and accessibility
3. Test the boot command alternatives above
4. Check VMware Workstation/Player compatibility