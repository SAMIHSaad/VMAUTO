param(
  [string]$ConfigPath = "c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\nutanix_config.json",
  [Parameter(Mandatory=$true)][ValidateSet('list','create','power','delete')] [string]$Command,
  [string]$Name,
  [int]$CPU = 2,
  [int]$RAM = 4096,
  [string]$ClusterUUID,
  [string]$SubnetUUID,
  [string]$ImageUUID,
  [int]$CoresPerVCPU = 1,
  [ValidateSet('UEFI','LEGACY')] [string]$BootType = 'UEFI',
  [string]$UserData,
  [string]$UUID,
  [ValidateSet('ON','OFF','RESET','SUSPEND')] [string]$State,
  [switch]$Wait
)

# Run the Python CLI with matching arguments
$py = "python"
$base = "c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\nutanix_manager.py"

if ($Command -eq 'list') {
  & $py $base --config $ConfigPath list
}
elseif ($Command -eq 'create') {
  if (-not $Name -or -not $ClusterUUID -or -not $SubnetUUID -or -not $ImageUUID) { throw "Missing required args for create" }
  $args = @(
    "--config", $ConfigPath,
    "create", $Name,
    "--cpu", $CPU,
    "--ram", $RAM,
    "--cluster-uuid", $ClusterUUID,
    "--subnet-uuid", $SubnetUUID,
    "--image-uuid", $ImageUUID,
    "--cores-per-vcpu", $CoresPerVCPU,
    "--boot-type", $BootType
  )
  if ($UserData) { $args += @("--user-data", $UserData) }
  & $py $base $args
}
elseif ($Command -eq 'power') {
  if (-not $UUID -or -not $State) { throw "Missing required args for power" }
  $args = @("--config", $ConfigPath, "power", $UUID, "--state", $State)
  if ($Wait) { $args += "--wait" }
  & $py $base $args
}
elseif ($Command -eq 'delete') {
  if (-not $UUID) { throw "Missing UUID for delete" }
  & $py $base --config $ConfigPath delete $UUID
}