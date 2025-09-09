#!/usr/bin/env python3
"""
VM Manager - Comprehensive VM management tool with multi-hypervisor support
Handles VM creation, organization, backup, and maintenance operations for VMware and Nutanix.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig, VMInfo
from vm_organizer import VMOrganizer
from ip_manager import get_available_ip

class VMManager:
    """Comprehensive VM management class with multi-hypervisor support."""
    
    def __init__(self, base_directory: str = None, config_file: str = None):
        """Initialize VM Manager.
        
        Args:
            base_directory: Base directory for VM operations
            config_file: Path to hypervisor configuration file
        """
        self.base_directory = Path(base_directory) if base_directory else Path.cwd()
        self.hypervisor_manager = HypervisorManager(config_file)
        self.organizer = VMOrganizer(str(self.base_directory))
    
    def create_vm(self, vm_name: str, os_type: str = "linux", cpu: str = "2", 
                  ram: str = "2048", ssd: str = "20", provider: str = None,
                  cluster: str = None, network: str = None, template: str = None,
                  auto_organize: bool = True) -> bool:
        """Create a new VM using specified or default hypervisor.
        
        Args:
            vm_name: Name of the VM
            os_type: Operating system type
            cpu: CPU count
            ram: RAM in MB
            ssd: SSD size in GB
            provider: Hypervisor provider ('vmware' or 'nutanix')
            cluster: Target cluster (for Nutanix)
            network: Target network
            template: Template to use (optional)
            auto_organize: Whether to automatically organize files after creation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Creating VM: {vm_name} on {provider or 'default'} hypervisor")
            
            # Get available IP
            ip_address = get_available_ip()
            if not ip_address:
                print("Warning: No available IP addresses")
            
            # Create VM configuration
            vm_config = VMConfig(
                name=vm_name,
                cpu=int(cpu),
                ram=int(ram),
                disk=int(ssd),
                os_type=os_type,
                network=network,
                ip_address=ip_address,
                template=template,
                cluster=cluster
            )
            
            # Create VM using hypervisor manager
            result = self.hypervisor_manager.create_vm(vm_config, provider)
            
            if result.get('success'):
                print(f"VM '{vm_name}' created successfully")
                
                # Organize files if requested and using VMware
                if auto_organize and result.get('provider') == 'vmware':
                    vm_config_dict = {
                        'vm_name': vm_name,
                        'os_type': os_type,
                        'cpu': cpu,
                        'ram': ram,
                        'ssd': ssd,
                        'ip_address': ip_address,
                        'creation_method': 'vm_manager_script',
                        'provider': result.get('provider')
                    }
                    
                    organized_dir = self.organizer.organize_vm_files(vm_name, vm_config_dict)
                    print(f"VM files organized in: {organized_dir}")
                
                return True
            else:
                print(f"Failed to create VM: {result.get('error')}")
                return False
            
        except Exception as e:
            print(f"Error creating VM: {str(e)}")
            return False
    
    def clone_vm(self, vm_name: str, source_vm: str, cpu: str = "2", 
                 ram: str = "2048", ssd: str = "20", provider: str = None,
                 cluster: str = None, network: str = None,
                 gateway: str = None, dns: str = None,
                 auto_organize: bool = True) -> bool:
        """Clone a VM from an existing VM.
        
        Args:
            vm_name: Name of the new VM
            source_vm: Name or path of the source VM
            cpu: CPU count
            ram: RAM in MB
            ssd: SSD size in GB
            provider: Hypervisor provider ('vmware' or 'nutanix')
            cluster: Target cluster (for Nutanix)
            network: Target network
            gateway: Gateway IP address
            dns: DNS server IP address
            auto_organize: Whether to automatically organize files after creation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Cloning VM '{vm_name}' from '{source_vm}' on {provider or 'default'} hypervisor")
            
            # Get available IP
            ip_address = get_available_ip()
            if not ip_address:
                print("Warning: No available IP addresses")
            
            # Create VM configuration
            vm_config = VMConfig(
                name=vm_name,
                cpu=int(cpu),
                ram=int(ram),
                disk=int(ssd),
                os_type='unknown',  # Will be determined from source
                network=network,
                ip_address=ip_address,
                gateway=gateway,
                dns=dns,
                cluster=cluster
            )
            
            # Clone VM using hypervisor manager
            result = self.hypervisor_manager.clone_vm(source_vm, vm_config, provider)
            
            if result.get('success'):
                print(f"VM '{vm_name}' cloned successfully")
                
                # Organize files if requested and using VMware
                if auto_organize and result.get('provider') == 'vmware':
                    vm_config_dict = {
                        'vm_name': vm_name,
                        'os_type': 'cloned',
                        'cpu': cpu,
                        'ram': ram,
                        'ssd': ssd,
                        'ip_address': ip_address,
                        'creation_method': 'vm_manager_clone',
                        'provider': result.get('provider'),
                        'source_vm': source_vm
                    }
                    
                    organized_dir = self.organizer.organize_vm_files(vm_name, vm_config_dict)
                    print(f"VM files organized in: {organized_dir}")
                
                return True
            else:
                print(f"Failed to clone VM: {result.get('error')}")
                return False
            
        except Exception as e:
            print(f"Error cloning VM: {str(e)}")
            return False
    
    def delete_vm(self, vm_name: str, provider: str = None) -> bool:
        """Delete a VM.
        
        Args:
            vm_name: Name of the VM
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.delete_vm(vm_name, provider)
            if success:
                print(f"VM '{vm_name}' deleted successfully")
            else:
                print(f"Failed to delete VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error deleting VM '{vm_name}': {str(e)}")
            return False
    
    def start_vm(self, vm_name: str, provider: str = None) -> bool:
        """Start a VM.
        
        Args:
            vm_name: Name of the VM
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.start_vm(vm_name, provider)
            if success:
                print(f"VM '{vm_name}' started successfully")
            else:
                print(f"Failed to start VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error starting VM '{vm_name}': {str(e)}")
            return False
    
    def stop_vm(self, vm_name: str, provider: str = None) -> bool:
        """Stop a VM.
        
        Args:
            vm_name: Name of the VM
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.stop_vm(vm_name, provider)
            if success:
                print(f"VM '{vm_name}' stopped successfully")
            else:
                print(f"Failed to stop VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error stopping VM '{vm_name}': {str(e)}")
            return False
    
    def restart_vm(self, vm_name: str, provider: str = None) -> bool:
        """Restart a VM.
        
        Args:
            vm_name: Name of the VM
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.restart_vm(vm_name, provider)
            if success:
                print(f"VM '{vm_name}' restarted successfully")
            else:
                print(f"Failed to restart VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error restarting VM '{vm_name}': {str(e)}")
            return False
    
    def list_vms(self, provider: str = None, detailed: bool = False) -> list:
        """List all VMs.
        
        Args:
            provider: Hypervisor provider ('vmware' or 'nutanix') or None for all
            detailed: Show detailed information
            
        Returns:
            List of VM information
        """
        try:
            vms = self.hypervisor_manager.list_vms(provider)
            
            if not vms:
                print("No VMs found.")
                return []
            
            print(f"Found {len(vms)} VM(s):")
            for vm in vms:
                print(f"\n- {vm.name} ({vm.hypervisor})")
                print(f"  State: {vm.state}")
                print(f"  UUID: {vm.uuid}")
                
                if detailed:
                    print(f"  CPU: {vm.cpu}")
                    print(f"  RAM: {vm.ram} MB")
                    print(f"  Disk: {vm.disk} GB")
                    if vm.ip_address:
                        print(f"  IP: {vm.ip_address}")
                    if vm.cluster:
                        print(f"  Cluster: {vm.cluster}")
            
            return vms
            
        except Exception as e:
            print(f"Error listing VMs: {str(e)}")
            return []
    
    def get_vm_info(self, vm_name: str, provider: str = None) -> VMInfo:
        """Get detailed information about a VM.
        
        Args:
            vm_name: Name of the VM
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            VM information or None
        """
        try:
            vm_info = self.hypervisor_manager.get_vm_info(vm_name, provider)
            
            if vm_info:
                print(f"VM Information for '{vm_name}':")
                print(f"  Hypervisor: {vm_info.hypervisor}")
                print(f"  State: {vm_info.state}")
                print(f"  UUID: {vm_info.uuid}")
                print(f"  CPU: {vm_info.cpu}")
                print(f"  RAM: {vm_info.ram} MB")
                print(f"  Disk: {vm_info.disk} GB")
                if vm_info.ip_address:
                    print(f"  IP: {vm_info.ip_address}")
                if vm_info.cluster:
                    print(f"  Cluster: {vm_info.cluster}")
            else:
                print(f"VM '{vm_name}' not found")
            
            return vm_info
            
        except Exception as e:
            print(f"Error getting VM info: {str(e)}")
            return None
    
    def create_snapshot(self, vm_name: str, snapshot_name: str, provider: str = None) -> bool:
        """Create a VM snapshot.
        
        Args:
            vm_name: Name of the VM
            snapshot_name: Name of the snapshot
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.create_snapshot(vm_name, snapshot_name, provider)
            if success:
                print(f"Snapshot '{snapshot_name}' created for VM '{vm_name}'")
            else:
                print(f"Failed to create snapshot '{snapshot_name}' for VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error creating snapshot: {str(e)}")
            return False
    
    def restore_snapshot(self, vm_name: str, snapshot_name: str, provider: str = None) -> bool:
        """Restore a VM snapshot.
        
        Args:
            vm_name: Name of the VM
            snapshot_name: Name of the snapshot
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.restore_snapshot(vm_name, snapshot_name, provider)
            if success:
                print(f"Snapshot '{snapshot_name}' restored for VM '{vm_name}'")
            else:
                print(f"Failed to restore snapshot '{snapshot_name}' for VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error restoring snapshot: {str(e)}")
            return False
    
    def delete_snapshot(self, vm_name: str, snapshot_name: str, provider: str = None) -> bool:
        """Delete a VM snapshot.
        
        Args:
            vm_name: Name of the VM
            snapshot_name: Name of the snapshot
            provider: Hypervisor provider ('vmware' or 'nutanix')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.hypervisor_manager.delete_snapshot(vm_name, snapshot_name, provider)
            if success:
                print(f"Snapshot '{snapshot_name}' deleted for VM '{vm_name}'")
            else:
                print(f"Failed to delete snapshot '{snapshot_name}' for VM '{vm_name}'")
            return success
            
        except Exception as e:
            print(f"Error deleting snapshot: {str(e)}")
            return False
    
    def get_providers_status(self) -> dict:
        """Get status of all hypervisor providers."""
        return self.hypervisor_manager.get_provider_status()
    
    def get_templates(self, provider: str = None) -> dict:
        """Get available templates from providers."""
        return self.hypervisor_manager.get_templates(provider)
    
    def get_clusters(self, provider: str = None) -> dict:
        """Get available clusters from providers."""
        return self.hypervisor_manager.get_clusters(provider)
    
    def get_networks(self, provider: str = None) -> dict:
        """Get available networks from providers."""
        return self.hypervisor_manager.get_networks(provider)
    
    def organize_vm(self, vm_name: str, vm_config: dict = None) -> bool:
        """Organize an existing VM (VMware only).
        
        Args:
            vm_name: Name of the VM
            vm_config: VM configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if vm_config is None:
                vm_config = {
                    'vm_name': vm_name,
                    'os_type': 'unknown',
                    'cpu': 'unknown',
                    'ram': 'unknown',
                    'ssd': 'unknown',
                    'organization_date': datetime.now().isoformat()
                }
            
            organized_dir = self.organizer.organize_vm_files(vm_name, vm_config)
            print(f"VM '{vm_name}' organized in: {organized_dir}")
            return True
            
        except Exception as e:
            print(f"Error organizing VM '{vm_name}': {str(e)}")
            return False

def main():
    """Main function for the VM manager script."""
    parser = argparse.ArgumentParser(description="Comprehensive VM Management Tool with Multi-Hypervisor Support")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Global options
    parser.add_argument('--base-dir', help='Base directory for operations')
    parser.add_argument('--config', help='Hypervisor configuration file')
    parser.add_argument('--provider', choices=['vmware', 'nutanix'], help='Hypervisor provider')
    
    # Create VM command
    create_parser = subparsers.add_parser('create', help='Create a new VM')
    create_parser.add_argument('vm_name', help='Name of the VM')
    create_parser.add_argument('--os-type', default='linux', help='OS type (default: linux)')
    create_parser.add_argument('--cpu', default='2', help='CPU count (default: 2)')
    create_parser.add_argument('--ram', default='2048', help='RAM in MB (default: 2048)')
    create_parser.add_argument('--ssd', default='20', help='SSD size in GB (default: 20)')
    create_parser.add_argument('--cluster', help='Target cluster (for Nutanix)')
    create_parser.add_argument('--network', help='Target network')
    create_parser.add_argument('--template', help='Template to use')
    create_parser.add_argument('--no-organize', action='store_true', help='Skip file organization')
    
    # Clone VM command
    clone_parser = subparsers.add_parser('clone', help='Clone a VM')
    clone_parser.add_argument('vm_name', help='Name of the new VM')
    clone_parser.add_argument('--source-vm', required=True, help='Source VM name or path')
    clone_parser.add_argument('--cpu', default='2', help='CPU count (default: 2)')
    clone_parser.add_argument('--ram', default='2048', help='RAM in MB (default: 2048)')
    clone_parser.add_argument('--ssd', default='20', help='SSD size in GB (default: 20)')
    clone_parser.add_argument('--cluster', help='Target cluster (for Nutanix)')
    clone_parser.add_argument('--network', help='Target network')
    clone_parser.add_argument('--gateway', help='Gateway IP address')
    clone_parser.add_argument('--dns', help='DNS server IP address')
    clone_parser.add_argument('--no-organize', action='store_true', help='Skip file organization')
    
    # VM control commands
    start_parser = subparsers.add_parser('start', help='Start a VM')
    start_parser.add_argument('vm_name', help='Name of the VM')
    
    stop_parser = subparsers.add_parser('stop', help='Stop a VM')
    stop_parser.add_argument('vm_name', help='Name of the VM')
    
    restart_parser = subparsers.add_parser('restart', help='Restart a VM')
    restart_parser.add_argument('vm_name', help='Name of the VM')
    
    delete_parser = subparsers.add_parser('delete', help='Delete a VM')
    delete_parser.add_argument('vm_name', help='Name of the VM')
    delete_parser.add_argument('--force', action='store_true', help='Force deletion without confirmation')
    
    # Info commands
    list_parser = subparsers.add_parser('list', help='List all VMs')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    
    info_parser = subparsers.add_parser('info', help='Get VM information')
    info_parser.add_argument('vm_name', help='Name of the VM')
    
    # Snapshot commands
    snapshot_parser = subparsers.add_parser('snapshot', help='Snapshot operations')
    snapshot_subparsers = snapshot_parser.add_subparsers(dest='snapshot_action', help='Snapshot actions')
    
    create_snap_parser = snapshot_subparsers.add_parser('create', help='Create snapshot')
    create_snap_parser.add_argument('vm_name', help='Name of the VM')
    create_snap_parser.add_argument('snapshot_name', help='Name of the snapshot')
    
    restore_snap_parser = snapshot_subparsers.add_parser('restore', help='Restore snapshot')
    restore_snap_parser.add_argument('vm_name', help='Name of the VM')
    restore_snap_parser.add_argument('snapshot_name', help='Name of the snapshot')
    
    delete_snap_parser = snapshot_subparsers.add_parser('delete', help='Delete snapshot')
    delete_snap_parser.add_argument('vm_name', help='Name of the VM')
    delete_snap_parser.add_argument('snapshot_name', help='Name of the snapshot')
    
    # Status and configuration commands
    status_parser = subparsers.add_parser('status', help='Show hypervisor providers status')
    
    templates_parser = subparsers.add_parser('templates', help='List available templates')
    
    clusters_parser = subparsers.add_parser('clusters', help='List available clusters')
    
    networks_parser = subparsers.add_parser('networks', help='List available networks')
    
    # Organize VM command (VMware only)
    organize_parser = subparsers.add_parser('organize', help='Organize existing VM files (VMware only)')
    organize_parser.add_argument('vm_name', help='Name of the VM')
    organize_parser.add_argument('--cpu', help='CPU count')
    organize_parser.add_argument('--ram', help='RAM in MB')
    organize_parser.add_argument('--ssd', help='SSD size in GB')
    organize_parser.add_argument('--os-type', help='Operating system type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize VM Manager
    manager = VMManager(args.base_dir, args.config)
    
    try:
        if args.command == 'create':
            success = manager.create_vm(
                args.vm_name,
                args.os_type,
                args.cpu,
                args.ram,
                args.ssd,
                args.provider,
                args.cluster,
                args.network,
                args.template,
                not args.no_organize
            )
            return 0 if success else 1
            
        elif args.command == 'clone':
            success = manager.clone_vm(
                args.vm_name,
                args.source_vm,
                args.cpu,
                args.ram,
                args.ssd,
                args.provider,
                args.cluster,
                args.network,
                args.gateway,
                args.dns,
                not args.no_organize
            )
            return 0 if success else 1
            
        elif args.command == 'start':
            success = manager.start_vm(args.vm_name, args.provider)
            return 0 if success else 1
            
        elif args.command == 'stop':
            success = manager.stop_vm(args.vm_name, args.provider)
            return 0 if success else 1
            
        elif args.command == 'restart':
            success = manager.restart_vm(args.vm_name, args.provider)
            return 0 if success else 1
            
        elif args.command == 'delete':
            if not args.force:
                confirm = input(f"Are you sure you want to delete VM '{args.vm_name}'? (y/N): ")
                if confirm.lower() != 'y':
                    print("Deletion cancelled.")
                    return 0
            
            success = manager.delete_vm(args.vm_name, args.provider)
            return 0 if success else 1
            
        elif args.command == 'list':
            manager.list_vms(args.provider, args.detailed)
            return 0
            
        elif args.command == 'info':
            vm_info = manager.get_vm_info(args.vm_name, args.provider)
            return 0 if vm_info else 1
            
        elif args.command == 'snapshot':
            if args.snapshot_action == 'create':
                success = manager.create_snapshot(args.vm_name, args.snapshot_name, args.provider)
                return 0 if success else 1
            elif args.snapshot_action == 'restore':
                success = manager.restore_snapshot(args.vm_name, args.snapshot_name, args.provider)
                return 0 if success else 1
            elif args.snapshot_action == 'delete':
                success = manager.delete_snapshot(args.vm_name, args.snapshot_name, args.provider)
                return 0 if success else 1
            else:
                snapshot_parser.print_help()
                return 1
                
        elif args.command == 'status':
            status = manager.get_providers_status()
            print("Hypervisor Providers Status:")
            for provider, info in status.items():
                print(f"\n{provider.upper()}:")
                print(f"  Enabled: {info['enabled']}")
                print(f"  Connected: {info['connected']}")
                if 'error' in info:
                    print(f"  Error: {info['error']}")
            return 0
            
        elif args.command == 'templates':
            templates = manager.get_templates(args.provider)
            print("Available Templates:")
            for provider, template_list in templates.items():
                print(f"\n{provider.upper()}:")
                for template in template_list:
                    print(f"  - {template}")
            return 0
            
        elif args.command == 'clusters':
            clusters = manager.get_clusters(args.provider)
            print("Available Clusters:")
            for provider, cluster_list in clusters.items():
                print(f"\n{provider.upper()}:")
                for cluster in cluster_list:
                    print(f"  - {cluster}")
            return 0
            
        elif args.command == 'networks':
            networks = manager.get_networks(args.provider)
            print("Available Networks:")
            for provider, network_list in networks.items():
                print(f"\n{provider.upper()}:")
                for network in network_list:
                    print(f"  - {network}")
            return 0
            
        elif args.command == 'organize':
            vm_config = {}
            if args.cpu:
                vm_config['cpu'] = args.cpu
            if args.ram:
                vm_config['ram'] = args.ram
            if args.ssd:
                vm_config['ssd'] = args.ssd
            if args.os_type:
                vm_config['os_type'] = args.os_type
            
            if vm_config:
                vm_config['vm_name'] = args.vm_name
            else:
                vm_config = None
                
            success = manager.organize_vm(args.vm_name, vm_config)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())