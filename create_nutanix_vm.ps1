# Script PowerShell pour créer une VM Nutanix CE dans VMware
param(
    [string]$VMName = "Nutanix-CE",
    [string]$ISOPath = "C:\ISOs\nutanix-ce.iso",
    [int]$RAM = 32768,  # 32 GB
    [int]$CPU = 8,
    [int]$DiskSize = 200  # 200 GB
)

Write-Host "🚀 Creating Nutanix CE VM: $VMName" -ForegroundColor Green

# Vérifier que l'ISO existe
if (-not (Test-Path $ISOPath)) {
    Write-Host "❌ ISO not found: $ISOPath" -ForegroundColor Red
    Write-Host "💡 Download Nutanix CE from: https://www.nutanix.com/products/community-edition"
    exit 1
}

# Créer la VM avec vmrun
$vmrunPath = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
$vmPath = "C:\Users\$env:USERNAME\Documents\Virtual Machines\$VMName\$VMName.vmx"

# Créer le répertoire
$vmDir = Split-Path $vmPath -Parent
New-Item -ItemType Directory -Path $vmDir -Force

# Créer le fichier VMX
$vmxContent = @"
.encoding = "windows-1252"
config.version = "8"
virtualHW.version = "19"
vmci0.present = "TRUE"
hpet0.present = "TRUE"
nvram = "$VMName.nvram"
virtualHW.productCompatibility = "hosted"
powerType.powerOff = "soft"
powerType.powerOn = "soft"
powerType.suspend = "soft"
powerType.reset = "soft"
displayName = "$VMName"
guestOS = "centos7-64"
numvcpus = "$CPU"
cpuid.coresPerSocket = "4"
memsize = "$RAM"
MemAllowAutoScaleDown = "FALSE"
MemTrimRate = "-1"

# Disque principal
scsi0.present = "TRUE"
scsi0.virtualDev = "lsilogic"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "$VMName.vmdk"
scsi0:0.deviceType = "scsi-hardDisk"

# CD-ROM avec ISO Nutanix
ide1:0.present = "TRUE"
ide1:0.deviceType = "cdrom-image"
ide1:0.fileName = "$ISOPath"
ide1:0.startConnected = "TRUE"

# Réseau
ethernet0.present = "TRUE"
ethernet0.connectionType = "nat"
ethernet0.virtualDev = "e1000"
ethernet0.wakeOnPcktRcv = "FALSE"
ethernet0.addressType = "generated"

# USB
usb.present = "TRUE"
ehci.present = "TRUE"
usb.vbluetooth.startConnected = "FALSE"

# Son
sound.present = "TRUE"
sound.fileName = "-1"
sound.autodetect = "TRUE"

# Boot
bios.bootOrder = "cdrom,hdd"
"@

# Écrire le fichier VMX
$vmxContent | Out-File -FilePath $vmPath -Encoding ASCII

Write-Host "✅ VMX file created: $vmPath" -ForegroundColor Green

# Créer le disque virtuel
Write-Host "🔧 Creating virtual disk..." -ForegroundColor Yellow
$diskPath = Join-Path $vmDir "$VMName.vmdk"
& $vmrunPath -T ws createDisk $diskPath ${DiskSize}GB

Write-Host "✅ Virtual disk created: $diskPath" -ForegroundColor Green

Write-Host "🎉 Nutanix CE VM created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Open VMware Workstation"
Write-Host "2. Open VM: $vmPath"
Write-Host "3. Start the VM"
Write-Host "4. Follow Nutanix CE installation wizard"
Write-Host "5. Default credentials: admin / nutanix/4u"
Write-Host ""
Write-Host "🌐 After installation, access via: https://[VM-IP]:9440"