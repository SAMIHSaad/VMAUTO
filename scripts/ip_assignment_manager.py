#!/usr/bin/env python3
"""
IP Assignment Manager
Unified interface for assigning IP addresses to VMs across different hypervisors
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from assign_ip_vmware import VMwareIPAssigner
from assign_ip_nutanix import NutanixIPAssigner

class IPAssignmentManager:
    """Unified IP assignment manager for multiple hypervisors"""
    
    def __init__(self, hypervisor_config: Dict[str, Any] = None):
        """Initialize IP assignment manager
        
        Args:
            hypervisor_config: Configuration for hypervisors
        """
        self.config = hypervisor_config or {}
        self.vmware_assigner = None
        self.nutanix_assigner = None
        
        # Initialize assigners based on config
        self._initialize_assigners()
    
    def _initialize_assigners(self):
        """Initialize hypervisor-specific assigners"""
        # Initialize VMware assigner
        vmware_config = self.config.get('vmware', {})
        if vmware_config.get('enabled', True):
            vmrun_path = vmware_config.get('vmrun_path')
            self.vmware_assigner = VMwareIPAssigner(vmrun_path)
        
        # Initialize Nutanix assigner
        nutanix_config = self.config.get('nutanix', {})
        if nutanix_config.get('enabled', True):
            self.nutanix_assigner = NutanixIPAssigner(
                prism_central_ip=nutanix_config.get('prism_central_ip', '127.0.0.1'),
                username=nutanix_config.get('username', 'admin'),
                password=nutanix_config.get('password', 'password'),
                port=nutanix_config.get('port', 9441),
                use_ssl=nutanix_config.get('use_ssl', False),
                verify_ssl=nutanix_config.get('verify_ssl', False)
            )
    
    def assign_ip(self, provider: str, vm_identifier: str, ip_address: str, 
                  **kwargs) -> Dict[str, Any]:
        """Assign IP address to a VM
        
        Args:
            provider: Hypervisor provider ('vmware' or 'nutanix')
            vm_identifier: VM identifier (VMX path for VMware, VM name for Nutanix)
            ip_address: IP address to assign
            **kwargs: Additional parameters specific to each provider
            
        Returns:
            Dict with success status and message
        """
        try:
            if provider.lower() == 'vmware':
                return self._assign_vmware_ip(vm_identifier, ip_address, **kwargs)
            elif provider.lower() == 'nutanix':
                return self._assign_nutanix_ip(vm_identifier, ip_address, **kwargs)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported provider: {provider}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error assigning IP: {str(e)}"
            }
    
    def _assign_vmware_ip(self, vmx_path: str, ip_address: str, **kwargs) -> Dict[str, Any]:
        """Assign IP to VMware VM"""
        if not self.vmware_assigner:
            return {
                'success': False,
                'error': "VMware assigner not initialized"
            }
        
        netmask = kwargs.get('netmask', '255.255.255.0')
        gateway = kwargs.get('gateway', '192.168.122.1')
        dns = kwargs.get('dns', '8.8.8.8')
        
        return self.vmware_assigner.assign_static_ip(
            vmx_path, ip_address, netmask, gateway, dns
        )
    
    def _assign_nutanix_ip(self, vm_name: str, ip_address: str, **kwargs) -> Dict[str, Any]:
        """Assign IP to Nutanix VM"""
        if not self.nutanix_assigner:
            return {
                'success': False,
                'error': "Nutanix assigner not initialized"
            }
        
        subnet_uuid = kwargs.get('subnet_uuid')
        netmask = kwargs.get('netmask', '255.255.255.0')
        gateway = kwargs.get('gateway', '192.168.122.1')
        
        return self.nutanix_assigner.assign_static_ip(
            vm_name, ip_address, subnet_uuid, netmask, gateway
        )
    
    def assign_ip_after_clone(self, provider: str, vm_config: Dict[str, Any], 
                             vm_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assign IP after VM cloning
        
        Args:
            provider: Hypervisor provider
            vm_config: VM configuration including IP address
            vm_result: Result from VM cloning operation
            
        Returns:
            Dict with success status and message
        """
        try:
            ip_address = vm_config.get('ip_address')
            if not ip_address:
                return {
                    'success': False,
                    'error': "No IP address specified in VM configuration"
                }
            
            if not vm_result.get('success'):
                return {
                    'success': False,
                    'error': "Cannot assign IP to failed VM clone"
                }
            
            if provider.lower() == 'vmware':
                vmx_path = vm_result.get('vmx_path')
                if not vmx_path:
                    return {
                        'success': False,
                        'error': "VMX path not found in VM result"
                    }
                
                return self.assign_ip('vmware', vmx_path, ip_address)
                
            elif provider.lower() == 'nutanix':
                vm_name = vm_config.get('name') or vm_result.get('vm_name')
                if not vm_name:
                    return {
                        'success': False,
                        'error': "VM name not found"
                    }
                
                return self.assign_ip('nutanix', vm_name, ip_address)
            
            else:
                return {
                    'success': False,
                    'error': f"Unsupported provider: {provider}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error in post-clone IP assignment: {str(e)}"
            }


def load_hypervisor_config() -> Dict[str, Any]:
    """Load hypervisor configuration from file"""
    try:
        import json
        config_path = Path(__file__).parent.parent / 'hypervisor_config.json'
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('providers', {})
        
        # Default configuration
        return {
            'vmware': {
                'enabled': True,
                'vmrun_path': r'C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe'
            },
            'nutanix': {
                'enabled': True,
                'prism_central_ip': '127.0.0.1',
                'username': 'admin',
                'password': 'password',
                'port': 9441,
                'use_ssl': False,
                'verify_ssl': False
            }
        }
        
    except Exception as e:
        print(f"Error loading hypervisor config: {e}")
        return {}


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 4:
        print("Usage: python ip_assignment_manager.py <provider> <vm_identifier> <ip_address> [additional_args...]")
        print("  provider: 'vmware' or 'nutanix'")
        print("  vm_identifier: VMX path for VMware, VM name for Nutanix")
        print("  ip_address: IP address to assign")
        print("  additional_args: Provider-specific arguments")
        sys.exit(1)
    
    provider = sys.argv[1]
    vm_identifier = sys.argv[2]
    ip_address = sys.argv[3]
    
    # Parse additional arguments
    kwargs = {}
    for i in range(4, len(sys.argv), 2):
        if i + 1 < len(sys.argv):
            key = sys.argv[i].lstrip('-')
            value = sys.argv[i + 1]
            kwargs[key] = value
    
    # Load configuration and create manager
    config = load_hypervisor_config()
    manager = IPAssignmentManager(config)
    
    # Assign IP
    result = manager.assign_ip(provider, vm_identifier, ip_address, **kwargs)
    
    if result['success']:
        print(f"✅ {result['message']}")
        sys.exit(0)
    else:
        print(f"❌ {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()