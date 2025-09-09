#!/usr/bin/env python3
"""
Fix VM creation location - Move VMs from output directories to cloned-vms
"""

import os
import shutil
from pathlib import Path

def fix_vm_creation_location():
    print("=== Fixing VM Creation Location ===")
    
    # Define paths
    base_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM')
    cloned_vms_dir = base_dir / 'cloned-vms'
    
    # Ensure cloned-vms directory exists
    cloned_vms_dir.mkdir(exist_ok=True)
    
    # Find all output directories that contain VMs
    output_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.startswith('output-'):
            output_dirs.append(item)
    
    print(f"Found {len(output_dirs)} output directories:")
    for output_dir in output_dirs:
        print(f"  - {output_dir.name}")
    
    moved_count = 0
    
    for output_dir in output_dirs:
        print(f"\nProcessing {output_dir.name}...")
        
        # Look for VM files in the output directory
        vmx_files = list(output_dir.glob('*.vmx'))
        
        if vmx_files:
            for vmx_file in vmx_files:
                vm_name = vmx_file.stem  # Get filename without extension
                print(f"  Found VM: {vm_name}")
                
                # Create destination directory in cloned-vms
                dest_dir = cloned_vms_dir / vm_name
                
                if dest_dir.exists():
                    print(f"    ⚠️  VM {vm_name} already exists in cloned-vms, skipping")
                    continue
                
                try:
                    print(f"    📁 Moving {vm_name} to cloned-vms...")
                    
                    # Move the entire output directory to cloned-vms with the VM name
                    shutil.move(str(output_dir), str(dest_dir))
                    print(f"    ✅ Moved {vm_name} to cloned-vms")
                    moved_count += 1
                    break  # Only process one VM per output directory
                    
                except Exception as e:
                    print(f"    ❌ Failed to move {vm_name}: {e}")
        else:
            print(f"  No VM files found in {output_dir.name}")
    
    print(f"\n=== Fix Complete ===")
    print(f"Moved {moved_count} VMs from output directories to cloned-vms")
    
    # Show current cloned-vms content
    print(f"\nCurrent cloned-vms directory content:")
    for vm_dir in cloned_vms_dir.iterdir():
        if vm_dir.is_dir():
            print(f"  - {vm_dir.name}")
    
    return moved_count

def show_current_status():
    """Show current VM organization status"""
    print("=== Current VM Organization Status ===")
    
    base_dir = Path(r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM')
    templates_dir = Path(r'C:\Users\saads\OneDrive\Documents\Virtual Machines')
    cloned_vms_dir = base_dir / 'cloned-vms'
    
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
    
    print(f"\n📁 Output directories (should be empty after fix):")
    output_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.startswith('output-'):
            output_dirs.append(item)
    
    if output_dirs:
        for output_dir in output_dirs:
            print(f"  - {output_dir.name}")
    else:
        print("  (No output directories found)")

if __name__ == "__main__":
    show_current_status()
    print("\n" + "="*50)
    moved_count = fix_vm_creation_location()
    
    if moved_count > 0:
        print(f"\n✅ Successfully fixed VM creation location!")
        print(f"Moved {moved_count} VMs to cloned-vms folder")
        print("\nNow all VMs created through the web form will go to cloned-vms folder")
    else:
        print("\n⚠️  No VMs needed to be moved")
    
    print("\n" + "="*50)
    show_current_status()