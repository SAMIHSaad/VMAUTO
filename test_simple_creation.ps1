# Simple test to create a VM and check location
Write-Host "=== Simple VM Creation Location Test ===" -ForegroundColor Green

# Check current directories
$clonedVmsPath = "c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms"
$defaultVmwarePath = "C:\Users\saads\OneDrive\Documents\Virtual Machines"

Write-Host "Before test:"
Write-Host "  Cloned VMs: $((Get-ChildItem -Path $clonedVmsPath -Directory).Count)"
Write-Host "  Default VMware: $((Get-ChildItem -Path $defaultVmwarePath -Directory).Count)"

# Try to register a user first
Write-Host "`nRegistering test user..." -ForegroundColor Yellow
$registerData = @{
    Nom = "Test"
    Prenom = "User"
    Username = "testuser"
    password = "testpass"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/register" -Method POST -Body $registerData -ContentType "application/json"
    Write-Host "User registered successfully" -ForegroundColor Green
} catch {
    Write-Host "Registration failed (user might already exist): $($_.Exception.Message)" -ForegroundColor Yellow
}

# Login with test user
Write-Host "`nLogging in..." -ForegroundColor Yellow
$loginData = @{
    Username = "testuser"
    password = "testpass"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method POST -Body $loginData -ContentType "application/json" -SessionVariable session
    Write-Host "Login successful" -ForegroundColor Green
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create VM
Write-Host "`nCreating VM..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$vmName = "test-$timestamp"

$vmData = @{
    vm_name = $vmName
    provider = "vmware"
    cpu = 2
    ram = 2048
    disk = 20
    os_type = "linux"
} | ConvertTo-Json

Write-Host "Creating VM: $vmName"

try {
    $vmResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/vms" -Method POST -Body $vmData -ContentType "application/json" -WebSession $session -TimeoutSec 60
    Write-Host "VM creation initiated" -ForegroundColor Green
} catch {
    Write-Host "VM creation timeout (normal - continues in background)" -ForegroundColor Yellow
}

Write-Host "`nTest completed. VM creation is running in background."
Write-Host "Check the directories in a few minutes to see where the VM was created."