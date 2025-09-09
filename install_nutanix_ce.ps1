# Script d'installation automatique Nutanix CE
param(
    [string]$ISOPath = "",
    [string]$VMName = "Nutanix-CE-Lab",
    [int]$RAM = 32768,  # 32 GB minimum
    [int]$CPU = 8,      # 8 cores recommandés
    [int]$DiskSize = 250 # 250 GB
)

Write-Host "🚀 INSTALLATION NUTANIX COMMUNITY EDITION" -ForegroundColor Green
Write-Host "=" * 60

# Vérifier les prérequis
Write-Host "🔍 Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier VMware Workstation
$vmrunPath = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
if (-not (Test-Path $vmrunPath)) {
    Write-Host "❌ VMware Workstation non trouvé!" -ForegroundColor Red
    Write-Host "💡 Installez VMware Workstation Pro" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ VMware Workstation trouvé" -ForegroundColor Green

# Vérifier l'ISO
if ($ISOPath -eq "" -or -not (Test-Path $ISOPath)) {
    Write-Host "❌ ISO Nutanix CE non spécifié ou introuvable!" -ForegroundColor Red
    Write-Host "💡 Téléchargez depuis: https://www.nutanix.com/products/community-edition" -ForegroundColor Yellow
    Write-Host "📝 Utilisation: .\install_nutanix_ce.ps1 -ISOPath 'C:\Path\To\nutanix-ce.iso'" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ ISO Nutanix CE trouvé: $ISOPath" -ForegroundColor Green

# Vérifier la RAM système
$totalRAM = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum).sum / 1GB
Write-Host "💾 RAM système: ${totalRAM} GB" -ForegroundColor Cyan
if ($totalRAM -lt 48) {
    Write-Host "⚠️ Attention: RAM système faible pour Nutanix CE" -ForegroundColor Yellow
    Write-Host "   Recommandé: 64 GB+ (48 GB minimum)" -ForegroundColor Yellow
}

# Créer la VM
Write-Host "`n🔧 Création de la VM Nutanix CE..." -ForegroundColor Yellow

$vmDir = "C:\Users\$env:USERNAME\Documents\Virtual Machines\$VMName"
$vmPath = "$vmDir\$VMName.vmx"

# Créer le répertoire
New-Item -ItemType Directory -Path $vmDir -Force | Out-Null

# Configuration VMX optimisée pour Nutanix
$vmxContent = @"
.encoding = "windows-1252"
config.version = "8"
virtualHW.version = "19"
vmci0.present = "TRUE"
hpet0.present = "TRUE"
nvram = "$VMName.nvram"
displayName = "$VMName"
guestOS = "centos7-64"

# CPU Configuration
numvcpus = "$CPU"
cpuid.coresPerSocket = "4"
vcpu.hotadd = "TRUE"

# Memory Configuration  
memsize = "$RAM"
mem.hotadd = "TRUE"
MemAllowAutoScaleDown = "FALSE"
MemTrimRate = "-1"

# Disk Configuration
scsi0.present = "TRUE"
scsi0.virtualDev = "lsilogic"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "$VMName.vmdk"
scsi0:0.deviceType = "scsi-hardDisk"

# Second disk for Nutanix storage
scsi0:1.present = "TRUE"
scsi0:1.fileName = "${VMName}_storage.vmdk"
scsi0:1.deviceType = "scsi-hardDisk"

# CD-ROM with Nutanix ISO
ide1:0.present = "TRUE"
ide1:0.deviceType = "cdrom-image"
ide1:0.fileName = "$ISOPath"
ide1:0.startConnected = "TRUE"

# Network Configuration
ethernet0.present = "TRUE"
ethernet0.connectionType = "bridged"
ethernet0.virtualDev = "e1000"
ethernet0.wakeOnPcktRcv = "FALSE"
ethernet0.addressType = "generated"

# USB and Sound
usb.present = "TRUE"
ehci.present = "TRUE"
sound.present = "TRUE"
sound.fileName = "-1"
sound.autodetect = "TRUE"

# Boot Configuration
bios.bootOrder = "cdrom,hdd"
bios.hddOrder = "scsi0:0"

# Performance Optimizations
mainMem.useNamedFile = "FALSE"
sched.mem.pshare.enable = "FALSE"
prefvmx.useRecommendedLockedMemSize = "TRUE"
"@

# Écrire le fichier VMX
$vmxContent | Out-File -FilePath $vmPath -Encoding ASCII
Write-Host "✅ Fichier VMX créé: $vmPath" -ForegroundColor Green

# Créer les disques virtuels
Write-Host "💽 Création des disques virtuels..." -ForegroundColor Yellow

# Disque principal (OS)
$mainDisk = "$vmDir\$VMName.vmdk"
& $vmrunPath -T ws createDisk $mainDisk ${DiskSize}GB
Write-Host "✅ Disque principal créé: ${DiskSize} GB" -ForegroundColor Green

# Disque de stockage (pour Nutanix)
$storageDisk = "$vmDir\${VMName}_storage.vmdk"
& $vmrunPath -T ws createDisk $storageDisk 500GB
Write-Host "✅ Disque de stockage créé: 500 GB" -ForegroundColor Green

# Instructions d'installation
Write-Host "`n🎉 VM Nutanix CE créée avec succès!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📋 ÉTAPES SUIVANTES:" -ForegroundColor Cyan
Write-Host "1. Ouvrir VMware Workstation" -ForegroundColor White
Write-Host "2. Ouvrir la VM: $vmPath" -ForegroundColor White
Write-Host "3. Démarrer la VM" -ForegroundColor White
Write-Host "4. Suivre l'assistant d'installation Nutanix CE" -ForegroundColor White
Write-Host "5. Configurer le réseau (IP statique recommandée)" -ForegroundColor White
Write-Host "6. Attendre la fin de l'installation (30-60 minutes)" -ForegroundColor White

Write-Host "`n🌐 APRÈS INSTALLATION:" -ForegroundColor Cyan
Write-Host "• Interface web: https://[IP-VM]:9440" -ForegroundColor White
Write-Host "• Credentials par défaut: admin / nutanix/4u" -ForegroundColor White
Write-Host "• Configurer dans notre système:" -ForegroundColor White
Write-Host "  - Ouvrir http://localhost:5000" -ForegroundColor White
Write-Host "  - Aller dans Settings > Nutanix" -ForegroundColor White
Write-Host "  - Entrer l'IP et les credentials" -ForegroundColor White

Write-Host "`n⚡ CONFIGURATION RECOMMANDÉE:" -ForegroundColor Cyan
Write-Host "• Réseau: Bridged (pour accès direct)" -ForegroundColor White
Write-Host "• IP: Statique (évite les changements)" -ForegroundColor White
Write-Host "• DNS: 8.8.8.8, 8.8.4.4" -ForegroundColor White

Write-Host "`n🔧 SPÉCIFICATIONS VM:" -ForegroundColor Cyan
Write-Host "• CPU: $CPU cores" -ForegroundColor White
Write-Host "• RAM: $RAM MB" -ForegroundColor White
Write-Host "• Disque OS: ${DiskSize} GB" -ForegroundColor White
Write-Host "• Disque Storage: 500 GB" -ForegroundColor White
Write-Host "• Réseau: Bridged" -ForegroundColor White

Write-Host "`n✨ Prêt pour l'installation!" -ForegroundColor Green