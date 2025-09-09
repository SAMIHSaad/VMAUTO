# VM Manager PowerShell Script
# Comprehensive VM management tool for Windows PowerShell

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("create", "organize", "list", "backup", "cleanup", "help", "clone")]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$VMName,
    
    [string]$OSType = "linux",
    [string]$CPU = "2",
    [string]$RAM = "2048",
    [string]$SSD = "20",
    [string]$BaseDir = $PWD,
    [string]$SourceVMX,
    [switch]$NoOrganize,
    [switch]$Detailed
)

function Show-Help {
    Write-Host @"
VM Manager - Comprehensive VM Management Tool

USAGE:
    .\vm_manager.ps1 <command> [options]

COMMANDS:
    create <vm_name>    Create a new VM (using Packer)
    clone <vm_name>     Clone a VM from an existing .vmx file
    organize <vm_name>  Organize existing VM files
    list               List all organized VMs
    backup <vm_name>   Backup a VM
    cleanup            Clean up old output directories
    help               Show this help message

CREATE OPTIONS:
    -OSType <type>     Operating system type (default: linux)
    -CPU <count>       CPU count (default: 2)
    -RAM <mb>          RAM in MB (default: 2048)
    -SSD <gb>          SSD size in GB (default: 20)
    -NoOrganize        Skip automatic file organization

CLONE OPTIONS:
    -SourceVMX <path>  Absolute path to the source .vmx file (required)
    -CPU <count>       CPU count (default: 2)
    -RAM <mb>          RAM in MB (default: 2048)
    -SSD <gb>          SSD size in GB (Note: Resizing disk might require additional steps)
    -NoOrganize        Skip automatic file organization

ORGANIZE OPTIONS:
    -OSType <type>     Operating system type
    -CPU <count>       CPU count
    -RAM <mb>          RAM in MB
    -SSD <gb>          SSD size in GB

LIST OPTIONS:
    -Detailed          Show detailed VM information

GLOBAL OPTIONS:
    -BaseDir <path>    Base directory for operations (default: current directory)

EXAMPLES:
    .\vm_manager.ps1 create "MyUbuntuVM" -CPU 4 -RAM 4096
    .\vm_manager.ps1 clone "MyWinVM" -SourceVMX "C:\VMs\WinTemplate\WinTemplate.vmx" -RAM 4096
    .\vm_manager.ps1 organize "ExistingVM"
    .\vm_manager.ps1 list -Detailed
    .\vm_manager.ps1 backup "MyUbuntuVM"
    .\vm_manager.ps1 cleanup
"@
}

