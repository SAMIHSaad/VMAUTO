# Executable POST API Test for VM Creation
# This script actually executes the API calls to test VM creation

param(
    [string]$BaseUrl = "http://localhost:5000",
    [string]$Username = "testuser",
    [string]$Password = "testpass"
)

Write-Host "=== VM Creation API Executable Test ===" -ForegroundColor Green
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

# Create a web session to maintain cookies
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

function Test-ServerConnectivity {
    Write-Host "`n1️⃣ Testing server connectivity..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $BaseUrl -Method GET -TimeoutSec 5 -UseBasicParsing -WebSession $session
        Write-Host "✅ Server is responding (Status: $($response.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Server is not responding: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Make sure Flask app is running with: python app.py" -ForegroundColor Yellow
        return $false
    }
}

function Register-TestUser {
    Write-Host "`n2️⃣ Registering test user..." -ForegroundColor Yellow
    try {
        $registerData = @{
            Nom = "Test"
            Prenom = "User"
            Username = $Username
            password = $Password
        }
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/register" -Method POST -Body ($registerData | ConvertTo-Json) -ContentType "application/json" -WebSession $session
        Write-Host "✅ User registration successful" -ForegroundColor Green
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode -eq 409) {
            Write-Host "✅ User already exists (OK)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

function Login-User {
    Write-Host "`n3️⃣ Logging in..." -ForegroundColor Yellow
    try {
        $loginData = @{
            Username = $Username
            password = $Password
        }
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/login" -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json" -WebSession $session
        Write-Host "✅ Login successful" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-ProvidersStatus {
    Write-Host "`n4️⃣ Getting providers status..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/providers/status" -Method GET -WebSession $session
        
        if ($response.success) {
            Write-Host "✅ Providers status retrieved" -ForegroundColor Green
            
            foreach ($provider in $response.providers.PSObject.Properties) {
                $name = $provider.Name
                $status = $provider.Value
                $enabled = if ($status.enabled) { "✅" } else { "❌" }
                $connected = if ($status.connected) { "🔗" } else { "🔌" }
                Write-Host "   $enabled $connected $name`: $($status.status)" -ForegroundColor White
            }
            
            return $response.providers
        } else {
            Write-Host "❌ Failed to get providers status" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "❌ Error getting providers: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Test-VMCreation {
    param(
        [string]$TestName,
        [hashtable]$VMData
    )
    
    Write-Host "`n🚀 Testing: $TestName" -ForegroundColor Cyan
    Write-Host "   VM Name: $($VMData.vm_name)" -ForegroundColor White
    Write-Host "   Provider: $($VMData.provider)" -ForegroundColor White
    Write-Host "   Specs: $($VMData.cpu) CPU, $($VMData.ram)MB RAM, $($VMData.disk)GB Disk" -ForegroundColor White
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/vms" -Method POST -Body ($VMData | ConvertTo-Json) -ContentType "application/json" -WebSession $session -TimeoutSec 3600
        
        if ($response.success) {
            Write-Host "✅ VM creation request successful!" -ForegroundColor Green
            Write-Host "   Message: $($response.message)" -ForegroundColor White
            return $true
        } else {
            Write-Host "❌ VM creation failed" -ForegroundColor Red
            Write-Host "   Error: $($response.error)" -ForegroundColor Red
            return $false
        }
    } catch {
        if ($_.Exception.Message -like "*timeout*") {
            Write-Host "⏰ VM creation timed out (this may be normal for long builds)" -ForegroundColor Yellow
            Write-Host "   Check the Flask app console for progress" -ForegroundColor White
            return $false
        } else {
            Write-Host "❌ VM creation error: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

function Get-VMList {
    Write-Host "`n5️⃣ Listing VMs..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/vms" -Method GET -WebSession $session
        
        if ($response.success) {
            $vmCount = $response.vms.Count
            Write-Host "✅ Found $vmCount VMs" -ForegroundColor Green
            
            foreach ($vm in $response.vms) {
                Write-Host "   📱 $($vm.name) [$($vm.hypervisor)] - $($vm.state)" -ForegroundColor White
                Write-Host "      CPU: $($vm.cpu), RAM: $($vm.ram)MB, IP: $($vm.ip_address)" -ForegroundColor Gray
            }
            
            return $response.vms
        } else {
            Write-Host "❌ Failed to list VMs" -ForegroundColor Red
            return @()
        }
    } catch {
        Write-Host "❌ Error listing VMs: $($_.Exception.Message)" -ForegroundColor Red
        return @()
    }
}

# Main execution
Write-Host "Starting VM Creation API Test..." -ForegroundColor White

# Test server connectivity
if (-not (Test-ServerConnectivity)) {
    exit 1
}

# Register test user
if (-not (Register-TestUser)) {
    exit 1
}

# Login
if (-not (Login-User)) {
    exit 1
}

# Get providers status
$providers = Get-ProvidersStatus
if (-not $providers) {
    Write-Host "❌ Cannot proceed without providers" -ForegroundColor Red
    exit 1
}

# Find an enabled provider
$enabledProvider = $null
foreach ($provider in $providers.PSObject.Properties) {
    if ($provider.Value.enabled -and $provider.Value.connected) {
        $enabledProvider = $provider.Name
        break
    }
}

if (-not $enabledProvider) {
    Write-Host "❌ No enabled and connected providers found" -ForegroundColor Red
    Write-Host "Please enable a provider in the hypervisor manager configuration" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Using provider: $enabledProvider" -ForegroundColor Green

# Test VM creation
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$testResults = @()

$testCases = @(
    @{
        Name = "Basic Linux VM"
        Data = @{
            vm_name = "test-vm-basic-$timestamp"
            provider = $enabledProvider
            cpu = 2
            ram = 2048
            disk = 20
            os_type = "linux"
        }
    },
    @{
        Name = "High-Spec VM"
        Data = @{
            vm_name = "test-vm-high-$timestamp"
            provider = $enabledProvider
            cpu = 4
            ram = 4096
            disk = 40
            os_type = "linux"
        }
    }
)

foreach ($testCase in $testCases) {
    $result = Test-VMCreation -TestName $testCase.Name -VMData $testCase.Data
    $testResults += @{
        Name = $testCase.Name
        Success = $result
    }
    
    # Wait between tests
    Start-Sleep -Seconds 2
}

# List VMs
Get-VMList | Out-Null

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor White
Write-Host "📊 Test Summary" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor White

$successCount = ($testResults | Where-Object { $_.Success }).Count
$totalCount = $testResults.Count

Write-Host "Total tests: $totalCount" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $($totalCount - $successCount)" -ForegroundColor Red

foreach ($result in $testResults) {
    $status = if ($result.Success) { "✅" } else { "❌" }
    Write-Host "$status $($result.Name)" -ForegroundColor White
}

if ($successCount -eq $totalCount) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ Some tests failed. Check the output above for details." -ForegroundColor Yellow
    Write-Host "Note: VM creation failures may be due to VNC issues or long build times." -ForegroundColor White
    exit 1
}