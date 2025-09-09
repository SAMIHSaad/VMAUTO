# Simple POST API Test for VM Creation
param(
    [string]$BaseUrl = "http://localhost:5000"
)

Write-Host "=== VM Creation API Test ===" -ForegroundColor Green

# Create web session
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Test server connectivity
Write-Host "1. Testing server connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $BaseUrl -Method GET -TimeoutSec 5 -UseBasicParsing -WebSession $session
    Write-Host "Server is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Server is not responding: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Register test user
Write-Host "2. Registering test user..." -ForegroundColor Yellow
try {
    $registerData = @{
        Nom = "Test"
        Prenom = "User"
        Username = "testuser"
        password = "testpass"
    }
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/register" -Method POST -Body ($registerData | ConvertTo-Json) -ContentType "application/json" -WebSession $session
    Write-Host "User registration successful" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "User already exists (OK)" -ForegroundColor Green
    } else {
        Write-Host "Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Login
Write-Host "3. Logging in..." -ForegroundColor Yellow
try {
    $loginData = @{
        Username = "testuser"
        password = "testpass"
    }
    
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/login" -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json" -WebSession $session
    Write-Host "Login successful" -ForegroundColor Green
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get providers status
Write-Host "4. Getting providers status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/providers/status" -Method GET -WebSession $session
    
    if ($response.success) {
        Write-Host "Providers status retrieved" -ForegroundColor Green
        
        $enabledProvider = $null
        foreach ($provider in $response.providers.PSObject.Properties) {
            $name = $provider.Name
            $status = $provider.Value
            $enabled = if ($status.enabled) { "YES" } else { "NO" }
            $connected = if ($status.connected) { "YES" } else { "NO" }
            Write-Host "   $name - Enabled: $enabled, Connected: $connected, Status: $($status.status)" -ForegroundColor White
            
            if ($status.enabled -and $status.connected) {
                $enabledProvider = $name
            }
        }
        
        if (-not $enabledProvider) {
            Write-Host "No enabled and connected providers found" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Using provider: $enabledProvider" -ForegroundColor Green
    }
} catch {
    Write-Host "Error getting providers: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test VM creation
Write-Host "5. Testing VM creation..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$vmData = @{
    vm_name = "test-vm-$timestamp"
    provider = $enabledProvider
    cpu = 2
    ram = 2048
    disk = 20
    os_type = "linux"
}

Write-Host "VM Configuration:" -ForegroundColor Cyan
Write-Host "   Name: $($vmData.vm_name)" -ForegroundColor White
Write-Host "   Provider: $($vmData.provider)" -ForegroundColor White
Write-Host "   CPU: $($vmData.cpu), RAM: $($vmData.ram)MB, Disk: $($vmData.disk)GB" -ForegroundColor White

try {
    Write-Host "Sending VM creation request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/vms" -Method POST -Body ($vmData | ConvertTo-Json) -ContentType "application/json" -WebSession $session -TimeoutSec 60
    
    if ($response.success) {
        Write-Host "VM creation request successful!" -ForegroundColor Green
        Write-Host "Message: $($response.message)" -ForegroundColor White
        
        if ($response.vm_name) {
            Write-Host "VM Name: $($response.vm_name)" -ForegroundColor White
        }
        if ($response.provider) {
            Write-Host "Provider: $($response.provider)" -ForegroundColor White
        }
    } else {
        Write-Host "VM creation failed" -ForegroundColor Red
        Write-Host "Error: $($response.error)" -ForegroundColor Red
        if ($response.stdout) {
            Write-Host "Output: $($response.stdout)" -ForegroundColor Gray
        }
    }
} catch {
    if ($_.Exception.Message -like "*timeout*") {
        Write-Host "VM creation request timed out (this is normal - VM creation takes time)" -ForegroundColor Yellow
        Write-Host "Check the Flask app console for progress" -ForegroundColor White
    } else {
        Write-Host "VM creation error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# List VMs
Write-Host "6. Listing VMs..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/vms" -Method GET -WebSession $session
    
    if ($response.success) {
        $vmCount = $response.vms.Count
        Write-Host "Found $vmCount VMs" -ForegroundColor Green
        
        foreach ($vm in $response.vms) {
            Write-Host "   VM: $($vm.name) [$($vm.hypervisor)] - $($vm.state)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "Error listing VMs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Test Complete ===" -ForegroundColor Green