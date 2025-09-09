# Manual POST API Test Script for VM Creation
# This script provides curl commands to test the VM creation API

Write-Host "=== VM Creation API Manual Test Guide ===" -ForegroundColor Green
Write-Host "Base URL: http://localhost:5000" -ForegroundColor Cyan

# Check if server is running
Write-Host "`n1. Testing server connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Server is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Server is not responding. Make sure Flask app is running with: python app.py" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Authentication Steps:" -ForegroundColor Yellow
Write-Host "First, you need to register and login to get authentication cookies." -ForegroundColor White

Write-Host "`n📝 Register a test user:" -ForegroundColor Cyan
$registerCommand = @"
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "Nom": "Test",
    "Prenom": "User",
    "Username": "testuser",
    "password": "testpass"
  }' \
  -c cookies.txt
"@
Write-Host $registerCommand -ForegroundColor Gray

Write-Host "`n🔐 Login to get authentication:" -ForegroundColor Cyan
$loginCommand = @"
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "Username": "testuser",
    "password": "testpass"
  }' \
  -c cookies.txt -b cookies.txt
"@
Write-Host $loginCommand -ForegroundColor Gray

Write-Host "`n3. Get Provider Status:" -ForegroundColor Yellow
$providerCommand = @"
curl -X GET http://localhost:5000/api/providers/status \
  -H "Content-Type: application/json" \
  -b cookies.txt
"@
Write-Host $providerCommand -ForegroundColor Gray

Write-Host "`n4. VM Creation POST Tests:" -ForegroundColor Yellow

Write-Host "`n🚀 Test 1: Basic Linux VM Creation" -ForegroundColor Cyan
$vmName1 = "test-vm-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$createVM1 = @"
curl -X POST http://localhost:5000/api/vms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "vm_name": "$vmName1",
    "provider": "vmware",
    "cpu": 2,
    "ram": 2048,
    "disk": 20,
    "os_type": "linux"
  }'
"@
Write-Host $createVM1 -ForegroundColor Gray

Write-Host "`n🚀 Test 2: High-Spec VM Creation" -ForegroundColor Cyan
$vmName2 = "test-vm-high-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$createVM2 = @"
curl -X POST http://localhost:5000/api/vms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "vm_name": "$vmName2",
    "provider": "vmware",
    "cpu": 4,
    "ram": 4096,
    "disk": 40,
    "os_type": "linux"
  }'
"@
Write-Host $createVM2 -ForegroundColor Gray

Write-Host "`n🚀 Test 3: Template-based VM Creation" -ForegroundColor Cyan
$vmName3 = "test-vm-template-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$createVM3 = @"
curl -X POST http://localhost:5000/api/vms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "vm_name": "$vmName3",
    "provider": "vmware",
    "template": "ubuntu",
    "cpu": 2,
    "ram": 2048,
    "disk": 20,
    "os_type": "linux"
  }'
"@
Write-Host $createVM3 -ForegroundColor Gray

Write-Host "`n5. List VMs:" -ForegroundColor Yellow
$listVMs = @"
curl -X GET http://localhost:5000/api/vms \
  -H "Content-Type: application/json" \
  -b cookies.txt
"@
Write-Host $listVMs -ForegroundColor Gray

Write-Host "`n6. PowerShell Alternative (using Invoke-RestMethod):" -ForegroundColor Yellow

Write-Host "`n📝 PowerShell Register:" -ForegroundColor Cyan
Write-Host @"
`$registerData = @{
    Nom = "Test"
    Prenom = "User"
    Username = "testuser"
    password = "testpass"
}
`$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod -Uri "http://localhost:5000/api/register" -Method POST -Body (`$registerData | ConvertTo-Json) -ContentType "application/json" -WebSession `$session
"@ -ForegroundColor Gray

Write-Host "`n🔐 PowerShell Login:" -ForegroundColor Cyan
Write-Host @"
`$loginData = @{
    Username = "testuser"
    password = "testpass"
}
Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method POST -Body (`$loginData | ConvertTo-Json) -ContentType "application/json" -WebSession `$session
"@ -ForegroundColor Gray

Write-Host "`n🚀 PowerShell VM Creation:" -ForegroundColor Cyan
Write-Host @"
`$vmData = @{
    vm_name = "test-vm-ps-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    provider = "vmware"
    cpu = 2
    ram = 2048
    disk = 20
    os_type = "linux"
}
Invoke-RestMethod -Uri "http://localhost:5000/api/vms" -Method POST -Body (`$vmData | ConvertTo-Json) -ContentType "application/json" -WebSession `$session
"@ -ForegroundColor Gray

Write-Host "`n📋 Expected Response Format:" -ForegroundColor Yellow
Write-Host @"
Success Response:
{
  "success": true,
  "vm_name": "test-vm-123",
  "provider": "vmware",
  "message": "VM 'test-vm-123' created successfully"
}

Error Response:
{
  "success": false,
  "error": "Error message here",
  "stdout": "Packer output (if available)"
}
"@ -ForegroundColor Gray

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "- VM creation can take 10-30 minutes depending on the configuration" -ForegroundColor White
Write-Host "- Use unique VM names to avoid conflicts" -ForegroundColor White
Write-Host "- Check provider status first to ensure VMware is enabled and connected" -ForegroundColor White
Write-Host "- Monitor the Flask app console for detailed logs during VM creation" -ForegroundColor White
Write-Host "- The API will automatically retry with headless mode if VNC fails" -ForegroundColor White

Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
Write-Host "- If authentication fails, check if the database is initialized" -ForegroundColor White
Write-Host "- If provider is not enabled, check hypervisor_manager configuration" -ForegroundColor White
Write-Host "- If VM creation fails, check the VNC troubleshooting guide" -ForegroundColor White
Write-Host "- Use the Python test script for automated testing: python test_post_api.py" -ForegroundColor White

Write-Host "`n=== Ready to Test! ===" -ForegroundColor Green
Write-Host "Copy and paste the curl commands above to test the API manually." -ForegroundColor Cyan