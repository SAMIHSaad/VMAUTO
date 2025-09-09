"""
Base Hypervisor Provider
Abstract base class for all hypervisor providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class VMConfig:
    """VM Configuration data class"""
    name: str
    cpu: int
    ram: int  # in MB
    disk: int  # in GB
    os_type: str
    network: Optional[str] = None
    ip_address: Optional[str] = None
    gateway: Optional[str] = None
    dns: Optional[str] = None
    template: Optional[str] = None
    cluster: Optional[str] = None
    storage_container: Optional[str] = None

@dataclass
class VMInfo:
    """VM Information data class"""
    name: str
    uuid: str
    state: str
    cpu: int
    ram: int
    disk: int
    ip_address: Optional[str] = None
    hypervisor: str = ""
    cluster: Optional[str] = None

class BaseHypervisorProvider(ABC):
    """Abstract base class for hypervisor providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration"""
        self.config = config
        self.provider_name = self.__class__.__name__.replace('Provider', '').lower()
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the hypervisor"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the hypervisor"""
        pass
    
    @abstractmethod
    def create_vm(self, vm_config: VMConfig) -> Dict[str, Any]:
        """Create a new VM"""
        pass
    
    @abstractmethod
    def clone_vm(self, source_vm: str, vm_config: VMConfig) -> Dict[str, Any]:
        """Clone an existing VM"""
        pass
    
    @abstractmethod
    def delete_vm(self, vm_name: str) -> bool:
        """Delete a VM"""
        pass
    
    @abstractmethod
    def start_vm(self, vm_name: str) -> bool:
        """Start a VM"""
        pass
    
    @abstractmethod
    def stop_vm(self, vm_name: str) -> bool:
        """Stop a VM"""
        pass
    
    @abstractmethod
    def restart_vm(self, vm_name: str) -> bool:
        """Restart a VM"""
        pass
    
    @abstractmethod
    def get_vm_info(self, vm_name: str) -> Optional[VMInfo]:
        """Get VM information"""
        pass
    
    @abstractmethod
    def list_vms(self) -> List[VMInfo]:
        """List all VMs"""
        pass
    
    @abstractmethod
    def get_templates(self) -> List[str]:
        """Get available VM templates"""
        pass
    
    @abstractmethod
    def get_clusters(self) -> List[str]:
        """Get available clusters"""
        pass
    
    @abstractmethod
    def get_networks(self) -> List[str]:
        """Get available networks"""
        pass
    
    @abstractmethod
    def create_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Create a VM snapshot"""
        pass
    
    @abstractmethod
    def restore_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Restore a VM snapshot"""
        pass
    
    @abstractmethod
    def delete_snapshot(self, vm_name: str, snapshot_name: str) -> bool:
        """Delete a VM snapshot"""
        pass
    
    @abstractmethod
    def open_console(self, vm_name: str) -> Dict[str, Any]:
        """Open VM console"""
        pass
    
    def validate_config(self, vm_config: VMConfig) -> bool:
        """Validate VM configuration"""
        if not vm_config.name:
            raise ValueError("VM name is required")
        if vm_config.cpu <= 0:
            raise ValueError("CPU count must be positive")
        if vm_config.ram <= 0:
            raise ValueError("RAM must be positive")
        if vm_config.disk <= 0:
            raise ValueError("Disk size must be positive")
        return True
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name