function Invoke-CreateVM {
    param(
        [string]$Name,
        [string]$OS,
        [string]$CPUCount,
        [string]$Memory,
        [string]$Storage,
        [bool]$AutoOrganize
    )
    
    Write-Host "Creating VM: $Name" -ForegroundColor Green
    
    try {
        # Use Python VM manager for the heavy lifting
        $pythonArgs = @(
            "vm_manager.py", "create", $Name,
            "--os-type", $OS,
            "--cpu", $CPUCount,
            "--ram", $Memory,
            "--ssd", $Storage,
            "--base-dir", $BaseDir
        )
        
        if (-not $AutoOrganize) {
            $pythonArgs += "--no-organize"
        }
        
        $result = & python $pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' created successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to create VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error creating VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-CloneVM {
    param(
        [string]$Name,
        [string]$SourceVMX,
        [string]$CPUCount,
        [string]$Memory,
        [string]$Storage,
        [bool]$AutoOrganize
    )
    
    Write-Host "Cloning VM: $Name from $SourceVMX" -ForegroundColor Green
    
    try {
        $pythonArgs = @(
            "vm_manager.py", "clone", $Name,
            "--source-vmx", $SourceVMX,
            "--cpu", $CPUCount,
            "--ram", $Memory,
            "--ssd", $Storage,
            "--base-dir", $BaseDir
        )
        
        if (-not $AutoOrganize) {
            $pythonArgs += "--no-organize"
        }
        
        $result = & python $pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' cloned successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to clone VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error cloning VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-OrganizeVM {
    param(
        [string]$Name,
        [hashtable]$Config = @{}
    )
    
    Write-Host "Organizing VM: $Name" -ForegroundColor Green
    
    try {
        $pythonArgs = @("vm_manager.py", "organize", $Name, "--base-dir", $BaseDir)
        
        if ($Config.ContainsKey("CPU")) { $pythonArgs += @("--cpu", $Config.CPU) }
        if ($Config.ContainsKey("RAM")) { $pythonArgs += @("--ram", $Config.RAM) }
        if ($Config.ContainsKey("SSD")) { $pythonArgs += @("--ssd", $Config.SSD) }
        if ($Config.ContainsKey("OSType")) { $pythonArgs += @("--os-type", $Config.OSType) }
        
        $result = & python $pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' organized successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to organize VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error organizing VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-ListVMs {
    param([bool]$ShowDetailed)
    
    Write-Host "Listing organized VMs..." -ForegroundColor Green
    
    try {
        $pythonArgs = @("vm_manager.py", "list", "--base-dir", $BaseDir)
        
        if ($ShowDetailed) {
            $pythonArgs += "--detailed"
        }
        
        & python $pythonArgs
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Host "Error listing VMs: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-BackupVM {
    param([string]$Name)
    
    Write-Host "Backing up VM: $Name" -ForegroundColor Green
    
    try {
        $result = & python "vm_manager.py" "backup" $Name "--base-dir" $BaseDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' backed up successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to backup VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error backing up VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-Cleanup {
    Write-Host "Cleaning up old output directories..." -ForegroundColor Green
    
    try {
        $result = & python "vm_manager.py" "cleanup" "--base-dir" $BaseDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Cleanup completed successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Cleanup failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error during cleanup: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "create" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for create command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $success = Invoke-CreateVM -Name $VMName -OS $OSType -CPUCount $CPU -Memory $RAM -Storage $SSD -AutoOrganize (-not $NoOrganize)
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "clone" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for clone command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        if (-not $SourceVMX) {
            Write-Host "Error: SourceVMX path is required for clone command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $success = Invoke-CloneVM -Name $VMName -SourceVMX $SourceVMX -CPUCount $CPU -Memory $RAM -Storage $SSD -AutoOrganize (-not $NoOrganize)
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "organize" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for organize command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $config = @{}
        if ($CPU -ne "2") { $config.CPU = $CPU }
        if ($RAM -ne "2048") { $config.RAM = $RAM }
        if ($SSD -ne "20") { $config.SSD = $SSD }
        if ($OSType -ne "linux") { $config.OSType = $OSType }
        
        $success = Invoke-OrganizeVM -Name $VMName -Config $config
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "list" {
        $success = Invoke-ListVMs -ShowDetailed $Detailed
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "backup" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for backup command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $success = Invoke-BackupVM -Name $VMName
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "cleanup" {
        $success = Invoke-Cleanup
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "help" {
        Show-Help
        exit 0
    }
    
    default {
        Write-Host "Error: Unknown command '$Command'" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

function Show-Help {
    Write-Host @"
VM Manager - Comprehensive VM Management Tool

USAGE:
    .\vm_manager.ps1 <command> [options]

COMMANDS:
    create <vm_name>    Create a new VM
    organize <vm_name>  Organize existing VM files
    list               List all organized VMs
    backup <vm_name>   Backup a VM
    cleanup            Clean up old output directories
    help               Show this help message

CREATE OPTIONS:
    -OSType <type>     Operating system type (default: linux)
    -CPU <count>       CPU count (default: 2)
    -RAM <mb>          RAM in MB (default: 2048)
    -SSD <gb>          SSD size in GB (default: 20)
    -NoOrganize        Skip automatic file organization

ORGANIZE OPTIONS:
    -OSType <type>     Operating system type
    -CPU <count>       CPU count
    -RAM <mb>          RAM in MB
    -SSD <gb>          SSD size in GB

LIST OPTIONS:
    -Detailed          Show detailed VM information

GLOBAL OPTIONS:
    -BaseDir <path>    Base directory for operations (default: current directory)

EXAMPLES:
    .\vm_manager.ps1 create "MyUbuntuVM" -CPU 4 -RAM 4096
    .\vm_manager.ps1 organize "ExistingVM"
    .\vm_manager.ps1 list -Detailed
    .\vm_manager.ps1 backup "MyUbuntuVM"
    .\vm_manager.ps1 cleanup
"@
}

function Invoke-CreateVM {
    param(
        [string]$Name,
        [string]$OS,
        [string]$CPUCount,
        [string]$Memory,
        [string]$Storage,
        [bool]$AutoOrganize
    )
    
    Write-Host "Creating VM: $Name" -ForegroundColor Green
    
    try {
        # Use Python VM manager for the heavy lifting
        $pythonArgs = @(
            "vm_manager.py", "create", $Name,
            "--os-type", $OS,
            "--cpu", $CPUCount,
            "--ram", $Memory,
            "--ssd", $Storage,
            "--base-dir", $BaseDir
        )
        
        if (-not $AutoOrganize) {
            $pythonArgs += "--no-organize"
        }
        
        $result = & python $pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' created successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to create VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error creating VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-OrganizeVM {
    param(
        [string]$Name,
        [hashtable]$Config = @{}
    )
    
    Write-Host "Organizing VM: $Name" -ForegroundColor Green
    
    try {
        $pythonArgs = @("vm_manager.py", "organize", $Name, "--base-dir", $BaseDir)
        
        if ($Config.ContainsKey("CPU")) { $pythonArgs += @("--cpu", $Config.CPU) }
        if ($Config.ContainsKey("RAM")) { $pythonArgs += @("--ram", $Config.RAM) }
        if ($Config.ContainsKey("SSD")) { $pythonArgs += @("--ssd", $Config.SSD) }
        if ($Config.ContainsKey("OSType")) { $pythonArgs += @("--os-type", $Config.OSType) }
        
        $result = & python $pythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' organized successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to organize VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error organizing VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-ListVMs {
    param([bool]$ShowDetailed)
    
    Write-Host "Listing organized VMs..." -ForegroundColor Green
    
    try {
        $pythonArgs = @("vm_manager.py", "list", "--base-dir", $BaseDir)
        
        if ($ShowDetailed) {
            $pythonArgs += "--detailed"
        }
        
        & python $pythonArgs
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Host "Error listing VMs: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-BackupVM {
    param([string]$Name)
    
    Write-Host "Backing up VM: $Name" -ForegroundColor Green
    
    try {
        $result = & python "vm_manager.py" "backup" $Name "--base-dir" $BaseDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "VM '$Name' backed up successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to backup VM '$Name'" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error backing up VM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-Cleanup {
    Write-Host "Cleaning up old output directories..." -ForegroundColor Green
    
    try {
        $result = & python "vm_manager.py" "cleanup" "--base-dir" $BaseDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Cleanup completed successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Cleanup failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error during cleanup: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "create" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for create command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $success = Invoke-CreateVM -Name $VMName -OS $OSType -CPUCount $CPU -Memory $RAM -Storage $SSD -AutoOrganize (-not $NoOrganize)
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "organize" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for organize command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $config = @{}
        if ($CPU -ne "2") { $config.CPU = $CPU }
        if ($RAM -ne "2048") { $config.RAM = $RAM }
        if ($SSD -ne "20") { $config.SSD = $SSD }
        if ($OSType -ne "linux") { $config.OSType = $OSType }
        
        $success = Invoke-OrganizeVM -Name $VMName -Config $config
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "list" {
        $success = Invoke-ListVMs -ShowDetailed $Detailed
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "backup" {
        if (-not $VMName) {
            Write-Host "Error: VM name is required for backup command" -ForegroundColor Red
            Show-Help
            exit 1
        }
        
        $success = Invoke-BackupVM -Name $VMName
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "cleanup" {
        $success = Invoke-Cleanup
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "help" {
        Show-Help
        exit 0
    }
    
    default {
        Write-Host "Error: Unknown command '$Command'" -ForegroundColor Red
        Show-Help
        exit 1
    }
}