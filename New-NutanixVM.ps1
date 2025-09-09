<#
.SYNOPSIS
    Creates a new virtual machine on Nutanix AHV using REST APIs.
.DESCRIPTION
    This script automates the process of creating a virtual machine on Nutanix AHV.
    It uses the Nutanix REST APIs to create, configure, and start the VM.
.PARAMETER VMName
    The name for the new virtual machine.
.PARAMETER CPU
    The number of CPU cores for the new VM.
.PARAMETER RAM
    The amount of RAM in megabytes (MB) for the new VM.
.PARAMETER DiskSize
    The size of the primary virtual disk in gigabytes (GB).
.PARAMETER ClusterName
    The name of the Nutanix cluster where the VM will be created.
.PARAMETER NetworkName
    The name of the network to connect the VM to.
.PARAMETER PrismCentralIP
    The IP address of Prism Central.
.PARAMETER Username
    The username for Nutanix authentication.
.PARAMETER Password
    The password for Nutanix authentication.
.PARAMETER Template
    Optional template name to clone from.
.EXAMPLE
    .\New-NutanixVM.ps1 -VMName "MyUbuntuVM" -CPU 4 -RAM 4096 -DiskSize 100 -ClusterName "MyCluster" -NetworkName "VM Network" -PrismCentralIP "10.0.0.100" -Username "admin" -Password "password"
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$VMName,
    
    [Parameter(Mandatory=$false)]
    [int]$CPU = 2,
    
    [Parameter(Mandatory=$false)]
    [int]$RAM = 2048,
    
    [Parameter(Mandatory=$false)]
    [int]$DiskSize = 20,
    
    [Parameter(Mandatory=$true)]
    [string]$ClusterName,
    
    [Parameter(Mandatory=$true)]
    [string]$NetworkName,
    
    [Parameter(Mandatory=$true)]
    [string]$PrismCentralIP,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$true)]
    [string]$Password,
    
    [Parameter(Mandatory=$false)]
    [string]$Template = "",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 9440
)

$ErrorActionPreference = 'Stop'

