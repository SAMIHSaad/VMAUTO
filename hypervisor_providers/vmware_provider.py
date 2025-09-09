"""
VMware Hypervisor Provider
Handles VMware Workstation operations using vmrun and Packer
"""

import os
import sys
import subprocess
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from .base_provider import BaseHypervisorProvider, VMConfig, VMInfo

class VMwareProvider(BaseHypervisorProvider):
    """VMware Workstation provider using vmrun and Packer"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.vmrun_path = config.get('vmrun_path', r'C:\ Program Files (x86)\VMware\VMware Workstation\vmrun.exe')
        self.base_directory = Path(config.get('base_directory', os.getcwd()))
        self.templates_directory = Path(config.get('templates_directory', 
            r'C:\Users\saads\OneDrive\Documents\Virtual Machines'))
        self.cloned_vms_directory = self.base_directory / 'cloned-vms'
        self.permanent_vms_directory = self.base_directory / 'permanent_vms'
        self.created_machines_directory = self.base_directory / 'createdMachines'
        
        # Ensure directories exist
        self.cloned_vms_directory.mkdir(exist_ok=True)
        self.permanent_vms_directory.mkdir(exist_ok=True)
        self.created_machines_directory.mkdir(exist_ok=True)

        # Template alias mapping (case-insensitive keys)
        self.template_aliases = {
            "windowsserver2019": "Windows Server 2019",
            "windows server 2019": "Windows Server 2019",
            "ubuntu": "Ubuntu 64-bit (3)",
            "ubuntu3": "Ubuntu 64-bit (3)",
            "ubuntu 3": "Ubuntu 64-bit (3)",
            "ubuntu 64-bit (3)": "Ubuntu 64-bit (3)"
        }
    
    def connect(self) -> bool:
        """Connect to VMware (check if vmrun is available)"""
        try:
            result = subprocess.run([self.vmrun_path, 'list'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"Failed to connect to VMware: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from VMware (no action needed for vmrun)"""
        return True
    
    def create_vm(self, vm_config: VMConfig) -> Dict[str, Any]:
        """Create a new VM using Packer"""
        try:
            self.validate_config(vm_config)
            
            # Clean up existing output directory to prevent Packer conflicts
            self._cleanup_existing_output_directory(vm_config.name)
            
            # Determine ISO path and checksum
            iso_path = os.environ.get("ISO_PATH")
            if not iso_path:
                iso_path = r"C:/Users/saads/OneDrive/Documents/Coding/demo-automation/templates/ubuntu-24.04.2-desktop-amd64.iso"
            iso_checksum = self._compute_iso_checksum()
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "VM_NAME": vm_config.name,
                "OS_TYPE": vm_config.os_type,
                "CPU": str(vm_config.cpu),
                "RAM": str(vm_config.ram),
                "SSD": str(vm_config.disk),
                "IP_ADDRESS": vm_config.ip_address or ""
            })
            
            # Build Packer command
            packer_command = [
                "packer", "build",
                "-on-error=abort",
                "-var", f"vm_name={vm_config.name}",
                "-var", f"cpu={vm_config.cpu}",
                "-var", f"ram={vm_config.ram}",
                "-var", f"disk_gb={vm_config.disk}",
            ]

            # Ensure iso_url matches the checksum file to avoid mismatch
            if iso_path:
                iso_url_path = iso_path.replace("", "/")
                packer_command += ["-var", f"iso_url=file://{iso_url_path}"]
            
            if iso_checksum:
                packer_command += ["-var", f"iso_checksum={iso_checksum}"]
            
            # Try fast mode first, then headless, then GUI as fallbacks
            packer_command_fast = packer_command + ["build-fast.pkr.hcl"]
            packer_command_headless = packer_command + ["build-headless.pkr.hcl"]
            packer_command_gui = packer_command + ["build.pkr.hcl"]
            
            print(f"Creating VM '{vm_config.name}' with Packer (trying fast mode first)...")
            result = subprocess.run(
                packer_command_fast,
                cwd=str(self.base_directory),
                capture_output=True,
                text=True,
                env=env,
                timeout=300   # 5 minutes timeout for fast mode (template cloning)
            )
            
            # If fast mode failed, try headless mode as fallback
            if result.returncode != 0:
                print(f"Fast build failed. Trying headless mode as fallback...")
                print(f"Fast error (full): {result.stderr}")
                if result.stdout:
                    print(f"Fast stdout: {result.stdout}")
                
                # Clean up any partial build artifacts before retry
                self._cleanup_existing_output_directory(vm_config.name)
                
                print("Retrying with headless mode...")
                result = subprocess.run(
                    packer_command_headless,
                    cwd=str(self.base_directory),
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=900   # 15 minutes timeout for headless installation
                )
                
                # If headless also failed, try GUI mode as final fallback
                if result.returncode != 0:
                    print(f"Headless build also failed. Trying GUI mode as final fallback...")
                    print(f"Headless error (full): {result.stderr}")
                    if result.stdout:
                        print(f"Headless stdout: {result.stdout}")
                    
                    # Clean up any partial build artifacts before retry
                    self._cleanup_existing_output_directory(vm_config.name)
                    
                    print("Retrying with GUI mode...")
                    result = subprocess.run(
                        packer_command_gui,
                        cwd=str(self.base_directory),
                        capture_output=True,
                        text=True,
                        env=env,
                        timeout=1200  # 20 minutes timeout for GUI installation
                    )
                    
                    if result.returncode == 0:
                        print("✅ GUI build succeeded!")
                    else:
                        print(f"❌ All build modes failed")
                        print(f"GUI error (full): {result.stderr}")
                        if result.stdout:
                            print(f"GUI stdout: {result.stdout}")
                else:
                    print("✅ Headless build succeeded!")
            else:
                print("✅ Fast build succeeded!")
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Packer build failed: {result.stderr}",
                    'stdout': result.stdout
                }
            
            # The VM is already created in the createdMachines directory by Packer.
            
            return {
                'success': True,
                'vm_name': vm_config.name,
                'provider': 'vmware',
                'message': f"VM '{vm_config.name}' created successfully"
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "Packer build timed out."
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating VM: {str(e)}"
            }
    
    def clone_vm(self, source_vm: str, vm_config: VMConfig) -> Dict[str, Any]:
        """Clone an existing VM using vmrun"""
        try:
            self.validate_config(vm_config)
            
            # Resolve alias
            source_vm_name = self.template_aliases.get(source_vm.lower(), source_vm)

            # Find source VMX file from templates directory only
            source_vmx_path = self._find_template_vmx(source_vm_name)
            if not source_vmx_path:
                return {
                    'success': False,
                    'error': f"Source VM '{source_vm_name}' not found in templates directory"
                }
            
            # Destination paths
            dest_dir = self.cloned_vms_directory / vm_config.name
            dest_vmx_path = dest_dir / f"{vm_config.name}.vmx"
            
            if dest_dir.exists():
                return {
                    'success': False,
                    'error': f"Destination directory '{dest_dir}' already exists"
                }
            
            # Clone using vmrun
            clone_command = [
                self.vmrun_path, "clone",
                str(source_vmx_path),
                str(dest_vmx_path),
                "full",
                f"-cloneName={vm_config.name}"
            ]
            
            print(f"Cloning VM '{source_vm}' to '{vm_config.name}'...")
            result = subprocess.run(clone_command, capture_output=True, text=True, timeout=1800)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"vmrun clone failed: {result.stderr}"
                }
            
            # Configure cloned VM
            self._configure_cloned_vm(dest_vmx_path, vm_config)
            
            # Start VM
            subprocess.run([self.vmrun_path, "start", str(dest_vmx_path)], 
                         check=False)
            
            return {
                'success': True,
                'vm_name': vm_config.name,
                'provider': 'vmware',
                'vmx_path': str(dest_vmx_path),
                'message': f"VM '{vm_config.name}' cloned successfully"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error cloning VM: {str(e)}"
            }
    
    def delete_vm(self, vm_name: str) -> bool:
        """Delete a VM"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            # Stop VM if running
            subprocess.run([self.vmrun_path, "stop", str(vmx_path)], 
                         capture_output=True, check=False)
            
            # Delete VM directory
            vm_dir = vmx_path.parent
            import shutil
            shutil.rmtree(vm_dir, ignore_errors=True)
            
            return True
            
        except Exception as e:
            print(f"Error deleting VM '{vm_name}': {e}")
            return False
    
    def start_vm(self, vm_name: str) -> bool:
        """Start a VM"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            result = subprocess.run([self.vmrun_path, "start", str(vmx_path), "nogui"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error starting VM '{vm_name}': {e}")
            return False
    
    def stop_vm(self, vm_name: str) -> bool:
        """Stop a VM"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            result = subprocess.run([self.vmrun_path, "stop", str(vmx_path)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error stopping VM '{vm_name}': {e}")
            return False
    
    def restart_vm(self, vm_name: str) -> bool:
        """Restart a VM"""
        return self.stop_vm(vm_name) and self.start_vm(vm_name)
    
    def get_vm_info(self, vm_name: str) -> Optional[VMInfo]:
        """Get VM information"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return None
            
            # Read VMX file for configuration
            vmx_content = vmx_path.read_text()
            
            # Extract configuration
            cpu = self._extract_vmx_value(vmx_content, 'numvcpus', '2')
            ram = self._extract_vmx_value(vmx_content, 'memsize', '2048')
            
            # Get VM state
            result = subprocess.run([self.vmrun_path, "list"], 
                                  capture_output=True, text=True)
            is_running = str(vmx_path) in result.stdout if result.returncode == 0 else False
            state = "running" if is_running else "stopped"
            
            # Get IP address if running
            ip_address = None
            if is_running:
                try:
                    ip_result = subprocess.run([self.vmrun_path, "getGuestIPAddress", str(vmx_path)],
                                               capture_output=True, text=True, timeout=10)
                    if ip_result.returncode == 0 and ip_result.stdout.strip():
                        ip_address = ip_result.stdout.strip()
                except Exception as e:
                    print(f"Could not retrieve IP for {vm_name}: {e}")

            return VMInfo(
                name=vm_name,
                uuid=vm_name,  # VMware doesn't expose UUID easily via vmrun
                state=state,
                cpu=int(cpu),
                ram=int(ram),
                disk=0,  # Would need additional parsing
                ip_address=ip_address,
                hypervisor="vmware"
            )
            
        except Exception as e:
            print(f"Error getting VM info for '{vm_name}': {e}")
            return None
    
    def list_vms(self) -> List[VMInfo]:
        """List all VMs including cloned and created machines"""
        vms = []
        
        # Search in cloned VMs directory
        for vm_dir in self.cloned_vms_directory.iterdir():
            if vm_dir.is_dir():
                vm_info = self.get_vm_info(vm_dir.name)
                if vm_info:
                    vms.append(vm_info)
        
        # Search in created machines directory
        for vm_dir in self.created_machines_directory.iterdir():
            if vm_dir.is_dir():
                vm_info = self.get_vm_info(vm_dir.name)
                if vm_info:
                    vms.append(vm_info)
        
        return vms
    
    def get_templates(self) -> List[str]:
        """Get available VM templates - only return actual templates"""
        return ["Ubuntu 64-bit (3)", "Windows Server 2019"]
    
    def get_clusters(self) -> List[str]:
        """Get available clusters (not applicable for VMware Workstation)"""
        return ["local"]
    
    def get_networks(self) -> List[str]:
        """Get available networks"""
        return ["NAT", "Bridged", "Host-only"]
    
    def create_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Create a VM snapshot"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            result = subprocess.run([
                self.vmrun_path, "snapshot", str(vmx_path), snapshot_name
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating snapshot for VM '{vm_name}': {e}")
            return False
    
    def restore_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Restore a VM snapshot"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            result = subprocess.run([
                self.vmrun_path, "revertToSnapshot", str(vmx_path), snapshot_name
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error restoring snapshot for VM '{vm_name}': {e}")
            return False
    
    def delete_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Delete a VM snapshot"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return False
            
            result = subprocess.run([
                self.vmrun_path, "deleteSnapshot", str(vmx_path), snapshot_name
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error deleting snapshot for VM '{vm_name}': {e}")
            return False
    
    def _find_vmx_file(self, vm_name: str) -> Optional[Path]:
        """Find VMX file for a VM (cloned, permanent, or template)"""
        # Search in cloned VMs
        cloned_vmx = self.cloned_vms_directory / vm_name / f"{vm_name}.vmx"
        if cloned_vmx.exists():
            return cloned_vmx
        
        # Search in permanent VMs
        permanent_vmx = self.permanent_vms_directory / vm_name / f"{vm_name}.vmx"
        if permanent_vmx.exists():
            return permanent_vmx
        
        # Search in created machines
        created_vmx = self.created_machines_directory / vm_name / f"{vm_name}.vmx"
        if created_vmx.exists():
            return created_vmx

        # Search in templates directory
        template_vmx = self.templates_directory / vm_name 
        if template_vmx.is_dir():
            vmx_files = list(template_vmx.glob('*.vmx'))
            if vmx_files:
                return vmx_files[0]

        return None

    def _find_template_vmx(self, template_name: str) -> Optional[Path]:
        """Find VMX file for a template in the templates directory only"""
        for template_dir in self.templates_directory.iterdir():
            if template_dir.is_dir() and template_dir.name == template_name:
                vmx_files = list(template_dir.glob('*.vmx'))
                if vmx_files:
                    return vmx_files[0]
        return None
    
    def _compute_iso_checksum(self) -> Optional[str]:
        """Compute ISO checksum if ISO exists"""
        try:
            iso_path = os.environ.get("ISO_PATH")
            if not iso_path:
                iso_path = r"C:/Users/saads/OneDrive/Documents/Coding/demo-automation/templates/ubuntu-24.04.2-desktop-amd64.iso"
            
            if os.path.exists(iso_path):
                print(f"Computing SHA256 for ISO: {iso_path}")
                sha256 = hashlib.sha256()
                with open(iso_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(1024*1024), b''):
                        sha256.update(chunk)
                return f"sha256:{sha256.hexdigest()}"
        except Exception as e:
            print(f"Failed to compute ISO checksum: {e}")
        
        return None
    
    def _configure_cloned_vm(self, vmx_path: Path, vm_config: VMConfig):
        """Configure cloned VM settings by modifying VMX file directly"""
        try:
            # Read current VMX content
            vmx_content = vmx_path.read_text()
            lines = vmx_content.split('\n')
            
            # Update CPU and RAM settings
            new_lines = []
            cpu_updated = False
            ram_updated = False
            
            for line in lines:
                if line.strip().startswith('numvcpus ='):
                    new_lines.append(f'numvcpus = "{vm_config.cpu}"')
                    cpu_updated = True
                elif line.strip().startswith('memsize ='):
                    new_lines.append(f'memsize = "{vm_config.ram}"')
                    ram_updated = True
                else:
                    new_lines.append(line)
            
            # Add settings if they weren't found
            if not cpu_updated:
                new_lines.append(f'numvcpus = "{vm_config.cpu}"')
            if not ram_updated:
                new_lines.append(f'memsize = "{vm_config.ram}"')
            
            # Write back to VMX file
            vmx_path.write_text('\n'.join(new_lines))
            print(f"Configured VM with {vm_config.cpu} CPUs and {vm_config.ram}MB RAM")
            
            # Configure IP address if provided
            if vm_config.ip_address:
                print(f"Configuring IP address {vm_config.ip_address} for VM...")
                ip_result = self._assign_ip_address(vmx_path, vm_config.ip_address, vm_config.gateway, vm_config.dns)
                if ip_result['success']:
                    print(f"✅ {ip_result['message']}")
                else:
                    print(f"⚠️ IP assignment failed: {ip_result['error']}")
            
        except Exception as e:
            print(f"Error configuring cloned VM: {e}")
    
    def _assign_ip_address(self, vmx_path: Path, ip_address: str, gateway: str, dns: str) -> Dict[str, Any]:
        """Assign IP address to VM using the IP assignment script"""
        try:
            # Import the IP assignment manager
            scripts_dir = self.base_directory / 'scripts'
            sys.path.append(str(scripts_dir))
            
            from assign_ip_vmware import VMwareIPAssigner
            
            # Create IP assigner
            assigner = VMwareIPAssigner(self.vmrun_path)
            
            # Assign IP address
            result = assigner.assign_static_ip(str(vmx_path), ip_address, gateway=gateway, dns=dns)
            
            return result
            
        except ImportError as e:
            return {
                'success': False,
                'error': f"IP assignment script not found: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error assigning IP address: {str(e)}"
            }
    
    def _extract_vmx_value(self, vmx_content: str, key: str, default: str) -> str:
        """Extract value from VMX content"""
        for line in vmx_content.split('\n'):
            if line.strip().startswith(f'{key} ='):
                return line.split('=')[1].strip().strip('"')
        return default
    
    # _move_created_vm_to_created_machines_directory is removed as it is no longer needed.
    
    def _cleanup_existing_output_directory(self, vm_name: str):
        """Clean up existing Packer output directory to prevent conflicts"""
        import shutil
        
        # Common output directory patterns that Packer might use
        output_dirs = [
            self.base_directory / "output-ubuntu",
            self.base_directory / "output-windows", 
            self.base_directory / "output-centos",
            self.base_directory / f"output-{vm_name}",
            self.base_directory / f"{vm_name}_Output"
        ]
        
        for output_dir in output_dirs:
            if output_dir.exists():
                print(f"Cleaning up existing output directory: {output_dir}")
                try:
                    # Stop any VMs that might be using files in this directory
                    vmx_files = list(output_dir.glob("*.vmx"))
                    for vmx_file in vmx_files:
                        try:
                            subprocess.run([self.vmrun_path, "stop", str(vmx_file)], 
                                         capture_output=True, check=False, timeout=30)
                        except:
                            pass  # Ignore errors if VM is not running
                    
                    # Remove the directory
                    shutil.rmtree(str(output_dir), ignore_errors=True)
                    print(f"Successfully cleaned up: {output_dir}")
                    
                except Exception as e:
                    print(f"Warning: Could not fully clean up {output_dir}: {e}")
                    # Try to remove individual files if directory removal fails
                    try:
                        for file_path in output_dir.rglob("*"):
                            if file_path.is_file():
                                try:
                                    file_path.unlink()
                                except:
                                    pass
                    except:
                        pass
    
    def open_console(self, vm_name: str) -> Dict[str, Any]:
        """Open VM console in VMware Workstation"""
        try:
            vmx_path = self._find_vmx_file(vm_name)
            if not vmx_path:
                return {
                    'success': False,
                    'error': f"VM '{vm_name}' not found"
                }
            
            # Check if VMware Workstation GUI is available
            vmware_exe = self.vmrun_path.replace('vmrun.exe', 'vmware.exe')
            
            if not os.path.exists(vmware_exe):
                return {
                    'success': False,
                    'error': "VMware Workstation GUI not found"
                }
            
            # Launch VMware Workstation with the VM
            print(f"Opening console for VM '{vm_name}'...")
            subprocess.Popen([vmware_exe, str(vmx_path)], 
                           cwd=str(vmx_path.parent))
            
            return {
                'success': True,
                'message': f"Console opened for VM '{vm_name}'"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error opening console for VM '{vm_name}': {str(e)}"
            }
