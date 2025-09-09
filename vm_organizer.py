"""
VM Organizer Module
Handles the organization and backup of VM files after creation.
"""

import os
import shutil
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class VMOrganizer:
    """Handles VM file organization and backup operations."""
    
    def __init__(self, base_directory: str = None):
        """Initialize the VM Organizer.
        
        Args:
            base_directory: Base directory for VM operations. Defaults to current directory.
        """
        self.base_directory = Path(base_directory) if base_directory else Path.cwd()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for VM operations."""
        logger = logging.getLogger('vm_organizer')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.base_directory / 'vm_organizer.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not logger.handlers:
            logger.addHandler(file_handler)
            
        return logger
    
    def organize_vm_files(self, vm_name: str, vm_config: Dict) -> str:
        """Organize VM files into a structured directory.
        
        Args:
            vm_name: Name of the VM
            vm_config: Configuration dictionary containing VM parameters
            
        Returns:
            Path to the organized VM directory
        """
        try:
            self.logger.info(f"Starting organization for VM: {vm_name}")
            
            # Create the main VM directory
            vm_output_dir = self.base_directory / f"{vm_name}_Output"
            vm_output_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            subdirs = {
                'vm_files': vm_output_dir / 'vm_files',
                'config': vm_output_dir / 'config',
                'logs': vm_output_dir / 'logs',
                'backups': vm_output_dir / 'backups',
                'snapshots': vm_output_dir / 'snapshots'
            }
            
            for subdir in subdirs.values():
                subdir.mkdir(exist_ok=True)
            
            # Move VM files from Packer output directory
            self._move_vm_files(vm_name, subdirs['vm_files'])
            
            # Copy configuration files
            self._copy_config_files(subdirs['config'], vm_config)
            
            # Copy logs
            self._copy_logs(subdirs['logs'])
            
            # Create VM metadata
            self._create_vm_metadata(vm_output_dir, vm_name, vm_config)
            
            # Create backup script
            self._create_backup_script(vm_output_dir, vm_name)
            
            # Create snapshot script
            self._create_snapshot_script(vm_output_dir, vm_name)

            # Create power control scripts (snapshot before stop/restart)
            self._create_power_scripts(vm_output_dir, vm_name)
            
            # Create README file
            self._create_readme(vm_output_dir, vm_name)

            # Ensure persistent disk mode and enable AutoProtect autosnapshots
            self._ensure_vmx_persistent_and_autosave(vm_output_dir, vm_name)
            
            # Try to register VM with VMware
            self._register_vm_with_vmware(vm_output_dir, vm_name)
            
            self.logger.info(f"Successfully organized VM files for: {vm_name}")
            return str(vm_output_dir)
            
        except Exception as e:
            self.logger.error(f"Error organizing VM files for {vm_name}: {str(e)}")
            raise
    
    def _move_vm_files(self, vm_name: str, destination: Path):
        """Move VM files from Packer output directory to organized location."""
        # Look for Packer output directory
        packer_output_dir = self.base_directory / f"output-{vm_name}"
        
        if packer_output_dir.exists():
            self.logger.info(f"Moving VM files from {packer_output_dir} to {destination}")
            
            # Move all files from packer output to vm_files directory
            for file_path in packer_output_dir.iterdir():
                if file_path.is_file():
                    destination_file = destination / file_path.name
                    shutil.move(str(file_path), str(destination_file))
                    self.logger.info(f"Moved: {file_path.name}")
            
            # Remove empty packer output directory
            try:
                packer_output_dir.rmdir()
                self.logger.info(f"Removed empty directory: {packer_output_dir}")
            except OSError:
                self.logger.warning(f"Could not remove directory: {packer_output_dir}")
        else:
            self.logger.warning(f"Packer output directory not found: {packer_output_dir}")
    
    def _copy_config_files(self, config_dir: Path, vm_config: Dict):
        """Copy configuration files used to create the VM."""
        config_files = [
            'build.pkr.hcl',
            'http/user-data',
            'http/meta-data',
            'http/ks.cfg',
            'ansible/provision_vm.yml',
            'ansible/ansible.cfg'
        ]
        
        for config_file in config_files:
            source_file = self.base_directory / config_file
            if source_file.exists():
                if source_file.is_file():
                    destination = config_dir / source_file.name
                    shutil.copy2(str(source_file), str(destination))
                    self.logger.info(f"Copied config file: {config_file}")
                else:
                    # Handle directories
                    destination = config_dir / source_file.name
                    if destination.exists():
                        shutil.rmtree(str(destination))
                    shutil.copytree(str(source_file), str(destination))
                    self.logger.info(f"Copied config directory: {config_file}")
    
    def _copy_logs(self, logs_dir: Path):
        """Copy relevant log files."""
        log_files = [
            'flask_app.log',
            'vm_organizer.log'
        ]
        
        for log_file in log_files:
            source_file = self.base_directory / log_file
            if source_file.exists():
                destination = logs_dir / log_file
                shutil.copy2(str(source_file), str(destination))
                self.logger.info(f"Copied log file: {log_file}")
    
    def _create_vm_metadata(self, vm_dir: Path, vm_name: str, vm_config: Dict):
        """Create metadata file with VM information."""
        metadata = {
            'vm_name': vm_name,
            'creation_date': datetime.datetime.now().isoformat(),
            'configuration': vm_config,
            'directory_structure': {
                'vm_files': 'Contains all VM files (vmx, vmdk, nvram, etc.)',
                'config': 'Contains configuration files used to create the VM',
                'logs': 'Contains creation and operation logs',
                'backups': 'Directory for VM backups',
                'snapshots': 'Directory for VM snapshots'
            },
            'files_included': self._get_vm_files_list(vm_dir / 'vm_files')
        }
        
        metadata_file = vm_dir / 'vm_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Created metadata file: {metadata_file}")
    
    def _get_vm_files_list(self, vm_files_dir: Path) -> List[str]:
        """Get list of VM files."""
        if not vm_files_dir.exists():
            return []
        
        return [f.name for f in vm_files_dir.iterdir() if f.is_file()]
    
    def _create_backup_script(self, vm_dir: Path, vm_name: str):
        """Create a backup script for the VM."""
        backup_script_content = f'''@echo off
REM VM Backup Script for {vm_name}
REM This script creates a backup of the VM files

set VM_NAME={vm_name}
set VM_DIR=%~dp0
set BACKUP_DIR=%VM_DIR%backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo Creating backup for VM: %VM_NAME%
echo Backup directory: %BACKUP_DIR%

REM Create timestamped backup directory
mkdir "%BACKUP_DIR%\\%VM_NAME%_%TIMESTAMP%"

REM Copy VM files
echo Copying VM files...
xcopy "%VM_DIR%vm_files\\*" "%BACKUP_DIR%\\%VM_NAME%_%TIMESTAMP%\\" /E /I /H /Y

REM Copy metadata
copy "%VM_DIR%vm_metadata.json" "%BACKUP_DIR%\\%VM_NAME%_%TIMESTAMP%\\"

echo Backup completed: %BACKUP_DIR%\\%VM_NAME%_%TIMESTAMP%
pause
'''
        
        backup_script = vm_dir / 'create_backup.bat'
        with open(backup_script, 'w') as f:
            f.write(backup_script_content)
        
        self.logger.info(f"Created backup script: {backup_script}")
    
    def _create_snapshot_script(self, vm_dir: Path, vm_name: str):
        """Create a snapshot script for the VM."""
        snapshot_script_content = f'''@echo off
REM VM Snapshot Script for {vm_name}
REM This script creates a snapshot of the running VM using VMware tools

set VM_NAME={vm_name}
set VM_DIR=%~dp0
set SNAPSHOT_DIR=%VM_DIR%snapshots
set VMX_FILE=%VM_DIR%vm_files\\{vm_name}.vmx

echo Creating snapshot for VM: %VM_NAME%
echo VM file: %VMX_FILE%

REM Check if VMX file exists
if not exist "%VMX_FILE%" (
    echo Error: VMX file not found: %VMX_FILE%
    pause
    exit /b 1
)

REM Create snapshot directory if it doesn't exist
if not exist "%SNAPSHOT_DIR%" mkdir "%SNAPSHOT_DIR%"

REM Create snapshot name with timestamp
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set SNAPSHOT_NAME=Snapshot_%TIMESTAMP%

echo Creating snapshot: %SNAPSHOT_NAME%

REM Use vmrun to create snapshot (requires VMware Workstation/Player)
vmrun snapshot "%VMX_FILE%" "%SNAPSHOT_NAME%"

if %ERRORLEVEL% EQU 0 (
    echo Snapshot created successfully: %SNAPSHOT_NAME%
    echo Snapshot saved in VM directory
) else (
    echo Error creating snapshot. Make sure VMware tools are installed and VM is accessible.
)

pause
'''
        
        snapshot_script = vm_dir / 'create_snapshot.bat'
        with open(snapshot_script, 'w') as f:
            f.write(snapshot_script_content)
        
        self.logger.info(f"Created snapshot script: {snapshot_script}")
    
    def _create_power_scripts(self, vm_dir: Path, vm_name: str):
        """Create Start/Stop/Restart scripts that take a snapshot before power-off or restart."""
        vmx_path = vm_dir / 'vm_files' / f'{vm_name}.vmx'

        start_bat = f'''@echo off
REM Start VM (no snapshot here)
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
vmrun start %VMX% nogui
if %ERRORLEVEL% NEQ 0 (
  echo Failed to start VM
  pause
  exit /b %ERRORLEVEL%
)
echo VM started.
'''

        stop_bat = f'''@echo off
REM Stop VM after taking a snapshot
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do set TS=%%d%%b%%c_%%e%%f%%g
set TS=%TS: =0%
set SNAP=PreStop_%vm_name%_%TS%

REM Create snapshot
vmrun snapshot %VMX% "%SNAP%"
if %ERRORLEVEL% NEQ 0 (
  echo Snapshot failed. Aborting stop to avoid data loss.
  pause
  exit /b %ERRORLEVEL%
)

REM Graceful stop first
vmrun stop %VMX% soft
if %ERRORLEVEL% NEQ 0 (
  echo Soft stop failed, forcing power off...
  vmrun stop %VMX% hard
)
echo VM stopped.
'''

        restart_bat = f'''@echo off
REM Restart VM with a snapshot before reboot
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do set TS=%%d%%b%%c_%%e%%f%%g
set TS=%TS: =0%
set SNAP=PreRestart_%vm_name%_%TS%

REM Create snapshot
vmrun snapshot %VMX% "%SNAP%"
if %ERRORLEVEL% NEQ 0 (
  echo Snapshot failed. Aborting restart to avoid data loss.
  pause
  exit /b %ERRORLEVEL%
)

REM Try a guest OS reboot if tools are available; else stop+start
vmrun reset %VMX% soft
if %ERRORLEVEL% NEQ 0 (
  echo Soft reset failed, stopping and starting instead...
  vmrun stop %VMX% soft
  if %ERRORLEVEL% NEQ 0 vmrun stop %VMX% hard
  vmrun start %VMX% nogui
)
echo VM restarted.
'''

        # Write scripts
        (vm_dir / 'Start_VM.bat').write_text(start_bat)
        (vm_dir / 'Stop_VM_WithSnapshot.bat').write_text(stop_bat)
        (vm_dir / 'Restart_VM_WithSnapshot.bat').write_text(restart_bat)
        self.logger.info(f"Created power control scripts in: {vm_dir}")

    def _create_readme(self, vm_dir: Path, vm_name: str):
        """Create a README file with instructions."""
        readme_content = f'''# {vm_name} - Virtual Machine Package

This directory contains all files and configurations for the virtual machine "{vm_name}".

## Directory Structure

- **vm_files/**: Contains all VM files (vmx, vmdk, nvram, etc.)
- **config/**: Contains configuration files used to create the VM
- **logs/**: Contains creation and operation logs
- **backups/**: Directory for VM backups
- **snapshots/**: Directory for VM snapshots

## Files

- **vm_metadata.json**: Contains VM metadata and configuration information
- **create_backup.bat**: Script to create a backup of the VM
- **create_snapshot.bat**: Script to create a snapshot of the running VM
- **README.md**: This file

## Usage

### Running the VM
1. Navigate to the `vm_files/` directory
2. Double-click the `.vmx` file to open in VMware
3. Or use VMware Workstation/Player to open the VM

### Creating Backups
1. Run `create_backup.bat` to create a timestamped backup
2. Backups are stored in the `backups/` directory

### Creating Snapshots
1. Ensure the VM is running in VMware
2. Run `create_snapshot.bat` to create a snapshot
3. Snapshots are managed by VMware and stored with the VM files

## Important Notes

- Keep this entire directory structure intact to prevent VM loss
- Regular backups are recommended before making significant changes
- The VM files in `vm_files/` directory are the core VM components
- Configuration files in `config/` directory can be used to recreate the VM if needed

## VM Configuration

Creation Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
VM Name: {vm_name}

For detailed configuration information, see `vm_metadata.json`.

## Troubleshooting

If the VM fails to start:
1. Check that all files in `vm_files/` are present
2. Ensure VMware Workstation/Player is installed
3. Try opening the `.vmx` file directly in VMware
4. Check the logs in the `logs/` directory for error messages

## Recovery

If VM files are corrupted or lost:
1. Check the `backups/` directory for recent backups
2. Use the configuration files in `config/` directory to recreate the VM
3. Restore from the most recent backup in `backups/` directory
'''
        
        readme_file = vm_dir / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        self.logger.info(f"Created README file: {readme_file}")
    
    def _register_vm_with_vmware(self, vm_dir: Path, vm_name: str):
        """Try to register the VM with VMware Workstation."""
        try:
            # Find VMX file
            vm_files_dir = vm_dir / 'vm_files'
            vmx_files = list(vm_files_dir.glob('*.vmx'))
            
            if not vmx_files:
                self.logger.warning(f"No VMX file found for VM: {vm_name}")
                return
            
            vmx_file = vmx_files[0]
            self.logger.info(f"Found VMX file: {vmx_file}")
            
            # Try to run PowerShell registration script
            register_script = self.base_directory / 'register_vm.ps1'
            if register_script.exists():
                try:
                    import subprocess
                    cmd = [
                        'powershell.exe',
                        '-ExecutionPolicy', 'Bypass',
                        '-File', str(register_script),
                        '-VMXPath', str(vmx_file),
                        '-VMName', vm_name
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        self.logger.info(f"VM registration script completed for: {vm_name}")
                    else:
                        self.logger.warning(f"VM registration script had issues: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.logger.warning("VM registration script timed out")
                except Exception as e:
                    self.logger.warning(f"Could not run VM registration script: {e}")
            else:
                self.logger.warning("VM registration script not found")
                
            # Create a simple batch file to open the VM
            self._create_open_vm_script(vm_dir, vm_name, vmx_file)
            
        except Exception as e:
            self.logger.error(f"Error registering VM with VMware: {e}")
    
    def _create_open_vm_script(self, vm_dir: Path, vm_name: str, vmx_file: Path):
        """Create a script to easily open the VM in VMware."""
        script_content = f'''@echo off
REM Quick Open Script for {vm_name}
REM Double-click this file to open the VM in VMware Workstation

echo Opening {vm_name} in VMware Workstation...
echo.

REM Try to find VMware Workstation
set VMWARE_PATH=""
if exist "%ProgramFiles(x86)%\\VMware\\VMware Workstation\\vmware.exe" (
    set VMWARE_PATH="%ProgramFiles(x86)%\\VMware\\VMware Workstation\\vmware.exe"
) else if exist "%ProgramFiles%\\VMware\\VMware Workstation\\vmware.exe" (
    set VMWARE_PATH="%ProgramFiles%\\VMware\\VMware Workstation\\vmware.exe"
) else if exist "%ProgramFiles(x86)%\\VMware\\VMware Player\\vmware.exe" (
    set VMWARE_PATH="%ProgramFiles(x86)%\\VMware\\VMware Player\\vmware.exe"
) else if exist "%ProgramFiles%\\VMware\\VMware Player\\vmware.exe" (
    set VMWARE_PATH="%ProgramFiles%\\VMware\\VMware Player\\vmware.exe"
)

if %VMWARE_PATH%=="" (
    echo VMware Workstation/Player not found in standard locations.
    echo Please manually open the VMX file: {vmx_file}
    pause
    exit /b 1
)

echo Found VMware at: %VMWARE_PATH%
echo Opening VM: {vmx_file}
echo.

REM Open the VM
%VMWARE_PATH% "{vmx_file}"

if %ERRORLEVEL% EQU 0 (
    echo VM opened successfully!
) else (
    echo Error opening VM. You can manually open the VMX file in VMware.
)

echo.
echo VM Location: {vmx_file}
echo.
pause
'''
        
        open_script = vm_dir / f'Open_{vm_name}_in_VMware.bat'
        with open(open_script, 'w') as f:
            f.write(script_content)
        
        self.logger.info(f"Created VM open script: {open_script}")

    def _ensure_vmx_persistent_and_autosave(self, vm_dir: Path, vm_name: str):
        """Ensure the VMX is set to persistent disk mode and enable AutoProtect snapshots.
        This helps changes to be saved and periodic snapshots to be taken automatically.
        """
        try:
            vm_files_dir = vm_dir / 'vm_files'
            vmx_files = list(vm_files_dir.glob('*.vmx'))
            if not vmx_files:
                self.logger.warning(f"No VMX file found when trying to enforce persistence for {vm_name}")
                return

            vmx_file = vmx_files[0]
            self.logger.info(f"Enforcing persistent disk and AutoProtect on: {vmx_file}")

            # Read VMX
            content = vmx_file.read_text(encoding='utf-8', errors='ignore').splitlines()
            updated = False

            def set_or_add(key: str, value: str):
                nonlocal content, updated
                line = f"{key} = \"{value}\""
                found = False
                for i, l in enumerate(content):
                    if l.strip().lower().startswith(f"{key}".lower() + " "):
                        if content[i] != line:
                            content[i] = line
                            updated = True
                        found = True
                        break
                if not found:
                    content.append(line)
                    updated = True

            # Ensure disks are persistent: clear redo (snapshot diff file) and persistent mode
            # scsi0:0.redo = "" indicates no non-persistent redo log
            # Prefer VMware's independent-persistent mode so writes go straight to disk and are not affected by snapshots
            set_or_add("scsi0:0.redo", "")
            set_or_add("scsi0:0.mode", "independent-persistent")

            # Enable VMware AutoProtect autosnapshots in Workstation UI terms
            # AutoProtect settings are Workstation features; these keys are honored by VMware Workstation
            set_or_add("autoProtect.enable", "TRUE")
            set_or_add("autoProtect.interval", "hourly")   # hourly, daily, weekly
            set_or_add("autoProtect.maxSnapshots", "3")     # keep last 3 snapshots

            if updated:
                vmx_file.write_text("\n".join(content) + "\n", encoding='utf-8')
                self.logger.info("VMX updated to enforce persistence and AutoProtect.")
            else:
                self.logger.info("VMX already configured for persistence and AutoProtect.")
        except Exception as e:
            self.logger.warning(f"Failed to enforce persistent/autosave settings: {e}")

def organize_vm_after_creation(vm_name: str, vm_config: Dict, base_directory: str = None) -> str:
    """Convenience function to organize VM files after creation.
    
    Args:
        vm_name: Name of the VM
        vm_config: Configuration dictionary containing VM parameters
        base_directory: Base directory for operations
        
    Returns:
        Path to the organized VM directory
    """
    organizer = VMOrganizer(base_directory)
    return organizer.organize_vm_files(vm_name, vm_config)