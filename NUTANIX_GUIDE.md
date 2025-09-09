# Nutanix Support Guide

This guide explains how to configure and manage VMs on Nutanix via Prism v3 API using the new tools added to this repository.

## Overview
- nutanix_client.py: Minimal Prism v3 client (Python)
- nutanix_manager.py: CLI to list/create/power/delete VMs
- nutanix_manager.ps1: PowerShell wrapper for Windows users
- nutanix_config.example.json: Example configuration file
- PACKER_NUTANIX_TEMPLATE.pkr.hcl: Minimal Packer template (experimental)

## Prerequisites
- Nutanix Prism Central or Element with API access
- Python 3.9+
- `pip install requests`
- Optional: Packer (if using the Packer template)

## Configure
1. Copy config example:
   ```powershell
   Copy-Item "nutanix_config.example.json" "nutanix_config.json"
   ```
2. Edit `nutanix_config.json` with your Prism URL and credentials:
   ```json
   {
     "base_url": "https://PRISM:9440",
     "username": "admin",
     "password": "YOUR_PASSWORD",
     "verify_ssl": false,
     "project_uuid": null
   }
   ```

## Discover UUIDs
- Clusters:
  ```bash
  python -c "from nutanix_client import NutanixClient; import json; c=NutanixClient('https://PRISM:9440','admin','pwd',False); print(json.dumps(c.list_clusters(), indent=2))"
  ```
- Subnets:
  ```bash
  python -c "from nutanix_client import NutanixClient; import json; c=NutanixClient('https://PRISM:9440','admin','pwd',False); print(json.dumps(c.list_subnets(), indent=2))"
  ```
- Images:
  ```bash
  python -c "from nutanix_client import NutanixClient; import json; c=NutanixClient('https://PRISM:9440','admin','pwd',False); print(json.dumps(c.list_images(), indent=2))"
  ```

## Usage (CLI)
- List VMs:
  ```powershell
  python .\nutanix_manager.py --config .\nutanix_config.json list
  ```
- Create VM from image:
  ```powershell
  python .\nutanix_manager.py --config .\nutanix_config.json create "MyNutanixVM" `
    --cpu 2 --ram 4096 `
    --cluster-uuid <CLUSTER_UUID> `
    --subnet-uuid <SUBNET_UUID> `
    --image-uuid <IMAGE_UUID> `
    --cores-per-vcpu 1 --boot-type UEFI `
    --user-data .\http\user-data
  ```
- Power control:
  ```powershell
  python .\nutanix_manager.py --config .\nutanix_config.json power <VM_UUID> --state ON --wait
  ```
- Delete VM:
  ```powershell
  python .\nutanix_manager.py --config .\nutanix_config.json delete <VM_UUID>
  ```

## Usage (PowerShell Wrapper)
```powershell
# List
.\nutanix_manager.ps1 -Command list
# Create
.\nutanix_manager.ps1 -Command create -Name "MyNutanixVM" -CPU 2 -RAM 4096 -ClusterUUID <CLUSTER> -SubnetUUID <SUBNET> -ImageUUID <IMAGE> -UserData ".\http\user-data"
# Power ON
.\nutanix_manager.ps1 -Command power -UUID <VM_UUID> -State ON -Wait
# Delete
.\nutanix_manager.ps1 -Command delete -UUID <VM_UUID>
```

## Notes
- Ensure your image has valid OS credentials (e.g., ubuntu/ubuntu) or inject cloud-init user-data.
- SSL verification can be disabled via `verify_ssl: false` for lab environments.
- The Packer plugin reference is indicative; verify the correct Nutanix plugin and fields for your environment.

## Integration Ideas
- Add Nutanix as a provider alongside VMware in vm_manager.py (feature flag `--provider nutanix|vmware`).
- Reuse vm_organizer.py to post-process Nutanix VM metadata and generate backup/snapshot scripts (Nutanix-native or AHV equivalents).
- Map ip_manager.py allocations to Nutanix NIC configs if using static addressing.