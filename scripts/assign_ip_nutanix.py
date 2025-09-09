#!/usr/bin/env python3
"""
Nutanix IP Assignment Script
Assigns IP addresses to Nutanix VMs after cloning
"""

import sys
import time
import requests
import json
from typing import Dict, Any, Optional

class NutanixIPAssigner:
    """Handles IP assignment for Nutanix VMs"""
    
    def __init__(self, prism_central_ip: str, username: str, password: str, 
                 port: int = 9440, use_ssl: bool = True, verify_ssl: bool = False):
        """Initialize Nutanix IP assigner
        
        Args:
            prism_central_ip: Prism Central IP address
            username: Username for authentication
            password: Password for authentication
            port: Port number (default: 9440)
            use_ssl: Use HTTPS (default: True)
            verify_ssl: Verify SSL certificates (default: False)
        """
        self.prism_central_ip = prism_central_ip
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        
        # Setup session
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Base URLs
        protocol = "https" if use_ssl else "http"
        self.pc_base_url = f"{protocol}://{prism_central_ip}:{port}/api/nutanix/v3"
    
    def assign_static_ip(self, vm_name: str, ip_address: str, subnet_uuid: str = None,
                        netmask: str = "255.255.255.0", gateway: str = "192.168.122.1") -> Dict[str, Any]:
        """Assign static IP to a Nutanix VM
        
        Args:
            vm_name: Name of the VM
            ip_address: IP address to assign
            subnet_uuid: UUID of the subnet (will auto-detect if not provided)
            netmask: Network mask (default: 255.255.255.0)
            gateway: Gateway IP (default: 192.168.122.1)
            
        Returns:
            Dict with success status and message
        """
        try:
            print(f"Assigning IP {ip_address} to Nutanix VM: {vm_name}")
            
            # Get VM UUID
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return {
                    'success': False,
                    'error': f"VM '{vm_name}' not found"
                }
            
            # Get VM details
            vm_details = self._get_vm_details(vm_uuid)
            if not vm_details:
                return {
                    'success': False,
                    'error': f"Failed to get VM details for '{vm_name}'"
                }
            
            # Get subnet UUID if not provided
            if not subnet_uuid:
                subnet_uuid = self._get_default_subnet_uuid()
                if not subnet_uuid:
                    return {
                        'success': False,
                        'error': "No subnet found for IP assignment"
                    }
            
            # Update VM network configuration
            result = self._update_vm_network(vm_uuid, vm_details, ip_address, subnet_uuid)
            
            if result['success']:
                # Wait for VM to be updated
                time.sleep(10)
                
                # Verify IP assignment
                verify_result = self._verify_ip_assignment(vm_uuid, ip_address)
                if verify_result:
                    return {
                        'success': True,
                        'message': f"Successfully assigned IP {ip_address} to VM '{vm_name}'"
                    }
                else:
                    return {
                        'success': False,
                        'error': f"IP assignment verification failed for VM '{vm_name}'"
                    }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error assigning IP: {str(e)}"
            }
    
    def _get_vm_uuid(self, vm_name: str) -> Optional[str]:
        """Get VM UUID by name"""
        try:
            # List VMs and find by name
            list_spec = {
                "kind": "vm",
                "filter": f"vm_name=={vm_name}"
            }
            
            response = self.session.post(f"{self.pc_base_url}/vms/list", 
                                       json=list_spec, timeout=60)
            
            if response.status_code == 200:
                vms = response.json().get('entities', [])
                for vm in vms:
                    if vm.get('spec', {}).get('name') == vm_name:
                        return vm.get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting VM UUID: {e}")
            return None
    
    def _get_vm_details(self, vm_uuid: str) -> Optional[Dict[str, Any]]:
        """Get VM details"""
        try:
            response = self.session.get(f"{self.pc_base_url}/vms/{vm_uuid}", timeout=60)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            print(f"Error getting VM details: {e}")
            return None
    
    def _get_default_subnet_uuid(self) -> Optional[str]:
        """Get default subnet UUID"""
        try:
            # List subnets
            list_spec = {
                "kind": "subnet"
            }
            
            response = self.session.post(f"{self.pc_base_url}/subnets/list", 
                                       json=list_spec, timeout=60)
            
            if response.status_code == 200:
                subnets = response.json().get('entities', [])
                if subnets:
                    # Return first available subnet
                    return subnets[0].get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting subnet UUID: {e}")
            return None
    
    def _update_vm_network(self, vm_uuid: str, vm_details: Dict[str, Any], 
                          ip_address: str, subnet_uuid: str) -> Dict[str, Any]:
        """Update VM network configuration"""
        try:
            # Prepare update spec
            update_spec = {
                "spec": vm_details.get('spec', {}),
                "api_version": "3.1.0",
                "metadata": vm_details.get('metadata', {})
            }
            
            # Update network configuration
            nic_list = update_spec['spec'].get('resources', {}).get('nic_list', [])
            
            if not nic_list:
                # Add new NIC if none exists
                nic_list.append({
                    "nic_type": "NORMAL_NIC",
                    "is_connected": True,
                    "subnet_reference": {
                        "kind": "subnet",
                        "uuid": subnet_uuid
                    },
                    "ip_endpoint_list": [
                        {
                            "ip": ip_address,
                            "type": "ASSIGNED"
                        }
                    ]
                })
            else:
                # Update existing NIC
                for nic in nic_list:
                    nic['subnet_reference'] = {
                        "kind": "subnet",
                        "uuid": subnet_uuid
                    }
                    nic['ip_endpoint_list'] = [
                        {
                            "ip": ip_address,
                            "type": "ASSIGNED"
                        }
                    ]
                    break
            
            update_spec['spec']['resources']['nic_list'] = nic_list
            
            # Send update request
            response = self.session.put(f"{self.pc_base_url}/vms/{vm_uuid}", 
                                      json=update_spec, timeout=120)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                
                if task_uuid:
                    success = self._wait_for_task(task_uuid)
                    if success:
                        return {
                            'success': True,
                            'message': f"VM network updated successfully"
                        }
                
                return {
                    'success': False,
                    'error': "VM network update task failed or timed out"
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to update VM network: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error updating VM network: {str(e)}"
            }
    
    def _wait_for_task(self, task_uuid: str, timeout: int = 300) -> bool:
        """Wait for task completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.pc_base_url}/tasks/{task_uuid}", timeout=30)
                
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get('status')
                    
                    if status == 'SUCCEEDED':
                        return True
                    elif status == 'FAILED':
                        print(f"Task failed: {task_data.get('error_detail', 'Unknown error')}")
                        return False
                
            except Exception as e:
                print(f"Error checking task status: {e}")
            
            time.sleep(10)
        
        print("Task timed out")
        return False
    
    def _verify_ip_assignment(self, vm_uuid: str, expected_ip: str) -> bool:
        """Verify IP assignment"""
        try:
            vm_details = self._get_vm_details(vm_uuid)
            if not vm_details:
                return False
            
            nic_list = vm_details.get('spec', {}).get('resources', {}).get('nic_list', [])
            
            for nic in nic_list:
                ip_endpoint_list = nic.get('ip_endpoint_list', [])
                for endpoint in ip_endpoint_list:
                    if endpoint.get('ip') == expected_ip:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error verifying IP assignment: {e}")
            return False


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 6:
        print("Usage: python assign_ip_nutanix.py <prism_central_ip> <username> <password> <vm_name> <ip_address> [subnet_uuid]")
        sys.exit(1)
    
    prism_central_ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    vm_name = sys.argv[4]
    ip_address = sys.argv[5]
    subnet_uuid = sys.argv[6] if len(sys.argv) > 6 else None
    
    assigner = NutanixIPAssigner(prism_central_ip, username, password, 
                                port=9441, use_ssl=False, verify_ssl=False)
    result = assigner.assign_static_ip(vm_name, ip_address, subnet_uuid)
    
    if result['success']:
        print(f"✅ {result['message']}")
        sys.exit(0)
    else:
        print(f"❌ {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()