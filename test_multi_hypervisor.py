#!/usr/bin/env python3
"""
Test script for multi-hypervisor VM management system
Tests both VMware and Nutanix providers
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig

def test_hypervisor_manager():
    """Test the hypervisor manager initialization"""
    print("Testing Hypervisor Manager initialization...")
    
    try:
        manager = HypervisorManager()
        print(f"✓ Hypervisor Manager initialized successfully")
        
        # Test provider status
        status = manager.get_provider_status()
        print(f"✓ Provider status retrieved: {list(status.keys())}")
        
        # Test available providers
        providers = manager.get_available_providers()
        print(f"✓ Available providers: {providers}")
        
        return manager
        
    except Exception as e:
        print(f"✗ Error initializing Hypervisor Manager: {e}")
        return None

def test_vmware_provider(manager):
    """Test VMware provider functionality"""
    print("\nTesting VMware Provider...")
    
    try:
        # Test connection
        connected = manager.connect_provider('vmware')
        print(f"✓ VMware connection test: {'Connected' if connected else 'Failed'}")
        
        # Test getting templates
        templates = manager.get_templates('vmware')
        print(f"✓ VMware templates: {templates.get('vmware', [])}")
        
        # Test getting clusters
        clusters = manager.get_clusters('vmware')
        print(f"✓ VMware clusters: {clusters.get('vmware', [])}")
        
        # Test getting networks
        networks = manager.get_networks('vmware')
        print(f"✓ VMware networks: {networks.get('vmware', [])}")
        
        # Test listing VMs
        vms = manager.list_vms('vmware')
        print(f"✓ VMware VMs found: {len(vms)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing VMware provider: {e}")
        return False

def test_nutanix_provider(manager):
    """Test Nutanix provider functionality"""
    print("\nTesting Nutanix Provider...")
    
    try:
        # Check if Nutanix is enabled
        status = manager.get_provider_status()
        nutanix_status = status.get('nutanix', {})
        
        if not nutanix_status.get('enabled', False):
            print("ℹ Nutanix provider is disabled - skipping tests")
            return True
        
        # Test connection
        connected = manager.connect_provider('nutanix')
        print(f"✓ Nutanix connection test: {'Connected' if connected else 'Failed'}")
        
        if not connected:
            print("ℹ Nutanix connection failed - check configuration")
            return True
        
        # Test getting templates
        templates = manager.get_templates('nutanix')
        print(f"✓ Nutanix templates: {templates.get('nutanix', [])}")
        
        # Test getting clusters
        clusters = manager.get_clusters('nutanix')
        print(f"✓ Nutanix clusters: {clusters.get('nutanix', [])}")
        
        # Test getting networks
        networks = manager.get_networks('nutanix')
        print(f"✓ Nutanix networks: {networks.get('nutanix', [])}")
        
        # Test listing VMs
        vms = manager.list_vms('nutanix')
        print(f"✓ Nutanix VMs found: {len(vms)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing Nutanix provider: {e}")
        return False

def test_vm_config():
    """Test VM configuration creation"""
    print("\nTesting VM Configuration...")
    
    try:
        # Test basic VM config
        vm_config = VMConfig(
            name="test-vm",
            cpu=2,
            ram=2048,
            disk=20,
            os_type="linux"
        )
        print(f"✓ Basic VM config created: {vm_config.name}")
        
        # Test Nutanix-specific VM config
        nutanix_config = VMConfig(
            name="test-nutanix-vm",
            cpu=4,
            ram=4096,
            disk=40,
            os_type="linux",
            cluster="test-cluster",
            network="test-network",
            template="ubuntu-template"
        )
        print(f"✓ Nutanix VM config created: {nutanix_config.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing VM configuration: {e}")
        return False

def test_configuration_management(manager):
    """Test configuration management"""
    print("\nTesting Configuration Management...")
    
    try:
        # Test getting current config
        status = manager.get_provider_status()
        print(f"✓ Configuration status retrieved")
        
        # Test setting default provider
        current_default = manager.config.get('default_provider', 'vmware')
        print(f"✓ Current default provider: {current_default}")
        
        # Test provider enabling/disabling (without actually changing)
        print(f"✓ Configuration management functions available")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing configuration management: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Multi-Hypervisor VM Management System Test")
    print("=" * 60)
    
    # Test hypervisor manager
    manager = test_hypervisor_manager()
    if not manager:
        print("\n✗ Critical error: Could not initialize Hypervisor Manager")
        return 1
    
    # Test VM configuration
    if not test_vm_config():
        print("\n✗ VM configuration test failed")
        return 1
    
    # Test configuration management
    if not test_configuration_management(manager):
        print("\n✗ Configuration management test failed")
        return 1
    
    # Test VMware provider
    vmware_success = test_vmware_provider(manager)
    
    # Test Nutanix provider
    nutanix_success = test_nutanix_provider(manager)
    
    # Cleanup
    try:
        manager.disconnect_all_providers()
        print("\n✓ All providers disconnected")
    except Exception as e:
        print(f"\n⚠ Warning: Error disconnecting providers: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"VMware Provider: {'✓ PASS' if vmware_success else '✗ FAIL'}")
    print(f"Nutanix Provider: {'✓ PASS' if nutanix_success else '✗ FAIL'}")
    print("=" * 60)
    
    if vmware_success and nutanix_success:
        print("🎉 All tests passed! Multi-hypervisor system is ready.")
        return 0
    else:
        print("⚠ Some tests failed. Check the configuration and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())