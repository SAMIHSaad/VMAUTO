#!/usr/bin/env python3
"""
Rollback VM organization - Move VMs back to templates directory
"""

import os
import shutil
from pathlib import Path

def rollback_vm_organization():
    print("=== Rolling Back VM Organization ===")
    
    # Define paths
    templates_dir = Path(r'C:\Users\saads\OneDrive\Documents\Virtual Machines')
    cloned_vms_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms')
    
    # Ensure templates directory exists
    templates_dir.mkdir(exist_ok=True)
    
    # VMs to move back to templates (these were originally templates)
    vms_to_move_back = [
        'CentOS 7 64-bit',
        'Clone of Ubuntu 64-bit (3)',
        'nutanix',
        'Ubuntu 64-bit',
        'Ubuntu 64-bit (2)',
    ]
    
    # VMs to keep in cloned-vms (these were actually cloned)
    vms_to_keep_in_cloned = [
        'www',
        'za'
    ]
    
    print("Rolling back VM organization...")
    moved_count = 0
    
    for vm_name in vms_to_move_back:
        source_path = cloned_vms_dir / vm_name
        dest_path = templates_dir / vm_name
        
        if source_path.exists():
            if dest_path.exists():
                print(f"  ⚠️  {vm_name} already exists in templates, skipping")
                continue
            
            try:
                print(f"  📁 Moving {vm_name} back to templates...")
                shutil.move(str(source_path), str(dest_path))
                print(f"  ✅ Moved {vm_name} back")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Failed to move {vm_name}: {e}")
        else:
            print(f"  ⚠️  {vm_name} not found in cloned-vms directory")
    
    print(f"\n=== Rollback Complete ===")
    print(f"Moved {moved_count} VMs back to templates folder")
    
    # Show final distribution
    print("\nFinal VM distribution:")
    print(f"Templates directory ({templates_dir}):")
    for vm_dir in templates_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print(f"\nCloned VMs directory ({cloned_vms_dir}) - Only actual clones:")
    for vm_dir in cloned_vms_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    return moved_count

if __name__ == "__main__":
    moved_count = rollback_vm_organization()
    
    if moved_count > 0:
        print(f"\n✅ Successfully rolled back {moved_count} VMs to templates folder")
        print("\nNow the real issue can be fixed:")
        print("- Templates are in their correct location")
        print("- Only actual cloned VMs (www, za) remain in cloned-vms")
        print("- Need to fix where new VMs are created via web form")
    else:
        print("\n⚠️  No VMs were moved (they may already be in the correct location)")