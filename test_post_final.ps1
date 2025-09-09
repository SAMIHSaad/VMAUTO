# Final POST API Test for VM Creation
param(
    [string]$BaseUrl = "http://localhost:5000"
)

Write-Host "=== Final VM Creation API Test ===" -ForegroundColor Green

# Create web session
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Login
Write-Host "1. Logging in..." -ForegroundColor Yellow
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

# Test VM creation
Write-Host "2. Testing VM creation..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$vmData = @{
    vm_name = "test-vm-final-$timestamp"
    provider = "vmware"
    cpu = 2
    ram = 2048
    disk = 20
    os_type = "linux"
}

Write-Host "VM Configuration:" -ForegroundColor Cyan
foreach ($key in $vmData.Keys) {
    Write-Host "   $key`: $($vmData[$key])" -ForegroundColor White
}

try {
    Write-Host "Sending VM creation request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/vms" -Method POST -Body ($vmData | ConvertTo-Json) -ContentType "application/json" -WebSession $session -TimeoutSec 120
    
    Write-Host "Response received:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor White
    
    if ($response.success) {
        Write-Host "VM creation initiated successfully!" -ForegroundColor Green
    } else {
        Write-Host "VM creation failed: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host "   Message: $($_.Exception.Message)" -ForegroundColor White
    
    if ($_.Exception.Response) {
        Write-Host "   Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor White
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            Write-Host "   Response Body: $responseBody" -ForegroundColor White
            
            # Try to parse as JSON
            try {
                $errorResponse = $responseBody | ConvertFrom-Json
                Write-Host "   Parsed Error:" -ForegroundColor Yellow
                Write-Host "     Success: $($errorResponse.success)" -ForegroundColor White
                Write-Host "     Error: $($errorResponse.error)" -ForegroundColor White
            } catch {
                Write-Host "   Raw Response: $responseBody" -ForegroundColor Gray
            }
        } catch {
            Write-Host "   Could not read response body" -ForegroundColor Gray
        }
    }
}

Write-Host "=== Test Complete ===" -ForegroundColor Green