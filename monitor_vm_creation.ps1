# Monitor VM Creation Location
Write-Host "=== Monitoring VM Creation Location ===" -ForegroundColor Green

$clonedVmsPath = "c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms"
$defaultVmwarePath = "C:\Users\saads\OneDrive\Documents\Virtual Machines"
$vmName = "test-20250904-161849"

Write-Host "Monitoring VM: $vmName"
Write-Host "Checking every 30 seconds for 5 minutes..."

for ($i = 1; $i -le 10; $i++) {
    Write-Host "`n--- Check $i/10 ---" -ForegroundColor Yellow
    
    # Check cloned-vms directory
    $vmInCloned = Test-Path "$clonedVmsPath\$vmName"
    Write-Host "VM in cloned-vms: $vmInCloned"
    
    # Check default VMware directory
    $vmInDefault = Test-Path "$defaultVmwarePath\$vmName"
    Write-Host "VM in default VMware: $vmInDefault"
    
    # List all directories in both locations
    Write-Host "Cloned VMs directory contents:"
    Get-ChildItem -Path $clonedVmsPath -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
    
    Write-Host "Default VMware directory contents (recent):"
    Get-ChildItem -Path $defaultVmwarePath -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { 
        Write-Host "  - $($_.Name) (modified: $($_.LastWriteTime))" 
    }
    
    if ($vmInCloned) {
        Write-Host "✅ SUCCESS: VM found in cloned-vms directory!" -ForegroundColor Green
        break
    } elseif ($vmInDefault) {
        Write-Host "⚠️  VM found in default directory - waiting for move..." -ForegroundColor Yellow
    } else {
        Write-Host "⏳ VM not yet visible - creation in progress..." -ForegroundColor Cyan
    }
    
    if ($i -lt 10) {
        Write-Host "Waiting 30 seconds..."
        Start-Sleep -Seconds 30
    }
}

Write-Host "`n=== Final Status ===" -ForegroundColor Green
$finalInCloned = Test-Path "$clonedVmsPath\$vmName"
$finalInDefault = Test-Path "$defaultVmwarePath\$vmName"

Write-Host "VM in cloned-vms: $finalInCloned"
Write-Host "VM in default VMware: $finalInDefault"

if ($finalInCloned) {
    Write-Host "✅ SUCCESS: VM creation location fix is working!" -ForegroundColor Green
} elseif ($finalInDefault) {
    Write-Host "❌ ISSUE: VM is still in default directory" -ForegroundColor Red
} else {
    Write-Host "⏳ VM creation may still be in progress" -ForegroundColor Yellow
}