# Detailed POST API Test for VM Creation with Error Handling
param(
    [string]$BaseUrl = "http://localhost:5000"
)

Write-Host "=== Detailed VM Creation API Test ===" -ForegroundColor Green

# Create web session
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Function to make API calls with detailed error handling
function Invoke-APICall {
    param(
        [string]$Uri,
        [string]$Method,
        [object]$Body = $null,
        [string]$Description
    )
    
    Write-Host "Making API call: $Description" -ForegroundColor Cyan
    Write-Host "   URI: $Uri" -ForegroundColor Gray
    Write-Host "   Method: $Method" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Uri
            Method = $Method
            WebSession = $session
            ContentType = "application/json"
        }
        
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $params.Body = $jsonBody
            Write-Host "   Body: $jsonBody" -ForegroundColor Gray
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "   Success: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Green
        return @{ Success = $true; Data = $response }
        
    } catch {
        $errorDetails = @{
            Message = $_.Exception.Message
            StatusCode = $null
            ResponseBody = $null
        }
        
        if ($_.Exception.Response) {
            $errorDetails.StatusCode = $_.Exception.Response.StatusCode
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $errorDetails.ResponseBody = $reader.ReadToEnd()
                $reader.Close()
            } catch {
                $errorDetails.ResponseBody = "Could not read response body"
            }
        }
        
        Write-Host "   Error: $($errorDetails.Message)" -ForegroundColor Red
        Write-Host "   Status Code: $($errorDetails.StatusCode)" -ForegroundColor Red
        Write-Host "   Response Body: $($errorDetails.ResponseBody)" -ForegroundColor Red
        
        return @{ Success = $false; Error = $errorDetails }
    }
}

# Test server connectivity
$result = Invoke-APICall -Uri $BaseUrl -Method "GET" -Description "Server connectivity test"
if (-not $result.Success) {
    Write-Host "Cannot proceed without server connectivity" -ForegroundColor Red
    exit 1
}

# Register test user
$registerData = @{
    Nom = "Test"
    Prenom = "User"
    Username = "testuser"
    password = "testpass"
}

$result = Invoke-APICall -Uri "$BaseUrl/api/register" -Method "POST" -Body $registerData -Description "User registration"
# Continue even if registration fails (user might already exist)

# Login
$loginData = @{
    Username = "testuser"
    password = "testpass"
}

$result = Invoke-APICall -Uri "$BaseUrl/api/login" -Method "POST" -Body $loginData -Description "User login"
if (-not $result.Success) {
    Write-Host "Cannot proceed without authentication" -ForegroundColor Red
    exit 1
}

# Get providers status
$result = Invoke-APICall -Uri "$BaseUrl/api/providers/status" -Method "GET" -Description "Get providers status"
if (-not $result.Success) {
    Write-Host "Cannot proceed without providers information" -ForegroundColor Red
    exit 1
}

$providers = $result.Data.providers
$enabledProvider = $null

Write-Host "`nProvider Analysis:" -ForegroundColor Yellow
foreach ($provider in $providers.PSObject.Properties) {
    $name = $provider.Name
    $status = $provider.Value
    Write-Host "   Provider: $name" -ForegroundColor White
    Write-Host "     Enabled: $($status.enabled)" -ForegroundColor Gray
    Write-Host "     Connected: $($status.connected)" -ForegroundColor Gray
    Write-Host "     Status: $($status.status)" -ForegroundColor Gray
    
    if ($status.enabled -and $status.connected) {
        $enabledProvider = $name
        Write-Host "     -> Selected for testing" -ForegroundColor Green
    }
}

if (-not $enabledProvider) {
    Write-Host "No enabled and connected providers found" -ForegroundColor Red
    exit 1
}

# Get templates for the selected provider
$result = Invoke-APICall -Uri "$BaseUrl/api/templates?provider=$enabledProvider" -Method "GET" -Description "Get templates for $enabledProvider"
$templates = if ($result.Success) { $result.Data.templates } else { @() }

