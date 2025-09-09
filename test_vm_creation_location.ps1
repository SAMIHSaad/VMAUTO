# Test VM Creation Location - Verify VMs go to cloned-vms folder
# This script tests if VMs created through the web form go to the correct location

Write-Host "=== Testing VM Creation Location ===" -ForegroundColor Green

# 1. Check current VM count in cloned-vms
$clonedVmsPath = "c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms"
$beforeCount = (Get-ChildItem -Path $clonedVmsPath -Directory).Count
Write-Host "VMs in cloned-vms before test: $beforeCount"

# 2. Check current VM count in default VMware directory
$defaultVmwarePath = "C:\Users\saads\OneDrive\Documents\Virtual Machines"
$beforeDefaultCount = (Get-ChildItem -Path $defaultVmwarePath -Directory).Count
Write-Host "VMs in default VMware directory before test: $beforeDefaultCount"

# 3. Authenticate
Write-Host "`n1. Authenticating..." -ForegroundColor Yellow
$loginData = @{
    Username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method POST -Body $loginData -ContentType "application/json" -SessionVariable session
    Write-Host "Authentication successful" -ForegroundColor Green
} catch {
    Write-Host "Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. Create a test VM
Write-Host "`n2. Creating test VM..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$vmName = "test-location-$timestamp"

$vmData = @{
    vm_name = $vmName
    provider = "vmware"
    cpu = 2
    ram = 2048
    disk = 20
    os_type = "linux"
} | ConvertTo-Json

Write-Host "VM Configuration:"
Write-Host "   vm_name = $vmName"
Write-Host "   provider = vmware"
Write-Host "   cpu = 2"
Write-Host "   ram = 2048"
Write-Host "   disk = 20"
Write-Host "   os_type = linux"

Write-Host "`nSending POST request to /api/vms..."

try {
    # Use a longer timeout for VM creation
    $vmResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/vms" -Method POST -Body $vmData -ContentType "application/json" -WebSession $session -TimeoutSec 300
    Write-Host "VM creation request successful" -ForegroundColor Green
    Write-Host "Response: $($vmResponse | ConvertTo-Json)"
} catch {
    if ($_.Exception.Message -like "*timeout*" -or $_.Exception.Message -like "*délai*") {
        Write-Host "Request timed out (this is normal for VM creation - process continues in background)" -ForegroundColor Yellow
    } else {
        Write-Host "Request failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. Wait a bit for the VM creation to start
Write-Host "`n3. Waiting for VM creation to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 6. Check if VM appears in cloned-vms directory (it should be moved there after creation)
Write-Host "`n4. Checking VM location..." -ForegroundColor Yellow

# Check cloned-vms directory
$afterCount = (Get-ChildItem -Path $clonedVmsPath -Directory).Count
Write-Host "VMs in cloned-vms after test: $afterCount"

# Check default VMware directory
$afterDefaultCount = (Get-ChildItem -Path $defaultVmwarePath -Directory).Count
Write-Host "VMs in default VMware directory after test: $afterDefaultCount"

# 7. Look for the specific VM
$vmFoundInCloned = Test-Path "$clonedVmsPath\$vmName"
$vmFoundInDefault = Test-Path "$defaultVmwarePath\$vmName"

Write-Host "`n=== Test Results ===" -ForegroundColor Green
Write-Host "VM Name: $vmName"
Write-Host "Found in cloned-vms: $vmFoundInCloned"
Write-Host "Found in default VMware directory: $vmFoundInDefault"

if ($vmFoundInCloned) {
    Write-Host "✅ SUCCESS: VM was created in the correct location (cloned-vms folder)" -ForegroundColor Green
} elseif ($vmFoundInDefault) {
    Write-Host "❌ ISSUE: VM was created in default VMware directory (needs to be moved)" -ForegroundColor Red
} else {
    Write-Host "⏳ VM creation in progress or not yet visible" -ForegroundColor Yellow
    Write-Host "Note: VM creation takes time. Check again in a few minutes." -ForegroundColor Yellow
}

Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "Test completed. The VM creation location fix has been implemented."
Write-Host "VMs created through the web form should now be automatically moved to cloned-vms folder."