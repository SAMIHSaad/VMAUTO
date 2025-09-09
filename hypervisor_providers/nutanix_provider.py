"""
Nutanix Hypervisor Provider
Handles Nutanix AHV operations using REST APIs
"""

import requests
import json
import base64
import time
from typing import Dict, List, Optional, Any
from urllib3.exceptions import InsecureRequestWarning
from .base_provider import BaseHypervisorProvider, VMConfig, VMInfo

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class NutanixProvider(BaseHypervisorProvider):
    """Nutanix AHV provider using REST APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.prism_central_ip = config.get('prism_central_ip')
        self.prism_element_ip = config.get('prism_element_ip')
        self.username = config.get('username')
        self.password = config.get('password')
        self.port = config.get('port', 9440)
        self.verify_ssl = config.get('verify_ssl', False)
        
        # API endpoints - Support HTTP pour mock server
        use_ssl = config.get('use_ssl', True)
        protocol = "https" if use_ssl else "http"
        self.pc_base_url = f"{protocol}://{self.prism_central_ip}:{self.port}/api/nutanix/v3"
        self.pe_base_url = f"{protocol}://{self.prism_element_ip}:{self.port}/PrismGateway/services/rest/v2.0" if self.prism_element_ip else None
        
        # Session
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        
        # Authentication
        auth_string = f"{self.username}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def connect(self) -> bool:
        """Connect to Nutanix cluster"""
        try:
            # Test connection to Prism Central
            response = self.session.post(f"{self.pc_base_url}/clusters/list", 
                                       json={"kind": "cluster"}, timeout=30)
            
            if response.status_code == 200:
                print("Successfully connected to Nutanix Prism Central")
                return True
            else:
                print(f"Failed to connect to Nutanix: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error connecting to Nutanix: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Nutanix"""
        try:
            self.session.close()
            return True
        except Exception as e:
            print(f"Error disconnecting from Nutanix: {e}")
            return False
    
    def create_vm(self, vm_config: VMConfig) -> Dict[str, Any]:
        """Create a new VM on Nutanix with fast template cloning and persistent data"""
        try:
            self.validate_config(vm_config)
            
            # Get cluster UUID
            cluster_uuid = self._get_cluster_uuid(vm_config.cluster)
            if not cluster_uuid:
                return {
                    'success': False,
                    'error': f"Cluster '{vm_config.cluster}' not found"
                }
            
            # Get network UUID
            network_uuid = self._get_network_uuid(vm_config.network)
            if not network_uuid:
                return {
                    'success': False,
                    'error': f"Network '{vm_config.network}' not found"
                }
            
            # If template is specified, use fast template cloning (like VMware)
            if vm_config.template:
                template_uuid = self._get_template_uuid(vm_config.template)
                if template_uuid:
                    print(f"Creating VM '{vm_config.name}' from template '{vm_config.template}' (fast mode)...")
                    return self._fast_clone_from_template(template_uuid, vm_config, cluster_uuid, network_uuid)
            
            # Prepare VM specification with persistent data optimization
            vm_spec = {
                "spec": {
                    "name": vm_config.name,
                    "description": f"VM created via Auto-Creation-VM - {vm_config.os_type} - Persistent Data Enabled",
                    "resources": {
                        "power_state": "ON",
                        "num_vcpus_per_socket": vm_config.cpu,
                        "num_sockets": 1,
                        "memory_size_mib": vm_config.ram,
                        "disk_list": [
                            {
                                "device_properties": {
                                    "device_type": "DISK",
                                    "disk_address": {
                                        "device_index": 0,
                                        "adapter_type": "SCSI"
                                    }
                                },
                                "disk_size_mib": vm_config.disk * 1024,
                                # Enable persistent data like VMware
                                "storage_config": {
                                    "flash_mode": "ON",  # Use flash storage for better performance
                                    "storage_container_reference": {
                                        "kind": "storage_container",
                                        "name": "default-container-" + str(hash(cluster_uuid))[:8]
                                    }
                                }
                            }
                        ],
                        "nic_list": [
                            {
                                "nic_type": "NORMAL_NIC",
                                "subnet_reference": {
                                    "kind": "subnet",
                                    "uuid": network_uuid
                                },
                                # Enable persistent MAC address
                                "mac_address": self._generate_persistent_mac()
                            }
                        ],
                        # VMware-like persistent settings
                        "guest_tools": {
                            "nutanix_guest_tools": {
                                "state": "ENABLED",
                                "version": "latest"
                            }
                        },
                        "hardware_clock_timezone": "UTC",
                        "machine_type": "PC"
                    },
                    "cluster_reference": {
                        "kind": "cluster",
                        "uuid": cluster_uuid
                    }
                },
                "api_version": "3.1.0",
                "metadata": {
                    "kind": "vm",
                    "categories": {
                        "Environment": ["Auto-Creation-VM"],
                        "OS": [vm_config.os_type],
                        "DataPersistence": ["Enabled"]
                    }
                }
            }
            
            # Create VM with optimized settings
            print(f"Creating VM '{vm_config.name}' on Nutanix with persistent data...")
            response = self.session.post(f"{self.pc_base_url}/vms", 
                                       json=vm_spec, timeout=120)  # Reduced timeout for faster response
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                
                # Wait for task completion with shorter timeout for faster creation
                if task_uuid:
                    success = self._wait_for_task(task_uuid, timeout=120)  # 2 minutes max
                    if success:
                        # Post-creation optimization for persistent data
                        self._optimize_vm_for_persistence(vm_config.name)
                        
                        return {
                            'success': True,
                            'vm_name': vm_config.name,
                            'provider': 'nutanix',
                            'task_uuid': task_uuid,
                            'message': f"VM '{vm_config.name}' created successfully with persistent data (under 2 minutes)",
                            'creation_time': '< 2 minutes',
                            'persistent_data': True
                        }
                
                return {
                    'success': False,
                    'error': "VM creation task failed or timed out (exceeded 2 minute limit)"
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create VM: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating VM: {str(e)}"
            }
    
    def clone_vm(self, source_vm: str, vm_config: VMConfig) -> Dict[str, Any]:
        """Clone an existing VM"""
        try:
            self.validate_config(vm_config)
            
            # Get source VM UUID
            source_vm_uuid = self._get_vm_uuid(source_vm)
            if not source_vm_uuid:
                return {
                    'success': False,
                    'error': f"Source VM '{source_vm}' not found"
                }
            
            # Clone VM
            clone_spec = {
                "spec_list": [
                    {
                        "name": vm_config.name,
                        "num_vcpus_per_socket": vm_config.cpu,
                        "num_sockets": 1,
                        "memory_size_mib": vm_config.ram
                    }
                ],
                "api_version": "3.1.0"
            }
            
            print(f"Cloning VM '{source_vm}' to '{vm_config.name}' on Nutanix...")
            response = self.session.post(f"{self.pc_base_url}/vms/{source_vm_uuid}/clone", 
                                       json=clone_spec, timeout=120)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                
                if task_uuid:
                    success = self._wait_for_task(task_uuid)
                    if success:
                        result = {
                            'success': True,
                            'vm_name': vm_config.name,
                            'provider': 'nutanix',
                            'task_uuid': task_uuid,
                            'message': f"VM '{vm_config.name}' cloned successfully from '{source_vm}'"
                        }
                        
                        # Configure IP address if provided
                        if vm_config.ip_address:
                            print(f"Configuring IP address {vm_config.ip_address} for VM...")
                            ip_result = self._assign_ip_address(vm_config.name, vm_config.ip_address)
                            if ip_result['success']:
                                print(f"✅ {ip_result['message']}")
                                result['ip_configured'] = True
                            else:
                                print(f"⚠️ IP assignment failed: {ip_result['error']}")
                                result['ip_configured'] = False
                                result['ip_error'] = ip_result['error']
                        
                        return result
                
                return {
                    'success': False,
                    'error': "VM clone task failed or timed out"
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to clone VM: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error cloning VM: {str(e)}"
            }
    
    def delete_vm(self, vm_name: str) -> bool:
        """Delete a VM"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return False
            
            # Stop VM first if running
            self.stop_vm(vm_name)
            
            # Delete VM
            response = self.session.delete(f"{self.pc_base_url}/vms/{vm_uuid}", timeout=120)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                if task_uuid:
                    return self._wait_for_task(task_uuid)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error deleting VM '{vm_name}': {e}")
            return False
    
    def start_vm(self, vm_name: str) -> bool:
        """Start a VM"""
        return self._change_vm_power_state(vm_name, "ON")
    
    def stop_vm(self, vm_name: str) -> bool:
        """Stop a VM"""
        return self._change_vm_power_state(vm_name, "OFF")
    
    def restart_vm(self, vm_name: str) -> bool:
        """Restart a VM"""
        return self.stop_vm(vm_name) and self.start_vm(vm_name)
    
    def get_vm_info(self, vm_name: str) -> Optional[VMInfo]:
        """Get VM information"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return None
            
            response = self.session.get(f"{self.pc_base_url}/vms/{vm_uuid}", timeout=30)
            
            if response.status_code == 200:
                vm_data = response.json()
                spec = vm_data.get('spec', {})
                resources = spec.get('resources', {})
                status = vm_data.get('status', {})
                
                # Get IP address
                ip_address = None
                nic_list = status.get('resources', {}).get('nic_list', [])
                if nic_list and nic_list[0].get('ip_endpoint_list'):
                    ip_address = nic_list[0]['ip_endpoint_list'][0].get('ip')
                
                return VMInfo(
                    name=vm_name,
                    uuid=vm_uuid,
                    state=resources.get('power_state', 'UNKNOWN').lower(),
                    cpu=resources.get('num_vcpus_per_socket', 0) * resources.get('num_sockets', 1),
                    ram=resources.get('memory_size_mib', 0),
                    disk=sum(disk.get('disk_size_mib', 0) for disk in resources.get('disk_list', [])) // 1024,
                    ip_address=ip_address,
                    hypervisor="nutanix",
                    cluster=spec.get('cluster_reference', {}).get('name')
                )
            
            return None
            
        except Exception as e:
            print(f"Error getting VM info for '{vm_name}': {e}")
            return None
    
    def list_vms(self) -> List[VMInfo]:
        """List all VMs"""
        try:
            vms = []
            
            # Get all VMs
            list_spec = {
                "kind": "vm",
                "length": 500
            }
            
            response = self.session.post(f"{self.pc_base_url}/vms/list", 
                                       json=list_spec, timeout=60)
            
            if response.status_code == 200:
                vm_list = response.json().get('entities', [])
                
                for vm_data in vm_list:
                    spec = vm_data.get('spec', {})
                    resources = spec.get('resources', {})
                    status = vm_data.get('status', {})
                    
                    # Get IP address
                    ip_address = None
                    nic_list = status.get('resources', {}).get('nic_list', [])
                    if nic_list and nic_list[0].get('ip_endpoint_list'):
                        ip_address = nic_list[0]['ip_endpoint_list'][0].get('ip')
                    
                    vm_info = VMInfo(
                        name=spec.get('name', 'Unknown'),
                        uuid=vm_data.get('metadata', {}).get('uuid', ''),
                        state=resources.get('power_state', 'UNKNOWN').lower(),
                        cpu=resources.get('num_vcpus_per_socket', 0) * resources.get('num_sockets', 1),
                        ram=resources.get('memory_size_mib', 0),
                        disk=sum(disk.get('disk_size_mib', 0) for disk in resources.get('disk_list', [])) // 1024,
                        ip_address=ip_address,
                        hypervisor="nutanix",
                        cluster=spec.get('cluster_reference', {}).get('name')
                    )
                    vms.append(vm_info)
            
            return vms
            
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []
    
    def get_templates(self) -> List[str]:
        """Get available VM templates - Only return the original 2 VMs"""
        return ["Windows Server 2019", "Ubuntu 64-bit (3)"]
    
    def get_clusters(self) -> List[str]:
        """Get available clusters"""
        try:
            clusters = []
            
            list_spec = {
                "kind": "cluster",
                "length": 100
            }
            
            response = self.session.post(f"{self.pc_base_url}/clusters/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                cluster_list = response.json().get('entities', [])
                
                for cluster in cluster_list:
                    spec = cluster.get('spec', {})
                    clusters.append(spec.get('name', 'Unknown'))
            
            return clusters
            
        except Exception as e:
            print(f"Error getting clusters: {e}")
            return []
    
    def get_networks(self) -> List[str]:
        """Get available networks"""
        try:
            networks = []
            
            list_spec = {
                "kind": "subnet",
                "length": 100
            }
            
            response = self.session.post(f"{self.pc_base_url}/subnets/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                subnet_list = response.json().get('entities', [])
                
                for subnet in subnet_list:
                    spec = subnet.get('spec', {})
                    networks.append(spec.get('name', 'Unknown'))
            
            return networks
            
        except Exception as e:
            print(f"Error getting networks: {e}")
            return []
    
    def create_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Create a VM snapshot"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return False
            
            snapshot_spec = {
                "spec": {
                    "name": snapshot_name,
                    "description": f"Snapshot of {vm_name} created by Auto-Creation-VM"
                },
                "api_version": "3.1.0",
                "metadata": {
                    "kind": "vm_snapshot"
                }
            }
            
            response = self.session.post(f"{self.pc_base_url}/vms/{vm_uuid}/snapshots", 
                                       json=snapshot_spec, timeout=120)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                if task_uuid:
                    return self._wait_for_task(task_uuid)
            
            return False
            
        except Exception as e:
            print(f"Error creating snapshot for VM '{vm_name}': {e}")
            return False
    
    def restore_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Restore a VM snapshot"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return False
            
            # Get snapshot UUID
            snapshot_uuid = self._get_snapshot_uuid(vm_uuid, snapshot_name)
            if not snapshot_uuid:
                return False
            
            restore_spec = {
                "api_version": "3.1.0"
            }
            
            response = self.session.post(f"{self.pc_base_url}/vms/{vm_uuid}/snapshots/{snapshot_uuid}/restore", 
                                       json=restore_spec, timeout=300)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                if task_uuid:
                    return self._wait_for_task(task_uuid)
            
            return False
            
        except Exception as e:
            print(f"Error restoring snapshot for VM '{vm_name}': {e}")
            return False
    
    def delete_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Delete a VM snapshot"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return False
            
            # Get snapshot UUID
            snapshot_uuid = self._get_snapshot_uuid(vm_uuid, snapshot_name)
            if not snapshot_uuid:
                return False
            
            response = self.session.delete(f"{self.pc_base_url}/vms/{vm_uuid}/snapshots/{snapshot_uuid}", 
                                         timeout=300)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                if task_uuid:
                    return self._wait_for_task(task_uuid)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error deleting snapshot for VM '{vm_name}': {e}")
            return False
    
    # Helper methods
    
    def _get_vm_uuid(self, vm_name: str) -> Optional[str]:
        """Get VM UUID by name"""
        try:
            list_spec = {
                "kind": "vm",
                "filter": f"vm_name=={vm_name}",
                "length": 1
            }
            
            response = self.session.post(f"{self.pc_base_url}/vms/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                entities = response.json().get('entities', [])
                if entities:
                    return entities[0].get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting VM UUID for '{vm_name}': {e}")
            return None
    
    def _get_cluster_uuid(self, cluster_name: str) -> Optional[str]:
        """Get cluster UUID by name"""
        try:
            list_spec = {
                "kind": "cluster",
                "filter": f"name=={cluster_name}",
                "length": 1
            }
            
            response = self.session.post(f"{self.pc_base_url}/clusters/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                entities = response.json().get('entities', [])
                if entities:
                    return entities[0].get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting cluster UUID for '{cluster_name}': {e}")
            return None
    
    def _get_network_uuid(self, network_name: str) -> Optional[str]:
        """Get network UUID by name"""
        try:
            list_spec = {
                "kind": "subnet",
                "filter": f"name=={network_name}",
                "length": 1
            }
            
            response = self.session.post(f"{self.pc_base_url}/subnets/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                entities = response.json().get('entities', [])
                if entities:
                    return entities[0].get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting network UUID for '{network_name}': {e}")
            return None
    
    def _assign_ip_address(self, vm_name: str, ip_address: str) -> Dict[str, Any]:
        """Assign IP address to VM using the IP assignment script"""
        try:
            # Import the IP assignment manager
            import os
            import sys
            from pathlib import Path
            
            # Add scripts directory to path
            base_dir = Path(os.getcwd())
            scripts_dir = base_dir / 'scripts'
            sys.path.append(str(scripts_dir))
            
            from assign_ip_nutanix import NutanixIPAssigner
            
            # Create IP assigner with current configuration
            assigner = NutanixIPAssigner(
                prism_central_ip=self.prism_central_ip,
                username=self.username,
                password=self.password,
                port=self.port,
                use_ssl=self.use_ssl,
                verify_ssl=self.verify_ssl
            )
            
            # Assign IP address
            result = assigner.assign_static_ip(vm_name, ip_address)
            
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
    
    def _get_template_uuid(self, template_name: str) -> Optional[str]:
        """Get template UUID by name"""
        try:
            list_spec = {
                "kind": "image",
                "filter": f"name=={template_name}",
                "length": 1
            }
            
            response = self.session.post(f"{self.pc_base_url}/images/list", 
                                       json=list_spec, timeout=30)
            
            if response.status_code == 200:
                entities = response.json().get('entities', [])
                if entities:
                    return entities[0].get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting template UUID for '{template_name}': {e}")
            return None
    
    def _get_snapshot_uuid(self, vm_uuid: str, snapshot_name: str) -> Optional[str]:
        """Get snapshot UUID by name"""
        try:
            response = self.session.get(f"{self.pc_base_url}/vms/{vm_uuid}/snapshots", timeout=30)
            
            if response.status_code == 200:
                snapshots = response.json().get('entities', [])
                for snapshot in snapshots:
                    if snapshot.get('spec', {}).get('name') == snapshot_name:
                        return snapshot.get('metadata', {}).get('uuid')
            
            return None
            
        except Exception as e:
            print(f"Error getting snapshot UUID for '{snapshot_name}': {e}")
            return None
    
    def _change_vm_power_state(self, vm_name: str, power_state: str) -> bool:
        """Change VM power state"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return False
            
            # Get current VM spec
            response = self.session.get(f"{self.pc_base_url}/vms/{vm_uuid}", timeout=30)
            if response.status_code != 200:
                return False
            
            vm_data = response.json()
            
            # Update power state
            vm_data['spec']['resources']['power_state'] = power_state
            
            # Update VM
            response = self.session.put(f"{self.pc_base_url}/vms/{vm_uuid}", 
                                      json=vm_data, timeout=300)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                if task_uuid:
                    return self._wait_for_task(task_uuid)
            
            return False
            
        except Exception as e:
            print(f"Error changing power state for VM '{vm_name}': {e}")
            return False
    
    def _wait_for_task(self, task_uuid: str, timeout: int = 120) -> bool:
        """Wait for a task to complete"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                response = self.session.get(f"{self.pc_base_url}/tasks/{task_uuid}", timeout=30)
                
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get('status')
                    
                    if status == 'SUCCEEDED':
                        return True
                    elif status == 'FAILED':
                        error_detail = task_data.get('error_detail', 'Unknown error')
                        print(f"Task failed: {error_detail}")
                        return False
                    
                    # Task still running, wait
                    time.sleep(5)
                else:
                    print(f"Error checking task status: {response.status_code}")
                    return False
            
            print(f"Task {task_uuid} timed out")
            return False
            
        except Exception as e:
            print(f"Error waiting for task {task_uuid}: {e}")
            return False
    
    def _clone_from_template(self, template_uuid: str, vm_config: VMConfig, vm_spec: Dict) -> Dict[str, Any]:
        """Clone VM from template"""
        try:
            # Modify spec to use template as source
            vm_spec['spec']['resources']['disk_list'][0]['data_source_reference'] = {
                'kind': 'image',
                'uuid': template_uuid
            }
            
            # Create VM from template
            response = self.session.post(f"{self.pc_base_url}/vms", 
                                       json=vm_spec, timeout=300)
            
            if response.status_code == 202:
                task_uuid = response.json().get('status', {}).get('execution_context', {}).get('task_uuid')
                
                if task_uuid:
                    success = self._wait_for_task(task_uuid)
                    if success:
                        return {
                            'success': True,
                            'vm_name': vm_config.name,
                            'provider': 'nutanix',
                            'task_uuid': task_uuid,
                            'message': f"VM '{vm_config.name}' created from template '{vm_config.template}'"
                        }
                
                return {
                    'success': False,
                    'error': "VM creation from template task failed or timed out"
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create VM from template: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating VM from template: {str(e)}"
            }
    
    def open_console(self, vm_name: str) -> Dict[str, Any]:
        """Open VM console (web-based for Nutanix)"""
        try:
            vm_uuid = self._get_vm_uuid(vm_name)
            if not vm_uuid:
                return {
                    'success': False,
                    'error': f"VM '{vm_name}' not found"
                }
            
            # For Nutanix, we'll provide the web console URL
            # In a real environment, this would be the Prism Central console URL
            console_url = f"https://{self.pc_ip}:9440/console/vm/{vm_uuid}"
            
            return {
                'success': True,
                'console_type': 'web',
                'console_url': console_url,
                'message': f"Web console URL for VM '{vm_name}': {console_url}",
                'instructions': "Open this URL in your browser to access the VM console. You may need to accept SSL certificates."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting console for VM '{vm_name}': {str(e)}"
            }