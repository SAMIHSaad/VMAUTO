"""
Hypervisor Manager
Unified interface for managing multiple hypervisor providers
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from hypervisor_providers import BaseHypervisorProvider, VMwareProvider, NutanixProvider, VMConfig, VMInfo

class HypervisorManager:
    """Unified hypervisor management class"""
    
    def __init__(self, config_file: str = None):
        """Initialize hypervisor manager
        
        Args:
            config_file: Path to configuration file
        """
        self.providers: Dict[str, BaseHypervisorProvider] = {}
        self.config_file = config_file or "hypervisor_config.json"
        self.config = self._load_config()
        self._initialize_providers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        # Default configuration
                # Default configuration
        # Default configuration
        default_config = {
            "default_provider": "vmware",
            "providers": {
                "vmware": {
                    "enabled": True,
                    "vmrun_path": r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
                    "base_directory": os.getcwd(),
                    "templates_directory": r"C:\Users\saads\OneDrive\Documents\Virtual Machines"
                },
                "nutanix": {
                    "enabled": True,
                    "prism_central_ip": "127.0.0.1",
                    "prism_element_ip": "127.0.0.1",
                    "username": "admin",
                    "password": "password",
                    "port": 9441,
                    "verify_ssl": False,
                    "use_ssl": False
                }
            }
        }
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def _initialize_providers(self):
        """Initialize enabled providers"""
        providers_config = self.config.get('providers', {})
        
        # Initialize VMware provider
        if providers_config.get('vmware', {}).get('enabled', False):
            try:
                vmware_config = providers_config['vmware']
                self.providers['vmware'] = VMwareProvider(vmware_config)
                print("VMware provider initialized")
            except Exception as e:
                print(f"Failed to initialize VMware provider: {e}")
        
        # Initialize Nutanix provider
        if providers_config.get('nutanix', {}).get('enabled', False):
            try:
                nutanix_config = providers_config['nutanix']
                self.providers['nutanix'] = NutanixProvider(nutanix_config)
                print("Nutanix provider initialized")
            except Exception as e:
                print(f"Failed to initialize Nutanix provider: {e}")
    
    def get_provider(self, provider_name: str = None) -> Optional[BaseHypervisorProvider]:
        """Get a specific provider or default provider"""
        if provider_name is None:
            provider_name = self.config.get('default_provider', 'vmware')
        
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers (all configured providers)"""
        # Return all configured providers, not just initialized ones
        providers_config = self.config.get('providers', {})
        return list(providers_config.keys())
    
    def connect_provider(self, provider_name: str) -> bool:
        """Connect to a specific provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.connect()
        return False
    
    def connect_all_providers(self) -> Dict[str, bool]:
        """Connect to all providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.connect()
        return results
    
    def disconnect_provider(self, provider_name: str) -> bool:
        """Disconnect from a specific provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.disconnect()
        return False
    
    def disconnect_all_providers(self) -> Dict[str, bool]:
        """Disconnect from all providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.disconnect()
        return results
    
    def create_vm(self, vm_config: VMConfig, provider_name: str = None) -> Dict[str, Any]:
        """Create a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {
                'success': False,
                'error': f"Provider '{provider_name or 'default'}' not available"
            }
        
        return provider.create_vm(vm_config)
    
    def clone_vm(self, source_vm: str, vm_config: VMConfig, provider_name: str = None) -> Dict[str, Any]:
        """Clone a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {
                'success': False,
                'error': f"Provider '{provider_name or 'default'}' not available"
            }
        
        return provider.clone_vm(source_vm, vm_config)
    
    def delete_vm(self, vm_name: str, provider_name: str = None) -> bool:
        """Delete a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.delete_vm(vm_name)
    
    def start_vm(self, vm_name: str, provider_name: str = None) -> bool:
        """Start a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.start_vm(vm_name)
    
    def stop_vm(self, vm_name: str, provider_name: str = None) -> bool:
        """Stop a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.stop_vm(vm_name)
    
    def restart_vm(self, vm_name: str, provider_name: str = None) -> bool:
        """Restart a VM using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.restart_vm(vm_name)
    
    def get_vm_info(self, vm_name: str, provider_name: str = None) -> Optional[VMInfo]:
        """Get VM information from specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return None
        
        return provider.get_vm_info(vm_name)
    
    def list_vms(self, provider_name: str = None) -> List[VMInfo]:
        """List VMs from specified provider or all providers"""
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return provider.list_vms()
            return []
        
        # List from all providers
        all_vms = []
        for name, provider in self.providers.items():
            try:
                vms = provider.list_vms()
                all_vms.extend(vms)
            except Exception as e:
                print(f"Error listing VMs from {name}: {e}")
        
        return all_vms
    
    def get_templates(self, provider_name: str = None) -> List[str]:
        """Get templates from specified provider or all providers"""
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return provider.get_templates()
            return []
        
        # Combine templates from all providers
        combined_templates = []
        template_names = set()
        
        for name, provider in self.providers.items():
            try:
                templates = provider.get_templates()
                for template in templates:
                    if template not in template_names:
                        combined_templates.append(template)
                        template_names.add(template)
            except Exception as e:
                print(f"Error getting templates from {name}: {e}")
        
        return combined_templates
    
    def update_provider_config(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """Update provider configuration"""
        try:
            # Update configuration
            if 'providers' not in self.config:
                self.config['providers'] = {}
            
            self.config['providers'][provider_name] = config
            self._save_config(self.config)
            
            # Reinitialize providers if enabled
            if config.get('enabled', False):
                if provider_name == 'vmware':
                    try:
                        self.providers['vmware'] = VMwareProvider(config)
                        print(f"VMware provider reinitialized")
                    except Exception as e:
                        print(f"Failed to reinitialize VMware provider: {e}")
                        return False
                elif provider_name == 'nutanix':
                    try:
                        self.providers['nutanix'] = NutanixProvider(config)
                        print(f"Nutanix provider initialized")
                    except Exception as e:
                        print(f"Failed to initialize Nutanix provider: {e}")
                        return False
            else:
                # Remove provider if disabled
                if provider_name in self.providers:
                    del self.providers[provider_name]
                    print(f"{provider_name} provider disabled")
            
            return True
        except Exception as e:
            print(f"Error updating provider config: {e}")
            return False
    
    def set_default_provider(self, provider_name: str) -> bool:
        """Set default provider"""
        try:
            self.config['default_provider'] = provider_name
            self._save_config(self.config)
            return True
        except Exception as e:
            print(f"Error setting default provider: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def get_clusters(self, provider_name: str = None) -> Dict[str, List[str]]:
        """Get clusters from specified provider or all providers"""
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return {provider_name: provider.get_clusters()}
            return {}
        
        all_clusters = {}
        for name, provider in self.providers.items():
            try:
                clusters = provider.get_clusters()
                all_clusters[name] = clusters
            except Exception as e:
                print(f"Error getting clusters from {name}: {e}")
                all_clusters[name] = []
        
        return all_clusters
    
    def get_networks(self, provider_name: str = None) -> Dict[str, List[str]]:
        """Get networks from specified provider or all providers"""
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                return {provider_name: provider.get_networks()}
            return {}
        
        all_networks = {}
        for name, provider in self.providers.items():
            try:
                networks = provider.get_networks()
                all_networks[name] = networks
            except Exception as e:
                print(f"Error getting networks from {name}: {e}")
                all_networks[name] = []
        
        return all_networks
    
    def create_snapshot(self, vm_name: str, snapshot_name: str, provider_name: str = None) -> bool:
        """Create a VM snapshot using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.create_snapshot(vm_name, snapshot_name)
    
    def restore_snapshot(self, vm_name: str, snapshot_name: str, provider_name: str = None) -> bool:
        """Restore a VM snapshot using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.restore_snapshot(vm_name, snapshot_name)
    
    def delete_snapshot(self, vm_name: str, snapshot_name: str, provider_name: str = None) -> bool:
        """Delete a VM snapshot using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return provider.delete_snapshot(vm_name, snapshot_name)
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration"""
        self.config.update(new_config)
        self._save_config(self.config)
        
        # Reinitialize providers
        self.providers.clear()
        self._initialize_providers()
    
    def enable_provider(self, provider_name: str, config: Dict[str, Any] = None):
        """Enable a provider"""
        if 'providers' not in self.config:
            self.config['providers'] = {}
        
        if provider_name not in self.config['providers']:
            self.config['providers'][provider_name] = {}
        
        self.config['providers'][provider_name]['enabled'] = True
        
        if config:
            self.config['providers'][provider_name].update(config)
        
        self._save_config(self.config)
        self._initialize_providers()
    
    def disable_provider(self, provider_name: str):
        """Disable a provider"""
        if provider_name in self.config.get('providers', {}):
            self.config['providers'][provider_name]['enabled'] = False
            self._save_config(self.config)
            
            # Remove from active providers
            if provider_name in self.providers:
                self.providers[provider_name].disconnect()
                del self.providers[provider_name]
    
    def set_default_provider(self, provider_name: str):
        """Set default provider"""
        if provider_name in self.providers:
            self.config['default_provider'] = provider_name
            self._save_config(self.config)
            return True
        return False
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            try:
                connected = provider.connect()
                provider.disconnect()  # Don't keep connection open
                
                status[name] = {
                    'enabled': True,
                    'connected': connected,
                    'provider_type': provider.get_provider_name()
                }
            except Exception as e:
                status[name] = {
                    'enabled': True,
                    'connected': False,
                    'error': str(e),
                    'provider_type': provider.get_provider_name()
                }
        
        # Add disabled providers
        for name, config in self.config.get('providers', {}).items():
            if not config.get('enabled', False) and name not in status:
                status[name] = {
                    'enabled': False,
                    'connected': False,
                    'provider_type': name
                }
        
        return status
    
    def open_console(self, vm_name: str, provider_name: str = None) -> Dict[str, Any]:
        """Open VM console using specified or default provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {
                'success': False,
                'error': f"Provider '{provider_name}' not found or not enabled"
            }
        
        return provider.open_console(vm_name)