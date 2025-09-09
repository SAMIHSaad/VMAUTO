#!/usr/bin/env python3
"""
System Status Script
Provides an overview of the VM automation system status.
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_system_status():
    """Check and display system status."""
    base_dir = Path.cwd()
    
    print("=" * 60)
    print("VM AUTOMATION SYSTEM STATUS")
    print("=" * 60)
    
    # Check core files
    print("\n📁 CORE FILES:")
    core_files = [
        'app.py',
        'vm_organizer.py',
        'vm_manager.py',
        'vm_manager.ps1',
        'build.pkr.hcl',
        'ip_manager.py'
    ]
    
    for file in core_files:
        file_path = base_dir / file
        status = "✅ EXISTS" if file_path.exists() else "❌ MISSING"
        print(f"  {file:<20} {status}")
    
    # Check organized VMs
    print("\n🖥️  ORGANIZED VMs:")
    vm_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.endswith('_Output'):
            vm_name = item.name[:-7]  # Remove '_Output' suffix
            metadata_file = item / 'vm_metadata.json'
            
            vm_info = {'name': vm_name, 'directory': str(item)}
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    vm_info['metadata'] = metadata
                except Exception:
                    vm_info['metadata'] = None
            
            vm_dirs.append(vm_info)
    
    if vm_dirs:
        for vm in vm_dirs:
            print(f"\n  📦 {vm['name']}")
            print(f"     Directory: {vm['directory']}")
            
            if vm.get('metadata'):
                metadata = vm['metadata']
                if 'creation_date' in metadata:
                    print(f"     Created: {metadata['creation_date']}")
                if 'configuration' in metadata:
                    config = metadata['configuration']
                    print(f"     CPU: {config.get('cpu', 'N/A')}")
                    print(f"     RAM: {config.get('ram', 'N/A')} MB")
                    print(f"     SSD: {config.get('ssd', 'N/A')} GB")
                    print(f"     OS: {config.get('os_type', 'N/A')}")
                
                # Check directory structure
                vm_dir = Path(vm['directory'])
                subdirs = ['vm_files', 'config', 'logs', 'backups', 'snapshots']
                missing_dirs = []
                for subdir in subdirs:
                    if not (vm_dir / subdir).exists():
                        missing_dirs.append(subdir)
                
                if missing_dirs:
                    print(f"     ⚠️  Missing directories: {', '.join(missing_dirs)}")
                else:
                    print(f"     ✅ All directories present")
                
                # Check for backup and snapshot scripts
                scripts = ['create_backup.bat', 'create_snapshot.bat']
                missing_scripts = []
                for script in scripts:
                    if not (vm_dir / script).exists():
                        missing_scripts.append(script)
                
                if missing_scripts:
                    print(f"     ⚠️  Missing scripts: {', '.join(missing_scripts)}")
                else:
                    print(f"     ✅ All scripts present")
    else:
        print("  No organized VMs found.")
    
    # Check for unorganized VMs
    print("\n📂 UNORGANIZED VMs:")
    unorganized = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.startswith('output-'):
            vm_name = item.name[7:]  # Remove 'output-' prefix
            organized_dir = base_dir / f"{vm_name}_Output"
            
            if not organized_dir.exists():
                unorganized.append(vm_name)
    
    if unorganized:
        for vm_name in unorganized:
            print(f"  📁 {vm_name} (can be organized)")
        print(f"\n  💡 To organize: python vm_manager.py organize <vm_name>")
    else:
        print("  No unorganized VMs found.")
    
    # Check system dependencies
    print("\n🔧 SYSTEM DEPENDENCIES:")
    dependencies = {
        'python': 'python --version',
        'packer': 'packer version',
        'vmware': 'vmrun'
    }
    
    for dep, cmd in dependencies.items():
        try:
            result = os.system(f"{cmd} >nul 2>&1")
            status = "✅ AVAILABLE" if result == 0 else "❌ NOT FOUND"
        except:
            status = "❌ NOT FOUND"
        print(f"  {dep:<10} {status}")
    
    # Check logs
    print("\n📋 LOG FILES:")
    log_files = ['flask_app.log', 'vm_organizer.log']
    for log_file in log_files:
        log_path = base_dir / log_file
        if log_path.exists():
            size = log_path.stat().st_size
            modified = datetime.fromtimestamp(log_path.stat().st_mtime)
            print(f"  {log_file:<20} ✅ {size} bytes, modified {modified.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  {log_file:<20} ❌ NOT FOUND")
    
    # System recommendations
    print("\n💡 RECOMMENDATIONS:")
    recommendations = []
    
    if not vm_dirs:
        recommendations.append("Create your first VM using the web interface or command line")
    
    if unorganized:
        recommendations.append(f"Organize {len(unorganized)} unorganized VM(s)")
    
    # Check for old backups (if any VMs exist)
    if vm_dirs:
        old_backups = 0
        for vm in vm_dirs:
            backup_dir = Path(vm['directory']) / 'backups'
            if backup_dir.exists():
                for backup in backup_dir.iterdir():
                    if backup.is_dir():
                        # Check if backup is older than 30 days
                        backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                        days_old = (datetime.now() - backup_time).days
                        if days_old > 30:
                            old_backups += 1
        
        if old_backups > 0:
            recommendations.append(f"Consider cleaning up {old_backups} old backup(s)")
    
    if not recommendations:
        recommendations.append("System is running optimally! 🎉")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("For help, run: python vm_manager.py --help")
    print("For web interface: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    check_system_status()