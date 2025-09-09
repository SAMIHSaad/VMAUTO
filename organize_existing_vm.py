#!/usr/bin/env python3
"""
Standalone script to organize existing VM files.
This can be used to organize VMs that were created before the automation was implemented.
"""

import argparse
import sys
from pathlib import Path
from vm_organizer import VMOrganizer

def main():
    """Main function for the standalone VM organizer script."""
    parser = argparse.ArgumentParser(
        description="Organize existing VM files into structured directories"
    )
    parser.add_argument(
        "vm_name",
        help="Name of the VM to organize"
    )
    parser.add_argument(
        "--cpu",
        default="2",
        help="CPU count (default: 2)"
    )
    parser.add_argument(
        "--ram",
        default="2048",
        help="RAM in MB (default: 2048)"
    )
    parser.add_argument(
        "--ssd",
        default="20",
        help="SSD size in GB (default: 20)"
    )
    parser.add_argument(
        "--os-type",
        default="linux",
        help="Operating system type (default: linux)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory containing VM files (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    args = parser.parse_args()
    
    # Prepare VM configuration
    vm_config = {
        'vm_name': args.vm_name,
        'os_type': args.os_type,
        'cpu': args.cpu,
        'ram': args.ram,
        'ssd': args.ssd,
        'golden_image_path': 'N/A (existing VM)',
        'ip_address': 'N/A (existing VM)'
    }
    
    try:
        if args.dry_run:
            print(f"DRY RUN: Would organize VM '{args.vm_name}' with the following configuration:")
            for key, value in vm_config.items():
                print(f"  {key}: {value}")
            
            base_dir = Path(args.base_dir) if args.base_dir else Path.cwd()
            packer_output_dir = base_dir / f"output-{args.vm_name}"
            vm_output_dir = base_dir / f"{args.vm_name}_Output"
            
            print(f"\nWould look for VM files in: {packer_output_dir}")
            print(f"Would create organized directory: {vm_output_dir}")
            
            if packer_output_dir.exists():
                print(f"\nFound VM files:")
                for file_path in packer_output_dir.iterdir():
                    if file_path.is_file():
                        print(f"  - {file_path.name}")
            else:
                print(f"\nWarning: VM files directory not found: {packer_output_dir}")
            
            return 0
        
        # Create organizer and organize files
        organizer = VMOrganizer(args.base_dir)
        organized_dir = organizer.organize_vm_files(args.vm_name, vm_config)
        
        print(f"Successfully organized VM '{args.vm_name}'")
        print(f"Organized directory: {organized_dir}")
        print("\nNext steps:")
        print(f"1. Navigate to: {organized_dir}")
        print("2. Read the README.md file for instructions")
        print("3. Use the provided backup and snapshot scripts")
        print("4. Open the VM using the .vmx file in the vm_files directory")
        
        return 0
        
    except Exception as e:
        print(f"Error organizing VM '{args.vm_name}': {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())