# Disable SSL certificate validation
if (-not ([System.Management.Automation.PSTypeName]'TrustAllCertsPolicy').Type) {
    Add-Type @"
        using System.Net;
        using System.Security.Cryptography.X509Certificates;
        public class TrustAllCertsPolicy : ICertificatePolicy {
            public bool CheckValidationResult(
                ServicePoint srvPoint, X509Certificate certificate,
                WebRequest request, int certificateProblem) {
                return true;
            }
        }
"@
    [System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
}

# Set TLS version
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# Base URL for Nutanix API
$BaseURL = "https://${PrismCentralIP}:${Port}/api/nutanix/v3"

# Create authentication header
$AuthString = "${Username}:${Password}"
$AuthBytes = [System.Text.Encoding]::ASCII.GetBytes($AuthString)
$AuthBase64 = [System.Convert]::ToBase64String($AuthBytes)
$Headers = @{
    'Authorization' = "Basic $AuthBase64"
    'Content-Type' = 'application/json'
    'Accept' = 'application/json'
}

function Invoke-NutanixAPI {
    param(
        [string]$Method,
        [string]$Uri,
        [object]$Body = $null
    )
    
    try {
        $params = @{
            Method = $Method
            Uri = $Uri
            Headers = $Headers
            TimeoutSec = 300
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Error "API call failed: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Error "Response: $responseBody"
        }
        throw
    }
}

function Get-ClusterUUID {
    param([string]$ClusterName)
    
    Write-Host "Getting cluster UUID for '$ClusterName'..."
    
    $body = @{
        kind = "cluster"
        filter = "name==$ClusterName"
        length = 1
    }
    
    $response = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/clusters/list" -Body $body
    
    if ($response.entities.Count -eq 0) {
        throw "Cluster '$ClusterName' not found"
    }
    
    return $response.entities[0].metadata.uuid
}

function Get-NetworkUUID {
    param([string]$NetworkName)
    
    Write-Host "Getting network UUID for '$NetworkName'..."
    
    $body = @{
        kind = "subnet"
        filter = "name==$NetworkName"
        length = 1
    }
    
    $response = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/subnets/list" -Body $body
    
    if ($response.entities.Count -eq 0) {
        throw "Network '$NetworkName' not found"
    }
    
    return $response.entities[0].metadata.uuid
}

function Get-TemplateUUID {
    param([string]$TemplateName)
    
    if ([string]::IsNullOrEmpty($TemplateName)) {
        return $null
    }
    
    Write-Host "Getting template UUID for '$TemplateName'..."
    
    $body = @{
        kind = "image"
        filter = "name==$TemplateName"
        length = 1
    }
    
    $response = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/images/list" -Body $body
    
    if ($response.entities.Count -eq 0) {
        Write-Warning "Template '$TemplateName' not found, creating VM from scratch"
        return $null
    }
    
    return $response.entities[0].metadata.uuid
}

function Wait-ForTask {
    param([string]$TaskUUID)
    
    Write-Host "Waiting for task $TaskUUID to complete..."
    
    $timeout = 600 # 10 minutes
    $elapsed = 0
    $interval = 5
    
    while ($elapsed -lt $timeout) {
        try {
            $task = Invoke-NutanixAPI -Method GET -Uri "$BaseURL/tasks/$TaskUUID"
            
            $status = $task.status
            Write-Host "Task status: $status"
            
            if ($status -eq "SUCCEEDED") {
                Write-Host "Task completed successfully" -ForegroundColor Green
                return $true
            }
            elseif ($status -eq "FAILED") {
                Write-Error "Task failed: $($task.error_detail)"
                return $false
            }
            
            Start-Sleep -Seconds $interval
            $elapsed += $interval
        }
        catch {
            Write-Warning "Error checking task status: $($_.Exception.Message)"
            Start-Sleep -Seconds $interval
            $elapsed += $interval
        }
    }
    
    Write-Error "Task timed out after $timeout seconds"
    return $false
}

function Create-NutanixVM {
    Write-Host "Creating VM '$VMName' on Nutanix cluster '$ClusterName'..." -ForegroundColor Yellow
    
    # Get required UUIDs
    $clusterUUID = Get-ClusterUUID -ClusterName $ClusterName
    $networkUUID = Get-NetworkUUID -NetworkName $NetworkName
    $templateUUID = Get-TemplateUUID -TemplateName $Template
    
    Write-Host "Cluster UUID: $clusterUUID"
    Write-Host "Network UUID: $networkUUID"
    if ($templateUUID) {
        Write-Host "Template UUID: $templateUUID"
    }
    
    # Create VM specification
    $vmSpec = @{
        spec = @{
            name = $VMName
            description = "VM created via PowerShell script - Auto-Creation-VM"
            resources = @{
                power_state = "ON"
                num_vcpus_per_socket = $CPU
                num_sockets = 1
                memory_size_mib = $RAM
                disk_list = @(
                    @{
                        device_properties = @{
                            device_type = "DISK"
                            disk_address = @{
                                device_index = 0
                                adapter_type = "SCSI"
                            }
                        }
                        disk_size_mib = $DiskSize * 1024
                    }
                )
                nic_list = @(
                    @{
                        nic_type = "NORMAL_NIC"
                        subnet_reference = @{
                            kind = "subnet"
                            uuid = $networkUUID
                        }
                    }
                )
            }
            cluster_reference = @{
                kind = "cluster"
                uuid = $clusterUUID
            }
        }
        api_version = "3.1.0"
        metadata = @{
            kind = "vm"
            categories = @{
                Environment = @("Auto-Creation-VM")
                CreatedBy = @("PowerShell-Script")
            }
        }
    }
    
    # If template is specified, add it as data source
    if ($templateUUID) {
        $vmSpec.spec.resources.disk_list[0].data_source_reference = @{
            kind = "image"
            uuid = $templateUUID
        }
    }
    
    # Create the VM
    Write-Host "Sending VM creation request..."
    $response = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/vms" -Body $vmSpec
    
    if ($response.status.execution_context.task_uuid) {
        $taskUUID = $response.status.execution_context.task_uuid
        Write-Host "VM creation task started: $taskUUID"
        
        $success = Wait-ForTask -TaskUUID $taskUUID
        
        if ($success) {
            Write-Host "VM '$VMName' created successfully on Nutanix!" -ForegroundColor Green
            
            # Get VM information
            Start-Sleep -Seconds 5
            $vmListBody = @{
                kind = "vm"
                filter = "vm_name==$VMName"
                length = 1
            }
            
            try {
                $vmList = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/vms/list" -Body $vmListBody
                if ($vmList.entities.Count -gt 0) {
                    $vm = $vmList.entities[0]
                    Write-Host ""
                    Write-Host "VM Details:" -ForegroundColor Cyan
                    Write-Host "  Name: $($vm.spec.name)"
                    Write-Host "  UUID: $($vm.metadata.uuid)"
                    Write-Host "  State: $($vm.spec.resources.power_state)"
                    Write-Host "  CPU: $($vm.spec.resources.num_vcpus_per_socket)"
                    Write-Host "  RAM: $($vm.spec.resources.memory_size_mib) MB"
                    Write-Host "  Cluster: $ClusterName"
                    
                    # Try to get IP address
                    if ($vm.status.resources.nic_list -and $vm.status.resources.nic_list[0].ip_endpoint_list) {
                        $ipAddress = $vm.status.resources.nic_list[0].ip_endpoint_list[0].ip
                        Write-Host "  IP Address: $ipAddress"
                    }
                }
            }
            catch {
                Write-Warning "Could not retrieve VM details: $($_.Exception.Message)"
            }
            
            return $true
        }
        else {
            Write-Error "VM creation failed"
            return $false
        }
    }
    else {
        Write-Error "No task UUID returned from VM creation request"
        return $false
    }
}

# Main execution
try {
    Write-Host "Starting Nutanix VM creation process..." -ForegroundColor Cyan
    Write-Host "VM Name: $VMName"
    Write-Host "CPU: $CPU cores"
    Write-Host "RAM: $RAM MB"
    Write-Host "Disk: $DiskSize GB"
    Write-Host "Cluster: $ClusterName"
    Write-Host "Network: $NetworkName"
    Write-Host "Prism Central: $PrismCentralIP"
    if ($Template) {
        Write-Host "Template: $Template"
    }
    Write-Host ""
    
    # Test connection to Prism Central
    Write-Host "Testing connection to Prism Central..."
    $testBody = @{ kind = "cluster" }
    $testResponse = Invoke-NutanixAPI -Method POST -Uri "$BaseURL/clusters/list" -Body $testBody
    Write-Host "Connection successful!" -ForegroundColor Green
    
    # Create the VM
    $success = Create-NutanixVM
    
    if ($success) {
        Write-Host ""
        Write-Host "VM creation completed successfully!" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host ""
        Write-Host "VM creation failed!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack Trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}