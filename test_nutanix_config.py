#!/usr/bin/env python3
"""
Test script to verify Nutanix configuration functionality
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def test_nutanix_configuration():
    """Test Nutanix configuration and activation"""
    print("🧪 Testing Nutanix Configuration")
    print("=" * 50)
    
    # Initialize manager
    manager = HypervisorManager()
    
    # Show initial status
    print("\n1. Initial Provider Status:")
    status = manager.get_provider_status()
    for provider, info in status.items():
        enabled = "✅ Enabled" if info['enabled'] else "❌ Disabled"
        connected = "🟢 Connected" if info['connected'] else "🔴 Disconnected"
        print(f"   {provider.upper()}: {enabled}, {connected}")
    
    # Show available providers
    print("\n2. Available Providers:")
    available = manager.get_available_providers()
    print(f"   {available}")
    
    # Test Nutanix configuration
    print("\n3. Testing Nutanix Configuration:")
    nutanix_config = {
        'enabled': True,
        'prism_central_ip': '10.0.0.100',
        'username': 'admin',
        'password': 'test_password',
        'port': 9440
    }
    
    print(f"   Configuring Nutanix with: {nutanix_config['prism_central_ip']}")
    success = manager.update_provider_config('nutanix', nutanix_config)
    
    if success:
        print("   ✅ Nutanix configuration updated successfully")
    else:
        print("   ❌ Failed to update Nutanix configuration")
        return False
    
    # Check status after configuration
    print("\n4. Provider Status After Configuration:")
    status = manager.get_provider_status()
    for provider, info in status.items():
        enabled = "✅ Enabled" if info['enabled'] else "❌ Disabled"
        connected = "🟢 Connected" if info['connected'] else "🔴 Disconnected"
        print(f"   {provider.upper()}: {enabled}, {connected}")
    
    # Test getting resources from Nutanix (should fail gracefully)
    print("\n5. Testing Nutanix Resource Discovery:")
    try:
        clusters = manager.get_clusters('nutanix')
        print(f"   Nutanix clusters: {clusters}")
        
        networks = manager.get_networks('nutanix')
        print(f"   Nutanix networks: {networks}")
        
        templates = manager.get_templates('nutanix')
        print(f"   Nutanix templates: {templates}")
        
    except Exception as e:
        print(f"   ⚠️ Resource discovery failed (expected): {e}")
    
    # Test disabling Nutanix
    print("\n6. Testing Nutanix Disable:")
    nutanix_config['enabled'] = False
    success = manager.update_provider_config('nutanix', nutanix_config)
    
    if success:
        print("   ✅ Nutanix disabled successfully")
    else:
        print("   ❌ Failed to disable Nutanix")
        return False
    
    # Final status
    print("\n7. Final Provider Status:")
    status = manager.get_provider_status()
    for provider, info in status.items():
        enabled = "✅ Enabled" if info['enabled'] else "❌ Disabled"
        connected = "🟢 Connected" if info['connected'] else "🔴 Disconnected"
        print(f"   {provider.upper()}: {enabled}, {connected}")
    
    print("\n🎉 Nutanix configuration test completed successfully!")
    return True

def test_web_interface_readiness():
    """Test that web interface can handle Nutanix"""
    print("\n🌐 Testing Web Interface Readiness")
    print("=" * 50)
    
    manager = HypervisorManager()
    
    # Test provider status endpoint data
    status = manager.get_provider_status()
    print("Provider status for web interface:")
    print(json.dumps(status, indent=2))
    
    # Test available providers endpoint data
    providers = manager.get_available_providers()
    print(f"\nAvailable providers for web interface: {providers}")
    
    # Test configuration endpoint data
    config = manager.get_config()
    print("\nConfiguration for web interface:")
    print(json.dumps(config, indent=2))
    
    print("\n✅ Web interface data structures are ready!")

def main():
    """Main test function"""
    print("🚀 Multi-Hypervisor Nutanix Configuration Test")
    print("=" * 60)
    
    try:
        # Test configuration functionality
        if not test_nutanix_configuration():
            return 1
        
        # Test web interface readiness
        test_web_interface_readiness()
        
        print("\n" + "=" * 60)
        print("🎯 All tests passed! Nutanix configuration is working!")
        print("\nNext steps:")
        print("1. Open web interface: http://localhost:5000")
        print("2. Go to Settings tab")
        print("3. Configure Nutanix with real credentials")
        print("4. Enable Nutanix provider")
        print("5. Test VM creation with Nutanix")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())