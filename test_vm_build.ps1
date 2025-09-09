#!/usr/bin/env powershell

# Test VM Build Script
# This script tests the VM creation process and verifies persistence

param(
    [string]$VmName = "test-ubuntu-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    [switch]$SkipBuild,
    [switch]$Verbose
)

function Log-Message {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-Prerequisites {
    Log-Message "Checking prerequisites..."
    
    # Check if Packer is installed
    try {
        $packerVersion = & packer version 2>$null
        Log-Message "Packer found: $packerVersion"
    } catch {
        Log-Message "ERROR: Packer not found. Please install Packer." "ERROR"
        return $false
    }
    
    # Check if VMware Workstation is installed
    $vmwarePath = "C:\Program Files (x86)\VMware\VMware Workstation\vmware.exe"
    if (-not (Test-Path $vmwarePath)) {
        Log-Message "ERROR: VMware Workstation not found at $vmwarePath" "ERROR"
        return $false
    }
    Log-Message "VMware Workstation found"
    
    # Check if ISO exists
    $isoPath = "C:/Users/saads/OneDrive/Documents/Coding/demo-automation/templates/ubuntu-24.04.2-desktop-amd64.iso"
    if (-not (Test-Path $isoPath)) {
        Log-Message "ERROR: Ubuntu ISO not found at $isoPath" "ERROR"
        return $false
    }
    Log-Message "Ubuntu ISO found"
    
    return $true
}

function Build-VM {
    param([string]$Name)
    
    Log-Message "Starting VM build: $Name"
    
    # Clean up any previous build artifacts
    $outputDir = "output-$Name"
    if (Test-Path $outputDir) {
        Log-Message "Cleaning up previous build artifacts..."
        Remove-Item -Path $outputDir -Recurse -Force
    }
    
    # Run Packer build
    $logFile = "logs/packer_$Name.out.log"
    $errFile = "logs/packer_$Name.err.log"
    
    # Ensure logs directory exists
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }
    
    Log-Message "Running Packer build (logs: $logFile, $errFile)..."
    
    $packerArgs = @(
        "build",
        "-var", "vm_name=$Name",
        "build.pkr.hcl"
    )
    
    if ($Verbose) {
        $packerArgs += "-debug"
    }
    
    $process = Start-Process -FilePath "packer" -ArgumentList $packerArgs -RedirectStandardOutput $logFile -RedirectStandardError $errFile -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Log-Message "Packer build completed successfully"
        return $true
    } else {
        Log-Message "ERROR: Packer build failed with exit code $($process.ExitCode)" "ERROR"
        Log-Message "Check logs: $logFile and $errFile" "ERROR"
        return $false
    }
}

function Test-VMPersistence {
    param([string]$Name)
    
    Log-Message "Testing VM persistence..."
    
    $vmDir = "permanent_vms/$Name"
    $vmxFile = Get-ChildItem -Path $vmDir -Filter "*.vmx" | Select-Object -First 1
    
    if (-not $vmxFile) {
        Log-Message "ERROR: VMX file not found in $vmDir" "ERROR"
        return $false
    }
    
    Log-Message "Found VMX file: $($vmxFile.FullName)"
    
    # Check VMX settings for persistence
    $vmxContent = Get-Content -Path $vmxFile.FullName -Raw
    
    $persistenceChecks = @(
        @{ Setting = "scsi0:0.mode"; Expected = "independent-persistent"; Description = "Disk persistence mode" },
        @{ Setting = "scsi0:0.writeThrough"; Expected = "TRUE"; Description = "Write-through mode" },
        @{ Setting = "ide0:0.present"; Expected = "FALSE"; Description = "CD-ROM disabled" }
    )
    
    $allChecksPass = $true
    foreach ($check in $persistenceChecks) {
        $pattern = "$($check.Setting)\s*=\s*`"$($check.Expected)`""
        if ($vmxContent -match $pattern) {
            Log-Message "✓ $($check.Description): OK"
        } else {
            Log-Message "✗ $($check.Description): FAILED" "ERROR"
            $allChecksPass = $false
        }
    }
    
    return $allChecksPass
}

function Main {
    Log-Message "Starting VM build test..."
    
    if (-not (Test-Prerequisites)) {
        Log-Message "Prerequisites check failed. Exiting." "ERROR"
        exit 1
    }
    
    if (-not $SkipBuild) {
        if (-not (Build-VM -Name $VmName)) {
            Log-Message "VM build failed. Exiting." "ERROR"
            exit 1
        }
    }
    
    if (-not (Test-VMPersistence -Name $VmName)) {
        Log-Message "VM persistence test failed." "ERROR"
        exit 1
    }
    
    Log-Message "All tests passed! VM $VmName is ready and configured for persistence."
    Log-Message "You can now start the VM from: permanent_vms/$VmName"
}

# Run the main function
Main