Write-Host "`nAvailable templates for $enabledProvider`: $($templates -join ', ')" -ForegroundColor Yellow

# Test VM creation with different configurations
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

$testConfigurations = @(
    @{
        Name = "Basic VM"
        Data = @{
            vm_name = "test-basic-$timestamp"
            provider = $enabledProvider
            cpu = 2
            ram = 2048
            disk = 20
            os_type = "linux"
        }
    },
    @{
        Name = "VM with Template"
        Data = @{
            vm_name = "test-template-$timestamp"
            provider = $enabledProvider
            cpu = 2
            ram = 2048
            disk = 20
            os_type = "linux"
            template = if ($templates.Count -gt 0) { $templates[0] } else { $null }
        }
    }
)

foreach ($config in $testConfigurations) {
    Write-Host "`n" + ("=" * 50) -ForegroundColor White
    Write-Host "Testing: $($config.Name)" -ForegroundColor Yellow
    Write-Host ("=" * 50) -ForegroundColor White
    
    # Remove null values from the configuration
    $cleanData = @{}
    foreach ($key in $config.Data.Keys) {
        if ($config.Data[$key] -ne $null) {
            $cleanData[$key] = $config.Data[$key]
        }
    }
    
    Write-Host "Configuration:" -ForegroundColor Cyan
    foreach ($key in $cleanData.Keys) {
        Write-Host "   $key`: $($cleanData[$key])" -ForegroundColor White
    }
    
    $result = Invoke-APICall -Uri "$BaseUrl/api/vms" -Method "POST" -Body $cleanData -Description "Create VM: $($config.Name)"
    
    if ($result.Success) {
        Write-Host "VM creation initiated successfully!" -ForegroundColor Green
        if ($result.Data.vm_name) {
            Write-Host "VM Name: $($result.Data.vm_name)" -ForegroundColor White
        }
        if ($result.Data.message) {
            Write-Host "Message: $($result.Data.message)" -ForegroundColor White
        }
    } else {
        Write-Host "VM creation failed - analyzing error..." -ForegroundColor Red
        
        # Try to parse the error response
        if ($result.Error.ResponseBody) {
            try {
                $errorResponse = $result.Error.ResponseBody | ConvertFrom-Json
                Write-Host "Parsed Error Response:" -ForegroundColor Yellow
                Write-Host "   Success: $($errorResponse.success)" -ForegroundColor White
                Write-Host "   Error: $($errorResponse.error)" -ForegroundColor White
                if ($errorResponse.stdout) {
                    Write-Host "   Stdout: $($errorResponse.stdout)" -ForegroundColor Gray
                }
            } catch {
                Write-Host "Raw Error Response: $($result.Error.ResponseBody)" -ForegroundColor Gray
            }
        }
    }
    
    # Wait between tests
    Start-Sleep -Seconds 2
}

# List VMs to see current state
Write-Host "`n" + ("=" * 50) -ForegroundColor White
Write-Host "Current VM List" -ForegroundColor Yellow
Write-Host ("=" * 50) -ForegroundColor White

$result = Invoke-APICall -Uri "$BaseUrl/api/vms" -Method "GET" -Description "List all VMs"
if ($result.Success) {
    $vms = $result.Data.vms
    Write-Host "Total VMs: $($vms.Count)" -ForegroundColor Green
    
    foreach ($vm in $vms) {
        Write-Host "   $($vm.name) [$($vm.hypervisor)] - $($vm.state)" -ForegroundColor White
        if ($vm.ip_address) {
            Write-Host "     IP: $($vm.ip_address)" -ForegroundColor Gray
        }
        Write-Host "     CPU: $($vm.cpu), RAM: $($vm.ram)MB" -ForegroundColor Gray
    }
}

Write-Host "`n=== Detailed Test Complete ===" -ForegroundColor Green