#!/usr/bin/env python3
"""
Organize VMs - Move all created VMs to cloned-vms folder
"""

import os
import shutil
from pathlib import Path

def organize_vms_to_cloned_folder():
    print("=== Organizing VMs to cloned-vms folder ===")
    
    # Define paths
    templates_dir = Path(r'C:\Users\saads\OneDrive\Documents\Virtual Machines')
    cloned_vms_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms')
    
    # Ensure cloned-vms directory exists
    cloned_vms_dir.mkdir(exist_ok=True)
    
    # List of VMs to move (exclude templates that should stay as templates)
    vms_to_move = [
        'CentOS 7 64-bit',
        'Clone of Ubuntu 64-bit (3)',
        'nutanix',
        'Ubuntu 64-bit',
        'Ubuntu 64-bit (2)',
        # Note: We'll keep 'Ubuntu 64-bit (3)' and 'Windows Server 2019' as templates
    ]
    
    # VMs to keep as templates
    templates_to_keep = [
        'Ubuntu 64-bit (3)',
        'Windows Server 2019'
    ]
    
    print("Current VM distribution:")
    print(f"Templates directory: {templates_dir}")
    for vm_dir in templates_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print(f"\nCloned VMs directory: {cloned_vms_dir}")
    for vm_dir in cloned_vms_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print(f"\nProposed organization:")
    print("VMs to move to cloned-vms:")
    for vm_name in vms_to_move:
        vm_path = templates_dir / vm_name
        if vm_path.exists():
            print(f"  ✓ {vm_name}")
        else:
            print(f"  ✗ {vm_name} (not found)")
    
    print("VMs to keep as templates:")
    for vm_name in templates_to_keep:
        vm_path = templates_dir / vm_name
        if vm_path.exists():
            print(f"  ✓ {vm_name}")
        else:
            print(f"  ✗ {vm_name} (not found)")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with moving VMs? (y/N): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    print("\nMoving VMs...")
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
    
    print(f"\n=== Organization Complete ===")
    print(f"Moved {moved_count} VMs to cloned-vms folder")
    
    # Show final distribution
    print("\nFinal VM distribution:")
    print(f"Templates directory ({templates_dir}):")
    for vm_dir in templates_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print(f"\nCloned VMs directory ({cloned_vms_dir}):")
    for vm_dir in cloned_vms_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    print("\n=== Recommendations ===")
    print("1. Test VM listing with: python -c \"from hypervisor_manager import HypervisorManager; hm = HypervisorManager(); vms = hm.list_vms(); print(f'Total VMs: {len(vms)}')\"")
    print("2. Restart Flask app to refresh VM cache")
    print("3. Test POST method to ensure everything works")

def show_current_organization():
    """Show current VM organization without making changes"""
    print("=== Current VM Organization ===")
    
    templates_dir = Path(r'C:\Users\saads\OneDrive\Documents\Virtual Machines')
    cloned_vms_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms')
    permanent_vms_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\permanent_vms')
    
    print(f"\n📁 Templates directory ({templates_dir}):")
    if templates_dir.exists():
        for vm_dir in templates_dir.iterdir():
            if vm_dir.is_dir():
                print(f"  - {vm_dir.name}")
    else:
        print("  (Directory not found)")
    
    print(f"\n📁 Cloned VMs directory ({cloned_vms_dir}):")
    if cloned_vms_dir.exists():
        for vm_dir in cloned_vms_dir.iterdir():
            if vm_dir.is_dir():
                print(f"  - {vm_dir.name}")
    else:
        print("  (Directory not found)")
    
    print(f"\n📁 Permanent VMs directory ({permanent_vms_dir}):")
    if permanent_vms_dir.exists():
        for vm_dir in permanent_vms_dir.iterdir():
            if vm_dir.is_dir():
                print(f"  - {vm_dir.name}")
    else:
        print("  (Directory empty)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        show_current_organization()
    else:
        show_current_organization()
        print("\n" + "="*50)
        organize_vms_to_cloned_folder()