#!/usr/bin/env python3
"""
VMware IP Assignment Script
Assigns IP addresses to VMware VMs after cloning
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

class VMwareIPAssigner:
    """Handles IP assignment for VMware VMs"""
    
    def __init__(self, vmrun_path: str = None):
        """Initialize VMware IP assigner
        
        Args:
            vmrun_path: Path to vmrun executable
        """
        self.vmrun_path = vmrun_path or r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
    
    def assign_static_ip(self, vmx_path: str, ip_address: str, netmask: str = "255.255.255.0", 
                        gateway: str = None, dns: str = None) -> Dict[str, Any]:
        """Assign static IP to a VMware VM
        
        Args:
            vmx_path: Path to VMX file
            ip_address: IP address to assign
            netmask: Network mask (default: 255.255.255.0)
            gateway: Gateway IP
            dns: DNS server
            
        Returns:
            Dict with success status and message
        """
        try:
            vmx_path = Path(vmx_path)
            if not vmx_path.exists():
                return {
                    'success': False,
                    'error': f"VMX file not found: {vmx_path}"
                }
            
            print(f"Assigning IP {ip_address} to VM: {vmx_path.name}")
            
            # Check if VM is running
            is_running = self._is_vm_running(vmx_path)
            vm_was_stopped = False
            
            if not is_running:
                # Start VM if not running
                print("Starting VM for IP configuration...")
                start_result = subprocess.run([
                    self.vmrun_path, "start", str(vmx_path), "nogui"
                ], capture_output=True, text=True, timeout=120)
                
                if start_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f"Failed to start VM: {start_result.stderr}"
                    }
                
                # Wait for VM to boot
                print("Waiting for VM to boot...")
                time.sleep(30)
                vm_was_stopped = True
            
            # Wait for VMware Tools to be ready
            print("Waiting for VMware Tools...")
            tools_ready = self._wait_for_tools(vmx_path, timeout=300)
            if not tools_ready:
                return {
                    'success': False,
                    'error': "VMware Tools not ready - cannot configure network"
                }
            
            # Detect guest OS and configure IP accordingly
            guest_os = self._detect_guest_os(vmx_path)
            
            if guest_os == "linux":
                result = self._configure_linux_ip(vmx_path, ip_address, netmask, gateway, dns)
            elif guest_os == "windows":
                result = self._configure_windows_ip(vmx_path, ip_address, netmask, gateway, dns)
            else:
                result = {
                    'success': False,
                    'error': f"Unsupported guest OS: {guest_os}"
                }
            
            # Stop VM if it was stopped initially
            if vm_was_stopped and result.get('success'):
                print("Stopping VM after IP configuration...")
                subprocess.run([
                    self.vmrun_path, "stop", str(vmx_path)
                ], capture_output=True, text=True, timeout=60)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error assigning IP: {str(e)}"
            }
    
    def _is_vm_running(self, vmx_path: Path) -> bool:
        """Check if VM is running"""
        try:
            result = subprocess.run([self.vmrun_path, "list"], 
                                  capture_output=True, text=True, timeout=30)
            return str(vmx_path) in result.stdout if result.returncode == 0 else False
        except:
            return False
    
    def _wait_for_tools(self, vmx_path: Path, timeout: int = 300) -> bool:
        """Wait for VMware Tools to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([
                    self.vmrun_path, "checkToolsState", str(vmx_path)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and "running" in result.stdout.lower():
                    return True
                    
            except:
                pass
            
            time.sleep(10)
        
        return False
    
    def _detect_guest_os(self, vmx_path: Path) -> str:
        """Detect guest OS from VMX file"""
        try:
            vmx_content = vmx_path.read_text()
            for line in vmx_content.split('\n'):
                if line.strip().startswith('guestOS ='):
                    guest_os = line.split('=')[1].strip().strip('"').lower()
                    if 'ubuntu' in guest_os or 'linux' in guest_os:
                        return "linux"
                    elif 'windows' in guest_os:
                        return "windows"
            
            # Default to linux if not detected
            return "linux"
            
        except:
            return "linux"
    
    def _configure_linux_ip(self, vmx_path: Path, ip_address: str, netmask: str, 
                           gateway: str, dns: str) -> Dict[str, Any]:
        """Configure IP for Linux guest"""
        try:
            # Create netplan configuration
            netplan_config = f"""network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses:
        - {ip_address}/24
      gateway4: {gateway}
      nameservers:
        addresses:
          - {dns}
          - 8.8.4.4
"""
            
            # Write netplan config to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(netplan_config)
                temp_config = f.name
            
            try:
                # Copy netplan config to VM
                copy_result = subprocess.run([
                    self.vmrun_path, "CopyFileFromHostToGuest", str(vmx_path),
                    temp_config, "/tmp/01-netcfg.yaml"
                ], capture_output=True, text=True, timeout=60)
                
                if copy_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f"Failed to copy netplan config: {copy_result.stderr}"
                    }
                
                # Apply netplan configuration
                commands = [
                    "sudo mv /tmp/01-netcfg.yaml /etc/netplan/01-netcfg.yaml",
                    "sudo chmod 600 /etc/netplan/01-netcfg.yaml",
                    "sudo netplan apply"
                ]
                
                for cmd in commands:
                    result = subprocess.run([
                        self.vmrun_path, "runProgramInGuest", str(vmx_path),
                        "/bin/bash", "-c", cmd
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        print(f"Warning: Command failed: {cmd} - {result.stderr}")
                
                # Verify IP assignment
                time.sleep(10)
                verify_result = subprocess.run([
                    self.vmrun_path, "runProgramInGuest", str(vmx_path),
                    "/bin/bash", "-c", "ip addr show ens33 | grep 'inet '"
                ], capture_output=True, text=True, timeout=30)
                
                if ip_address in verify_result.stdout:
                    return {
                        'success': True,
                        'message': f"Successfully assigned IP {ip_address} to Linux VM"
                    }
                else:
                    return {
                        'success': False,
                        'error': f"IP assignment verification failed. Output: {verify_result.stdout}"
                    }
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_config)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'error': f"Error configuring Linux IP: {str(e)}"
            }
    
    def _configure_windows_ip(self, vmx_path: Path, ip_address: str, netmask: str,
                             gateway: str, dns: str) -> Dict[str, Any]:
        """Configure IP for Windows guest"""
        try:
            # Windows netsh commands to set static IP
            commands = [
                f'netsh interface ip set address "Ethernet" static {ip_address} {netmask} {gateway}',
                f'netsh interface ip set dns "Ethernet" static {dns}',
                f'netsh interface ip add dns "Ethernet" 8.8.4.4 index=2'
            ]
            
            for cmd in commands:
                result = subprocess.run([
                    self.vmrun_path, "runProgramInGuest", str(vmx_path),
                    "cmd.exe", "/c", cmd
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    print(f"Warning: Command failed: {cmd} - {result.stderr}")
            
            # Verify IP assignment
            time.sleep(10)
            verify_result = subprocess.run([
                self.vmrun_path, "runProgramInGuest", str(vmx_path),
                "cmd.exe", "/c", "ipconfig"
            ], capture_output=True, text=True, timeout=30)
            
            if ip_address in verify_result.stdout:
                return {
                    'success': True,
                    'message': f"Successfully assigned IP {ip_address} to Windows VM"
                }
            else:
                return {
                    'success': False,
                    'error': f"IP assignment verification failed. Output: {verify_result.stdout}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error configuring Windows IP: {str(e)}"
            }


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 5:
        print("Usage: python assign_ip_vmware.py <vmx_path> <ip_address> <gateway> <dns> [netmask]")
        sys.exit(1)
    
    vmx_path = sys.argv[1]
    ip_address = sys.argv[2]
    gateway = sys.argv[3]
    dns = sys.argv[4]
    netmask = sys.argv[5] if len(sys.argv) > 5 else "255.255.255.0"
    
    assigner = VMwareIPAssigner()
    result = assigner.assign_static_ip(vmx_path, ip_address, netmask, gateway, dns)
    
    if result['success']:
        print(f"✅ {result['message']}")
        sys.exit(0)
    else:
        print(f"❌ {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
