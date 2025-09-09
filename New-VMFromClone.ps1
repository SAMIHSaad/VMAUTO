<#
.SYNOPSIS
    Creates a new VMware Workstation virtual machine by cloning a source VM and customizing its hardware.
.DESCRIPTION
    This script automates the process of creating a full clone of a source virtual machine.
    It copies the source VM files, modifies the VMX configuration for the new VM (CPU, RAM),
    resizes the virtual disk, and then starts it with vmrun.
.PARAMETER VMName
    The name for the new virtual machine.
.PARAMETER CPU
    The number of CPU cores for the new VM.
.PARAMETER RAM
    The amount of RAM in megabytes (MB) for the new VM.
.PARAMETER DiskSize
    The new total size of the primary virtual disk in gigabytes (GB).
.PARAMETER OSType
    The operating system type: 'linux' for Ubuntu or 'windows' for Windows Server 2019.
.EXAMPLE
    .PowerShell\New-VMFromClone.ps1 -VMName "MyNewUbuntuVM" -CPU 4 -RAM 4096 -DiskSize 100 -OSType "linux"
.EXAMPLE
    .PowerShell\New-VMFromClone.ps1 -VMName "MyNewWindowsVM" -CPU 4 -RAM 4096 -DiskSize 100 -OSType "windows"
#>
param (
    [Parameter(Mandatory=$true)]
    [string]$VMName,
    [Parameter(Mandatory=$false)]
    [int]$CPU = 2,
    [Parameter(Mandatory=$false)]
    [int]$RAM = 2048,
    [Parameter(Mandatory=$false)]
    [int]$DiskSize = 20,
    [Parameter(Mandatory=$false)]
    [string]$OSType = "linux"
)

$ErrorActionPreference = 'Stop'

# --- Configuration ---
# Set source VM directory and VMX file based on OS type
if ($OSType -eq "windows") {
    $SourceVMDir = "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\Windows Server 2019"
    $SourceVMX = "Windows Server 2019.vmx"
} else {
    # Default to Linux (Ubuntu)
    $SourceVMDir = "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\Ubuntu 64-bit (3)"
    $SourceVMX = "Ubuntu 64-bit (3).vmx"
}

$DestDir = "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms"
$VMRunPath = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
# ---------------------

# Validate that the source VM directory exists
if (-not (Test-Path $SourceVMDir)) {
    Write-Error "Source VM directory not found: $SourceVMDir. Please ensure the $OSType template VM is available."
    exit 1
}

# Validate that the source VMX file exists
$SourceVMXPath = Join-Path -Path $SourceVMDir -ChildPath $SourceVMX
if (-not (Test-Path $SourceVMXPath)) {
    # For Ubuntu, try the fixed-ubuntu.vmx as fallback
    if ($OSType -eq "linux") {
        $SourceVMX = "fixed-ubuntu.vmx"
        $SourceVMXPath = Join-Path -Path $SourceVMDir -ChildPath $SourceVMX
        if (-not (Test-Path $SourceVMXPath)) {
            Write-Error "Source VMX file not found: $SourceVMXPath. Please ensure the $OSType template VM is properly configured."
            exit 1
        }
        Write-Host "Using fallback VMX file: $SourceVMX"
    } else {
        Write-Error "Source VMX file not found: $SourceVMXPath. Please ensure the $OSType template VM is properly configured."
        exit 1
    }
}

Write-Host "Using source VM: $SourceVMDir"
Write-Host "OS Type: $OSType"

$NewVMDir = Join-Path -Path $DestDir -ChildPath $VMName

if (Test-Path $NewVMDir) {
    Write-Error "A directory for '$VMName' already exists at '$NewVMDir'. Please choose a different name or remove the existing directory."
    exit 1
}

Write-Host "Creating new VM directory: $NewVMDir"
New-Item -ItemType Directory -Path $NewVMDir | Out-Null

Write-Host "Copying VM files from $SourceVMDir... (This may take a few minutes)"
Copy-Item -Path "$SourceVMDir\*" -Destination $NewVMDir -Recurse -Force

Write-Host "Configuring new VM..."

$SourceVMXFileInNewDir = Join-Path -Path $NewVMDir -ChildPath $SourceVMX
$NewVMXFile = Join-Path -Path $NewVMDir -ChildPath "$VMName.vmx"
Rename-Item -Path $SourceVMXFileInNewDir -NewName "$VMName.vmx"

# Find the primary VMDK disk file to resize (check both SCSI and NVMe)
$SourceVmdk = $null
$DiskType = $null

# Check for SCSI disk (Ubuntu)
$ScsiDisk = Get-Content -Path $NewVMXFile | Where-Object { $_ -like 'scsi0:0.fileName =*' } | Select-Object -First 1
if ($ScsiDisk) {
    $SourceVmdk = ($ScsiDisk -replace 'scsi0:0.fileName = "(.*)"', '$1')
    $DiskType = "scsi"
}

# Check for NVMe disk (Windows Server 2019)
if (-not $SourceVmdk) {
    $NvmeDisk = Get-Content -Path $NewVMXFile | Where-Object { $_ -like 'nvme0:0.fileName =*' } | Select-Object -First 1
    if ($NvmeDisk) {
        $SourceVmdk = ($NvmeDisk -replace 'nvme0:0.fileName = "(.*)"', '$1')
        $DiskType = "nvme"
    }
}

if (-not $SourceVmdk) {
    Write-Error "Could not find primary disk file in VMX configuration"
    exit 1
}

$VmdkToResize = Join-Path -Path $NewVMDir -ChildPath $SourceVmdk
Write-Host "Found $DiskType disk: $SourceVmdk"

# Modify the VMX file for CPU, RAM, and Display Name
$vmxContent = Get-Content -Path $NewVMXFile
$newVmxContent = @()

foreach ($line in $vmxContent) {
    if ($line -like 'displayName =*') {
        $newVmxContent += "displayName = `"$VMName`""
    } elseif ($line -like 'sata0:1.present =*') {
        $newVmxContent += 'sata0:1.present = "FALSE"' # Disable problematic ISO
    } elseif ($line -like 'numvcpus =*') {
        $newVmxContent += "numvcpus = `"$CPU`""
    } elseif ($line -like 'memsize =*') {
        $newVmxContent += "memsize = `"$RAM`""
    } elseif ($line -match 'scsi0:0.fileName = "(.*)"') {
        # Ensure the SCSI disk file name in the VMX is correct after potential renames
        $newVmxContent += 'scsi0:0.fileName = "' + (Split-Path -Path $VmdkToResize -Leaf) + '"'
    } elseif ($line -match 'nvme0:0.fileName = "(.*)"') {
        # Ensure the NVMe disk file name in the VMX is correct after potential renames
        $newVmxContent += 'nvme0:0.fileName = "' + (Split-Path -Path $VmdkToResize -Leaf) + '"'
    } else {
        $newVmxContent += $line
    }
}

Set-Content -Path $NewVMXFile -Value $newVmxContent

# Resize the virtual disk
if ((Test-Path $VmdkToResize) -and $DiskSize -gt 0) {
    Write-Host "Resizing disk to ${DiskSize}GB..."
    & $VMRunPath expandDisk "$VmdkToResize" $DiskSize"GB"
    Write-Host -ForegroundColor Yellow "Note: The disk has been expanded. You must extend the partition within the guest OS to use the new space."
}

Write-Host "Starting new VM '$VMName'..."

& $VMRunPath start $NewVMXFile

Write-Host -ForegroundColor Green "VM '$VMName' created and started successfully. It is now available in VMware Workstation."
