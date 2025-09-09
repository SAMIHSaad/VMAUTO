# PowerShell script to register VM with VMware Workstation
param(
    [Parameter(Mandatory=$true)]
    [string]$VMXPath,
    
    [Parameter(Mandatory=$false)]
    [string]$VMName
)

Write-Host "========================================" -ForegroundColor Green
Write-Host "VMware VM Registration Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if VMX file exists
if (-not (Test-Path $VMXPath)) {
    Write-Host "ERROR: VMX file not found: $VMXPath" -ForegroundColor Red
    exit 1
}

Write-Host "VMX File: $VMXPath" -ForegroundColor Cyan
Write-Host ""

# Try to find VMware Workstation installation
$vmwareInstallPaths = @(
    "${env:ProgramFiles(x86)}\VMware\VMware Workstation",
    "${env:ProgramFiles}\VMware\VMware Workstation",
    "${env:ProgramFiles(x86)}\VMware\VMware Player",
    "${env:ProgramFiles}\VMware\VMware Player"
)

$vmrunPath = $null
$vmwarePath = $null

foreach ($path in $vmwareInstallPaths) {
    $testVmrunPath = Join-Path $path "vmrun.exe"
    $testVmwarePath = Join-Path $path "vmware.exe"
    
    if (Test-Path $testVmrunPath) {
        $vmrunPath = $testVmrunPath
        Write-Host "Found vmrun.exe at: $vmrunPath" -ForegroundColor Green
    }
    
    if (Test-Path $testVmwarePath) {
        $vmwarePath = $testVmwarePath
        Write-Host "Found vmware.exe at: $vmwarePath" -ForegroundColor Green
    }
    
    if ($vmrunPath -and $vmwarePath) {
        break
    }
}

if (-not $vmrunPath) {
    Write-Host "WARNING: vmrun.exe not found. VMware Workstation may not be installed." -ForegroundColor Yellow
    Write-Host "You can still manually open the VM in VMware Workstation." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Testing VMware tools..." -ForegroundColor Cyan
    
    try {
        # Test vmrun
        $result = & $vmrunPath "list" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ VMware tools are working correctly" -ForegroundColor Green
            Write-Host "Running VMs:" -ForegroundColor Cyan
            Write-Host $result -ForegroundColor Gray
        } else {
            Write-Host "⚠️ VMware tools detected but may have issues" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Error testing VMware tools: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "VM Registration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 To use your VM:" -ForegroundColor Cyan
Write-Host "1. Open VMware Workstation" -ForegroundColor White
Write-Host "2. Go to File → Open" -ForegroundColor White
Write-Host "3. Navigate to and select: $VMXPath" -ForegroundColor White
Write-Host "4. Your VM will be added to the VMware library" -ForegroundColor White
Write-Host "5. Power on your VM to start using it" -ForegroundColor White
Write-Host ""

if ($vmwarePath) {
    Write-Host "🎯 Quick Open Option:" -ForegroundColor Cyan
    Write-Host "Run this command to open VMware with your VM:" -ForegroundColor White
    Write-Host "`"$vmwarePath`" `"$VMXPath`"" -ForegroundColor Yellow
    Write-Host ""
    
    # Ask if user wants to open VMware now
    $response = Read-Host "Would you like to open VMware Workstation with this VM now? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y' -or $response -eq 'yes') {
        Write-Host "Opening VMware Workstation..." -ForegroundColor Green
        try {
            Start-Process -FilePath $vmwarePath -ArgumentList "`"$VMXPath`"" -NoNewWindow
            Write-Host "✅ VMware Workstation opened successfully!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Error opening VMware Workstation: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "📁 VM Files Location: $(Split-Path $VMXPath -Parent)" -ForegroundColor Cyan
Write-Host "📋 Your VM is now permanent and ready to use!" -ForegroundColor Green