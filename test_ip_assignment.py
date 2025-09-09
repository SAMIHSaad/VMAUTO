#!/usr/bin/env python3
"""
Test IP Assignment Functionality
Tests the IP assignment scripts and integration
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.append(str(scripts_dir))

from scripts.ip_assignment_manager import IPAssignmentManager, load_hypervisor_config

def test_ip_assignment_manager():
    """Test the IP assignment manager"""
    print("🧪 Testing IP Assignment Manager...")
    
    try:
        # Load configuration
        config = load_hypervisor_config()
        print(f"✅ Configuration loaded: {list(config.keys())}")
        
        # Create manager
        manager = IPAssignmentManager(config)
        print("✅ IP Assignment Manager created successfully")
        
        # Test configuration
        if manager.vmware_assigner:
            print("✅ VMware assigner initialized")
        else:
            print("⚠️ VMware assigner not initialized")
            
        if manager.nutanix_assigner:
            print("✅ Nutanix assigner initialized")
        else:
            print("⚠️ Nutanix assigner not initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing IP assignment manager: {e}")
        return False

def test_vmware_ip_script():
    """Test VMware IP assignment script"""
    print("\n🧪 Testing VMware IP Assignment Script...")
    
    try:
        from scripts.assign_ip_vmware import VMwareIPAssigner
        
        # Create assigner (this will test import and initialization)
        assigner = VMwareIPAssigner()
        print("✅ VMware IP assigner created successfully")
        
        # Test with a dummy VMX path (will fail but tests the logic)
        dummy_vmx = "C:\\dummy\\test.vmx"
        result = assigner.assign_static_ip(dummy_vmx, "192.168.122.100")
        
        # We expect this to fail since the VMX doesn't exist
        if not result['success'] and "not found" in result['error']:
            print("✅ VMware IP assigner error handling works correctly")
            return True
        else:
            print(f"⚠️ Unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing VMware IP script: {e}")
        return False

def test_nutanix_ip_script():
    """Test Nutanix IP assignment script"""
    print("\n🧪 Testing Nutanix IP Assignment Script...")
    
    try:
        from scripts.assign_ip_nutanix import NutanixIPAssigner
        
        # Create assigner with mock configuration
        assigner = NutanixIPAssigner(
            prism_central_ip="127.0.0.1",
            username="admin",
            password="password",
            port=9441,
            use_ssl=False,
            verify_ssl=False
        )
        print("✅ Nutanix IP assigner created successfully")
        
        # Test with a dummy VM name (will fail but tests the logic)
        result = assigner.assign_static_ip("dummy-vm", "192.168.122.100")
        
        # We expect this to fail since the VM doesn't exist
        if not result['success']:
            print("✅ Nutanix IP assigner error handling works correctly")
            return True
        else:
            print(f"⚠️ Unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Nutanix IP script: {e}")
        return False

def test_integration_with_providers():
    """Test integration with hypervisor providers"""
    print("\n🧪 Testing Integration with Hypervisor Providers...")
    
    try:
        # Test VMware provider integration
        from hypervisor_providers.vmware_provider import VMwareProvider
        
        vmware_config = {
            'vmrun_path': r'C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe',
            'base_directory': os.getcwd(),
            'templates_directory': r'C:\Users\saads\OneDrive\Documents\Virtual Machines'
        }
        
        vmware_provider = VMwareProvider(vmware_config)
        print("✅ VMware provider created successfully")
        
        # Test if the _assign_ip_address method exists
        if hasattr(vmware_provider, '_assign_ip_address'):
            print("✅ VMware provider has IP assignment method")
        else:
            print("❌ VMware provider missing IP assignment method")
            return False
        
        # Test Nutanix provider integration
        from hypervisor_providers.nutanix_provider import NutanixProvider
        
        nutanix_config = {
            'prism_central_ip': '127.0.0.1',
            'username': 'admin',
            'password': 'password',
            'port': 9441,
            'use_ssl': False,
            'verify_ssl': False
        }
        
        nutanix_provider = NutanixProvider(nutanix_config)
        print("✅ Nutanix provider created successfully")
        
        # Test if the _assign_ip_address method exists
        if hasattr(nutanix_provider, '_assign_ip_address'):
            print("✅ Nutanix provider has IP assignment method")
        else:
            print("❌ Nutanix provider missing IP assignment method")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing provider integration: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting IP Assignment Tests...\n")
    
    tests = [
        ("IP Assignment Manager", test_ip_assignment_manager),
        ("VMware IP Script", test_vmware_ip_script),
        ("Nutanix IP Script", test_nutanix_ip_script),
        ("Provider Integration", test_integration_with_providers)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print('='*50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())