#!/usr/bin/env python3
"""
Move VMs to cloned-vms folder automatically
"""

import os
import shutil
from pathlib import Path

def move_vms_to_cloned_folder():
    print("=== Moving VMs to cloned-vms folder ===")
    
    # Define paths
    templates_dir = Path(r'C:\Users\saads\OneDrive\Documents\Virtual Machines')
    cloned_vms_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms')
    
    # Ensure cloned-vms directory exists
    cloned_vms_dir.mkdir(exist_ok=True)
    
    # List of VMs to move (created VMs, not original templates)
    vms_to_move = [
        'CentOS 7 64-bit',
        'Clone of Ubuntu 64-bit (3)',
        'nutanix',
        'Ubuntu 64-bit',
        'Ubuntu 64-bit (2)',
    ]
    
    print("Moving VMs to cloned-vms folder...")
    moved_count = 0
    
    for vm_name in vms_to_move:
        source_path = templates_dir / vm_name
        dest_path = cloned_vms_dir / vm_name
        
        if source_path.exists():
            if dest_path.exists():
                print(f"  ⚠️  {vm_name} already exists in cloned-vms, skipping")
                continue
            
            try:
                print(f"  📁 Moving {vm_name}...")
                shutil.move(str(source_path), str(dest_path))
                print(f"  ✅ Moved {vm_name}")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Failed to move {vm_name}: {e}")
        else:
            print(f"  ⚠️  {vm_name} not found in templates directory")
    
    print(f"\n=== Move Complete ===")
    print(f"Moved {moved_count} VMs to cloned-vms folder")
    
    # Show final distribution
    print("\nFinal VM distribution:")
    print(f"Templates directory (kept as templates):")
    for vm_dir in templates_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print(f"\nCloned VMs directory (all created VMs):")
    for vm_dir in cloned_vms_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    return moved_count

if __name__ == "__main__":
    moved_count = move_vms_to_cloned_folder()
    
    if moved_count > 0:
        print(f"\n✅ Successfully moved {moved_count} VMs to cloned-vms folder")
        print("\nNext steps:")
        print("1. Restart Flask app to refresh VM cache")
        print("2. Test VM listing to verify all VMs are visible")
        print("3. Test POST method for VM creation")
    else:
        print("\n⚠️  No VMs were moved (they may already be in the correct location)")