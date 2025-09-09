
param (
    [string]$sourceDirectory,
    [string]$destinationDirectory,
    [switch]$OpenAfterRegister
)

# Log function
function Log-Message {
    param (
        [string]$message
    )
    Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] $message"
}

Log-Message "Starting VM registration script."
Log-Message "Source: $sourceDirectory"
Log-Message "Destination: $destinationDirectory"

# Check if source directory exists
if (-not (Test-Path -Path $sourceDirectory -PathType Container)) {
    Log-Message "ERROR: Source directory not found."
    Exit 1
}

# Create destination directory if it doesn't exist
if (-not (Test-Path -Path $destinationDirectory -PathType Container)) {
    Log-Message "Creating destination directory."
    New-Item -ItemType Directory -Path $destinationDirectory | Out-Null
}

# Copy or move VM files (prefer move to avoid Packer cleanup deleting our copy)
Log-Message "Copying VM files..."
try {
    # If destination is empty, move to be faster and atomic; else copy
    if (-not (Get-ChildItem -Path $destinationDirectory -Force | Where-Object { $_.Name -ne '.' -and $_.Name -ne '..' })) {
        Move-Item -Path "$sourceDirectory\*" -Destination $destinationDirectory -Force
    } else {
        Copy-Item -Path "$sourceDirectory\*" -Destination $destinationDirectory -Recurse -Force
    }
}
catch {
    Log-Message "Move/Copy failed; attempting copy fallback"
    Copy-Item -Path "$sourceDirectory\*" -Destination $destinationDirectory -Recurse -Force
}

# Find the VMX file
$vmxFile = Get-ChildItem -Path $destinationDirectory -Filter "*.vmx" | Select-Object -First 1

if ($null -eq $vmxFile) {
    Log-Message "ERROR: No .vmx file found in the destination directory."
    Exit 1
}

Log-Message "Found VMX file: $($vmxFile.FullName)"

# Ensure VMX will boot from disk and not keep ISO connected (target actual CD-ROM devices)
Log-Message "Ensuring VM boots from disk (detaching ISO and enforcing persistence)..."
try {
    $vmxText = Get-Content -Path $vmxFile.FullName -Raw

    # Helper: set or add a vmx key
    function Set-Or-AddVmxLine {
        param([string]$text, [string]$key, [string]$value)
        $escaped = [regex]::Escape($key)
        # Build regex patterns safely (avoid escaping quotes in PowerShell strings)
        $matchPattern    = '(?m)^{0}\s*=\s*"[^"]*"' -f $escaped
        $replacePattern  = '(?m)^({0})\s*=\s*"[^"]*"' -f $escaped
        $replacement     = '$1 = "{0}"' -f $value
        if ($text -match $matchPattern) {
            return ($text -replace $replacePattern, $replacement)
        } else {
            return ($text + "`n$key = `"$value`"`n")
        }
    }

    # Detach common CD-ROM device addresses (cover all typical mappings including ide0:0)
    $cdromAddrs = @("ide0:0", "ide0:1", "ide1:0", "sata0:1")
    foreach ($addr in $cdromAddrs) {
        # Ensure device is not connected
        $vmxText = Set-Or-AddVmxLine -text $vmxText -key "$addr.present" -value "FALSE"
        $vmxText = Set-Or-AddVmxLine -text $vmxText -key "$addr.startConnected" -value "FALSE"
        # Normalize device type and clear any ISO path
        $vmxText = Set-Or-AddVmxLine -text $vmxText -key "$addr.deviceType" -value "cdrom-raw"
        # Set both canonical and lowercase variants to be safe
        $vmxText = Set-Or-AddVmxLine -text $vmxText -key "$addr.fileName" -value ""
        $vmxText = Set-Or-AddVmxLine -text $vmxText -key "$addr.filename" -value ""
    }

    # For EFI firmware, boot order keys may not apply like BIOS; still set both common variants
    if ($vmxText -match '(?mi)^bios\.bootOrder\s*=') {
        $vmxText = $vmxText -replace '(?mi)^bios\.bootOrder\s*=\s*"[^"]*"', 'bios.bootOrder = "hdd,cdrom"'
    } else {
        $vmxText += "`nbios.bootOrder = `"hdd,cdrom`"`n"
    }
    if ($vmxText -match '(?mi)^bios\.bootorder\s*=') {
        $vmxText = $vmxText -replace '(?mi)^bios\.bootorder\s*=\s*"[^"]*"', 'bios.bootorder = "hdd,cdrom"'
    } else {
        $vmxText += "`nbios.bootorder = `"hdd,cdrom`"`n"
    }

    # Enforce persistent disk mode and no redo logs
    $vmxText = Set-Or-AddVmxLine -text $vmxText -key "scsi0:0.mode" -value "independent-persistent"
    $vmxText = Set-Or-AddVmxLine -text $vmxText -key "scsi0:0.redo" -value ""

    Set-Content -Path $vmxFile.FullName -Value $vmxText -Encoding ASCII
    Log-Message "VMX updated: ISO detached and persistence enforced."
}
catch {
    Log-Message "WARNING: Failed to adjust VMX for ISO detach/persistence: $_"
}

# Start the VM in VMware Workstation UI (no registration needed for Workstation)
function Start-VmInGui {
    param([string]$vmx)
    $vmrunPath   = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
    $vmwareGui   = "C:\Program Files (x86)\VMware\VMware Workstation\vmware.exe"

    if (Test-Path $vmrunPath) {
        Log-Message "Starting VM via vmrun (GUI)..."
        & $vmrunPath start "$vmx" gui
        $exit = $LASTEXITCODE
        if ($exit -eq 0) {
            Log-Message "VM started in GUI via vmrun."
            return
        }
        Log-Message "WARNING: vmrun start returned exit code $exit; falling back to vmware.exe"
    } else {
        Log-Message "WARNING: vmrun.exe not found; falling back to vmware.exe"
    }

    if (Test-Path $vmwareGui) {
        Start-Process -FilePath $vmwareGui -ArgumentList "`"$vmx`""
        Log-Message "VMX opened in VMware Workstation GUI."
    } else {
        Log-Message "ERROR: VMware Workstation not found at expected path."
    }
}

# Skip explicit registration: unnecessary and flaky on some host types
# Optionally open/start the VM in VMware Workstation UI
if ($OpenAfterRegister) {
    Start-VmInGui -vmx $vmxFile.FullName
}

Log-Message "Script finished."
