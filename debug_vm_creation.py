#!/usr/bin/env python3
"""
Debug VM Creation - Test the VM creation process step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig
from ip_manager import get_available_ip, initialize_ip_pool

def test_vm_creation():
    print("=== VM Creation Debug Test ===")
    
    # Initialize IP pool
    print("1. Initializing IP pool...")
    initialize_ip_pool()
    
    # Get available IP
    print("2. Getting available IP...")
    ip_address = get_available_ip()
    print(f"   Available IP: {ip_address}")
    
    if not ip_address:
        print("   ERROR: No available IP addresses")
        return False
    
    # Initialize hypervisor manager
    print("3. Initializing hypervisor manager...")
    try:
        hypervisor_manager = HypervisorManager()
        print("   Hypervisor manager initialized")
    except Exception as e:
        print(f"   ERROR: Failed to initialize hypervisor manager: {e}")
        return False
    
    # Get provider status
    print("4. Getting provider status...")
    try:
        status = hypervisor_manager.get_provider_status()
        print(f"   Provider status: {status}")
        
        # Find enabled provider
        enabled_provider = None
        for provider, provider_status in status.items():
            if provider_status.get('enabled') and provider_status.get('connected'):
                enabled_provider = provider
                break
        
        if not enabled_provider:
            print("   ERROR: No enabled and connected providers found")
            return False
        
        print(f"   Using provider: {enabled_provider}")
        
    except Exception as e:
        print(f"   ERROR: Failed to get provider status: {e}")
        return False
    
    # Create VM configuration
    print("5. Creating VM configuration...")
    try:
        vm_config = VMConfig(
            name="debug-test-vm",
            cpu=2,
            ram=2048,
            disk=20,
            os_type="linux",
            network=None,
            ip_address=ip_address,
            template=None,
            cluster=None
        )
        print(f"   VM config created: {vm_config}")
    except Exception as e:
        print(f"   ERROR: Failed to create VM config: {e}")
        return False
    
    # Test VM creation
    print("6. Testing VM creation...")
    try:
        result = hypervisor_manager.create_vm(vm_config, enabled_provider)
        print(f"   VM creation result: {result}")
        
        if result.get('success'):
            print("   SUCCESS: VM creation initiated")
            return True
        else:
            print(f"   FAILED: VM creation failed - {result.get('error', 'Unknown error')}")
            if 'stdout' in result:
                print(f"   Stdout: {result['stdout']}")
            return False
            
    except Exception as e:
        print(f"   ERROR: Exception during VM creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_components():
    print("\n=== API Components Test ===")
    
    # Test data parsing
    print("1. Testing data parsing...")
    test_data = {
        'vm_name': 'test-vm-debug',
        'cpu': 2,
        'ram': 2048,
        'disk': 20,
        'os_type': 'linux',
        'provider': 'vmware'
    }
    
    try:
        # Simulate the API logic
        ip_address = get_available_ip()
        print(f"   IP address: {ip_address}")
        
        vm_config = VMConfig(
            name=test_data['vm_name'],
            cpu=int(test_data.get('cpu', 2)),
            ram=int(test_data.get('ram', 2048)),
            disk=int(test_data.get('disk', 20)),
            os_type=test_data.get('os_type', 'linux'),
            network=test_data.get('network'),
            ip_address=ip_address,
            template=test_data.get('template'),
            cluster=test_data.get('cluster')
        )
        
        print(f"   VM config: {vm_config}")
        print("   SUCCESS: Data parsing works")
        
    except Exception as e:
        print(f"   ERROR: Data parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_components()
    test_vm_creation()