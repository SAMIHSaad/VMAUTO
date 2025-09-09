# Fix VMware VNC Connection Issues
# This script addresses common VNC connection problems with Packer and VMware

Write-Host "=== VMware VNC Connection Fix ===" -ForegroundColor Green

# 1. Check and start VMware services
Write-Host "`n1. Checking VMware services..." -ForegroundColor Yellow

$vmwareServices = @(
    "VMwareHostd",
    "VMAuthdService", 
    "VMnetDHCP",
    "VMware NAT Service"
)

foreach ($service in $vmwareServices) {
    try {
        $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
        if ($svc) {
            if ($svc.Status -ne "Running") {
                Write-Host "Starting service: $service" -ForegroundColor Cyan
                Start-Service -Name $service -ErrorAction SilentlyContinue
            } else {
                Write-Host "Service $service is already running" -ForegroundColor Green
            }
        } else {
            Write-Host "Service $service not found (may not be installed)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Could not manage service $service : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. Configure Windows Firewall for VNC ports
Write-Host "`n2. Configuring Windows Firewall for VNC ports..." -ForegroundColor Yellow

$vncPorts = @(5900, 5901, 5902, 5903, 5904, 5905)

foreach ($port in $vncPorts) {
    try {
        # Check if rule already exists
        $existingRule = Get-NetFirewallRule -DisplayName "VMware VNC Port $port" -ErrorAction SilentlyContinue
        
        if (-not $existingRule) {
            Write-Host "Creating firewall rule for port $port" -ForegroundColor Cyan
            New-NetFirewallRule -DisplayName "VMware VNC Port $port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -Profile Any
        } else {
            Write-Host "Firewall rule for port $port already exists" -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not create firewall rule for port $port : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. Check if ports are available
Write-Host "`n3. Checking port availability..." -ForegroundColor Yellow

foreach ($port in $vncPorts) {
    try {
        $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection) {
            Write-Host "Port $port is in use" -ForegroundColor Red
        } else {
            Write-Host "Port $port is available" -ForegroundColor Green
        }
    } catch {
        Write-Host "Port $port is available" -ForegroundColor Green
    }
}

# 4. Update VMware preferences to enable VNC
Write-Host "`n4. Updating VMware preferences..." -ForegroundColor Yellow

$preferencesPath = "$env:APPDATA\VMware\preferences.ini"

if (Test-Path $preferencesPath) {
    try {
        $preferences = Get-Content $preferencesPath
        $vncSettings = @(
            'pref.vmx.defaultVMPath = "C:\Users\saads\OneDrive\Documents\Virtual Machines"',
            'RemoteDisplay.vnc.enabled = "TRUE"',
            'RemoteDisplay.vnc.port = "5902"',
            'pref.vmplayer.exit.vmAction = "poweroff"',
            'pref.vmplayer.confirmOnExit = "FALSE"'
        )
        
        $modified = $false
        foreach ($setting in $vncSettings) {
            $key = $setting.Split('=')[0].Trim()
            if (-not ($preferences | Select-String -Pattern "^$key\s*=")) {
                Write-Host "Adding setting: $setting" -ForegroundColor Cyan
                $preferences += $setting
                $modified = $true
            }
        }
        
        if ($modified) {
            $preferences | Set-Content $preferencesPath
            Write-Host "VMware preferences updated" -ForegroundColor Green
        } else {
            Write-Host "VMware preferences already configured" -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not update VMware preferences: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "VMware preferences file not found at $preferencesPath" -ForegroundColor Red
}

# 5. Kill any hanging VMware processes
Write-Host "`n5. Cleaning up VMware processes..." -ForegroundColor Yellow

$processesToKill = @("vmware-vmx", "vmrun")

foreach ($processName in $processesToKill) {
    try {
        $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
        if ($processes) {
            Write-Host "Stopping $($processes.Count) $processName process(es)" -ForegroundColor Cyan
            $processes | Stop-Process -Force
        }
    } catch {
        Write-Host "No $processName processes to stop" -ForegroundColor Gray
    }
}

# 6. Restart VMware services
Write-Host "`n6. Restarting VMware services..." -ForegroundColor Yellow

foreach ($service in $vmwareServices) {
    try {
        $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -eq "Running") {
            Write-Host "Restarting service: $service" -ForegroundColor Cyan
            Restart-Service -Name $service -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Host "Could not restart service $service : $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== VMware VNC Fix Complete ===" -ForegroundColor Green
Write-Host "Please try running your Packer build again." -ForegroundColor Cyan
Write-Host "If the issue persists, try running VMware Workstation as Administrator." -ForegroundColor Yellow