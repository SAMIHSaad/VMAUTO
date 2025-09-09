# Test script for Ubuntu automated installation
# This script validates the Packer configuration and starts the build

Write-Host "=== Ubuntu Automated Installation Test ===" -ForegroundColor Green
Write-Host ""

# Check if Packer is installed
Write-Host "Checking Packer installation..." -ForegroundColor Yellow
try {
    $packerVersion = packer version
    Write-Host "✓ Packer found: $packerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Packer not found. Please install Packer first." -ForegroundColor Red
    exit 1
}

# Check if ISO file exists
$isoPath = "C:/Users/saads/OneDrive/Documents/Coding/demo-automation/templates/ubuntu-24.04.2-desktop-amd64.iso"
Write-Host "Checking ISO file..." -ForegroundColor Yellow
if (Test-Path $isoPath) {
    Write-Host "✓ ISO file found: $isoPath" -ForegroundColor Green
} else {
    Write-Host "✗ ISO file not found: $isoPath" -ForegroundColor Red
    Write-Host "Please update the iso_path variable in build.pkr.hcl" -ForegroundColor Yellow
    exit 1
}

# Validate Packer configuration
Write-Host "Validating Packer configuration..." -ForegroundColor Yellow
try {
    packer validate build.pkr.hcl
    Write-Host "✓ Packer configuration is valid" -ForegroundColor Green
} catch {
    Write-Host "✗ Packer configuration validation failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Display configuration summary
Write-Host ""
Write-Host "=== Configuration Summary ===" -ForegroundColor Cyan
Write-Host "• Auto-create account: ubuntu/ubuntu" -ForegroundColor White
Write-Host "• Keyboard layout: AZERTY (French)" -ForegroundColor White
Write-Host "• Locale: fr_FR.UTF-8" -ForegroundColor White
Write-Host "• Auto-select: Try or Install Ubuntu" -ForegroundColor White
Write-Host "• Skip configuration steps: Yes" -ForegroundColor White
Write-Host "• SSH enabled: Yes" -ForegroundColor White
Write-Host "• Ansible pre-installed: Yes" -ForegroundColor White
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to start the Ubuntu build? (y/N)"
if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
    Write-Host "Starting Ubuntu build..." -ForegroundColor Green
    Write-Host "This will take approximately 15-30 minutes depending on your system." -ForegroundColor Yellow
    Write-Host ""
    
    # Start the build
    packer build -var="vm_name=ubuntu-automated" build.pkr.hcl
} else {
    Write-Host "Build cancelled." -ForegroundColor Yellow
}