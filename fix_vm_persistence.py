#!/usr/bin/env python3
"""
VM Persistence Fix and Diagnostic Tool

This script helps diagnose and fix VM persistence issues where VMs lose data after power off or restart.

Common causes:
1. VMs running from live ISO instead of being properly installed
2. VMX files missing persistence settings
3. Disk mode set to non-persistent or dependent
4. CD-ROM/ISO still attached and set as primary boot device

Usage:
    python fix_vm_persistence.py --check [vm_name]     # Check specific VM or all VMs
    python fix_vm_persistence.py --fix [vm_name]       # Fix specific VM or all VMs
    python fix_vm_persistence.py --test vm_name        # Test VM persistence
    python fix_vm_persistence.py --organize vm_name    # Organize VM files properly
"""

import argparse
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent

class VMPersistenceFixer:
    """Tool to diagnose and fix VM persistence issues"""
    
    def __init__(self):
        self.vmrun_path = r'C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe'
        self.base_dir = BASE_DIR
        
    def find_all_vmx_files(self) -> List[Path]:
        """Find all VMX files in the project"""
        vmx_files = []
        
        # Search in common directories
        search_dirs = [
            self.base_dir / "cloned-vms",
            self.base_dir / "permanent_vms",
            self.base_dir / "output-ubuntu",
            self.base_dir / "output-windows",
            self.base_dir / "output-centos",
            self.base_dir / "output-clone"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                vmx_files.extend(search_dir.rglob("*.vmx"))
        
        # Also search for *_Output directories
        for output_dir in self.base_dir.glob("*_Output"):
            if output_dir.is_dir():
                vmx_files.extend(output_dir.rglob("*.vmx"))
        
        return list(set(vmx_files))  # Remove duplicates
    
    def find_vmx_by_name(self, vm_name: str) -> Optional[Path]:
        """Find VMX file by VM name"""
        all_vmx = self.find_all_vmx_files()
        
        for vmx_path in all_vmx:
            if vmx_path.stem == vm_name or vm_name in vmx_path.name:
                return vmx_path
        
        return None
    
    def check_vm_persistence(self, vmx_path: Path) -> Dict[str, any]:
        """Check VM persistence settings and return diagnostic info"""
        if not vmx_path.exists():
            return {"error": f"VMX file not found: {vmx_path}"}
        
        try:
            content = vmx_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Parse VMX settings
            settings = {}
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    settings[key.strip()] = value.strip().strip('"')
            
            # Check persistence settings
            issues = []
            warnings = []
            
            # Check disk mode
            disk_mode = settings.get('scsi0:0.mode', 'persistent')
            if disk_mode != 'independent-persistent':
                issues.append(f"Disk mode is '{disk_mode}', should be 'independent-persistent'")
            
            # Check redo log
            redo_log = settings.get('scsi0:0.redo', '')
            if redo_log and redo_log != '""' and redo_log != "''":
                issues.append(f"Redo log is set to '{redo_log}', should be empty")
            
            # Check CD-ROM devices
            cdrom_devices = ['ide1:0', 'sata0:1', 'ide0:1']
            for device in cdrom_devices:
                if settings.get(f'{device}.present', 'FALSE').upper() == 'TRUE':
                    if settings.get(f'{device}.deviceType', '') == 'cdrom-image':
                        warnings.append(f"CD-ROM device {device} is present and may contain ISO")
            
            # Check boot order
            boot_order = settings.get('bios.bootOrder', settings.get('bios.bootorder', ''))
            if boot_order and not boot_order.startswith('hdd'):
                warnings.append(f"Boot order is '{boot_order}', should start with 'hdd'")
            
            # Check if VM is running
            is_running = self.is_vm_running(vmx_path)
            
            return {
                "vmx_path": str(vmx_path),
                "vm_name": vmx_path.stem,
                "is_running": is_running,
                "disk_mode": disk_mode,
                "redo_log": redo_log,
                "boot_order": boot_order,
                "issues": issues,
                "warnings": warnings,
                "settings": settings
            }
            
        except Exception as e:
            return {"error": f"Error reading VMX file: {e}"}
    
    def is_vm_running(self, vmx_path: Path) -> bool:
        """Check if VM is currently running"""
        try:
            result = subprocess.run([self.vmrun_path, 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return str(vmx_path) in result.stdout
        except Exception:
            pass
        return False
    
    def fix_vm_persistence(self, vmx_path: Path, dry_run: bool = False) -> bool:
        """Fix VM persistence settings"""
        if not vmx_path.exists():
            print(f"❌ VMX file not found: {vmx_path}")
            return False
        
        try:
            content = vmx_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Settings to fix
            fixes = {
                'scsi0:0.mode': 'independent-persistent',
                'scsi0:0.redo': '',
                'scsi0:0.writeThrough': 'TRUE',
                'ide1:0.present': 'FALSE',
                'ide1:0.startConnected': 'FALSE',
                'ide1:0.deviceType': 'cdrom-raw',
                'ide1:0.fileName': '',
                'sata0:1.present': 'FALSE',
                'sata0:1.startConnected': 'FALSE',
                'ide0:1.present': 'FALSE',
                'ide0:1.startConnected': 'FALSE',
                'ide0:1.deviceType': 'cdrom-raw',
                'ide0:1.fileName': '',
                'bios.bootOrder': 'hdd,cdrom',
                'bios.bootorder': 'hdd,cdrom'
            }
            
            # Apply fixes
            changed = False
            for key, value in fixes.items():
                lines, line_changed = self._set_or_add_vmx_setting(lines, key, value)
                if line_changed:
                    changed = True
            
            if changed:
                if not dry_run:
                    # Backup original file
                    backup_path = vmx_path.with_suffix('.vmx.backup')
                    vmx_path.rename(backup_path)
                    
                    # Write fixed file
                    vmx_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
                    print(f"✅ Fixed persistence settings for {vmx_path.name}")
                    print(f"   Backup saved as {backup_path.name}")
                else:
                    print(f"🔧 Would fix persistence settings for {vmx_path.name}")
                return True
            else:
                print(f"✅ {vmx_path.name} already has correct persistence settings")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing {vmx_path.name}: {e}")
            return False
    
    def _set_or_add_vmx_setting(self, lines: List[str], key: str, value: str) -> Tuple[List[str], bool]:
        """Set or add a VMX setting"""
        target_line = f'{key} = "{value}"'
        key_lower = key.lower()
        
        # Find existing setting
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.lower().startswith(key_lower + ' ') and '=' in line_stripped:
                if lines[i] != target_line:
                    lines[i] = target_line
                    return lines, True
                return lines, False
        
        # Setting not found, add it
        lines.append(target_line)
        return lines, True
    
    def test_vm_persistence(self, vm_name: str) -> bool:
        """Test VM persistence by creating a test file and restarting"""
        vmx_path = self.find_vmx_by_name(vm_name)
        if not vmx_path:
            print(f"❌ VM '{vm_name}' not found")
            return False
        
        print(f"🧪 Testing persistence for VM: {vm_name}")
        
        # Check if VM is running
        if not self.is_vm_running(vmx_path):
            print("   Starting VM...")
            result = subprocess.run([self.vmrun_path, 'start', str(vmx_path), 'nogui'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to start VM: {result.stderr}")
                return False
            
            # Wait for VM to boot
            print("   Waiting for VM to boot...")
            time.sleep(30)
        
        # Create test file via SSH (if possible) or VMware tools
        test_file_path = "/tmp/persistence_test.txt"
        test_content = f"Persistence test created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            # Try to create test file using vmrun
            result = subprocess.run([
                self.vmrun_path, 'runProgramInGuest', str(vmx_path),
                '/bin/bash', '-c', f'echo "{test_content}" > {test_file_path}'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print("⚠️  Could not create test file automatically")
                print("   Please manually create a test file in the VM and restart it")
                return False
            
            print(f"   Created test file: {test_file_path}")
            
            # Restart VM
            print("   Restarting VM...")
            subprocess.run([self.vmrun_path, 'reset', str(vmx_path), 'soft'],
                         capture_output=True, text=True)
            
            # Wait for restart
            time.sleep(45)
            
            # Check if test file still exists
            result = subprocess.run([
                self.vmrun_path, 'runProgramInGuest', str(vmx_path),
                '/bin/cat', test_file_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and test_content in result.stdout:
                print("✅ Persistence test PASSED - data survived restart")
                return True
            else:
                print("❌ Persistence test FAILED - data was lost after restart")
                return False
                
        except Exception as e:
            print(f"❌ Error during persistence test: {e}")
            return False
    
    def organize_vm(self, vm_name: str) -> bool:
        """Organize VM files using the VM organizer"""
        try:
            from vm_organizer import VMOrganizer
            
            organizer = VMOrganizer(str(self.base_dir))
            vm_config = {
                'name': vm_name,
                'cpu': 2,
                'ram': 2048,
                'disk': 20,
                'os_type': 'linux'
            }
            
            result_path = organizer.organize_vm_files(vm_name, vm_config)
            print(f"✅ VM organized successfully: {result_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error organizing VM: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="VM Persistence Fix and Diagnostic Tool")
    parser.add_argument('--check', nargs='?', const='all', help='Check VM persistence (specific VM or all)')
    parser.add_argument('--fix', nargs='?', const='all', help='Fix VM persistence (specific VM or all)')
    parser.add_argument('--test', help='Test VM persistence by creating test file and restarting')
    parser.add_argument('--organize', help='Organize VM files properly')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    if not any([args.check, args.fix, args.test, args.organize]):
        parser.print_help()
        return 1
    
    fixer = VMPersistenceFixer()
    
    if args.check:
        print("🔍 Checking VM persistence settings...\n")
        
        if args.check == 'all':
            vmx_files = fixer.find_all_vmx_files()
            if not vmx_files:
                print("❌ No VMX files found")
                return 1
        else:
            vmx_path = fixer.find_vmx_by_name(args.check)
            if not vmx_path:
                print(f"❌ VM '{args.check}' not found")
                return 1
            vmx_files = [vmx_path]
        
        for vmx_path in vmx_files:
            result = fixer.check_vm_persistence(vmx_path)
            
            if 'error' in result:
                print(f"❌ {vmx_path.name}: {result['error']}")
                continue
            
            print(f"📋 VM: {result['vm_name']}")
            print(f"   Path: {result['vmx_path']}")
            print(f"   Running: {'Yes' if result['is_running'] else 'No'}")
            print(f"   Disk Mode: {result['disk_mode']}")
            print(f"   Boot Order: {result['boot_order']}")
            
            if result['issues']:
                print("   ❌ Issues:")
                for issue in result['issues']:
                    print(f"      - {issue}")
            
            if result['warnings']:
                print("   ⚠️  Warnings:")
                for warning in result['warnings']:
                    print(f"      - {warning}")
            
            if not result['issues'] and not result['warnings']:
                print("   ✅ No issues found")
            
            print()
    
    if args.fix:
        print("🔧 Fixing VM persistence settings...\n")
        
        if args.fix == 'all':
            vmx_files = fixer.find_all_vmx_files()
            if not vmx_files:
                print("❌ No VMX files found")
                return 1
        else:
            vmx_path = fixer.find_vmx_by_name(args.fix)
            if not vmx_path:
                print(f"❌ VM '{args.fix}' not found")
                return 1
            vmx_files = [vmx_path]
        
        fixed_count = 0
        for vmx_path in vmx_files:
            if fixer.fix_vm_persistence(vmx_path, args.dry_run):
                fixed_count += 1
        
        print(f"\n✅ Fixed {fixed_count}/{len(vmx_files)} VMs")
        
        if not args.dry_run and fixed_count > 0:
            print("\n⚠️  Important: Restart any running VMs for changes to take effect")
    
    if args.test:
        print("🧪 Testing VM persistence...\n")
        success = fixer.test_vm_persistence(args.test)
        return 0 if success else 1
    
    if args.organize:
        print("📁 Organizing VM files...\n")
        success = fixer.organize_vm(args.organize)
        return 0 if success else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())