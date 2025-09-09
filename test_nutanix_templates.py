#!/usr/bin/env python3
"""
Test Nutanix Templates - Verify only original 2 VMs are shown
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from hypervisor_providers.nutanix_provider import NutanixProvider

def test_nutanix_templates():
    """Test that Nutanix only shows the original 2 VMs as templates"""
    print("🧪 Testing Nutanix Template Selection")
    print("=" * 50)
    
    # Create Nutanix provider
    nutanix_config = {
        'prism_central_ip': '127.0.0.1',
        'username': 'admin',
        'password': 'password',
        'port': 9441,
        'use_ssl': False,
        'verify_ssl': False
    }
    
    try:
        provider = NutanixProvider(nutanix_config)
        print("✅ Nutanix provider created")
        
        # Connect to provider
        if provider.connect():
            print("✅ Connected to Nutanix mock server")
            
            # Get templates
            templates = provider.get_templates()
            print(f"📋 Available templates: {templates}")
            
            # Verify only the original 2 VMs are present
            expected_templates = ['Windows Server 2019', 'Ubuntu 64-bit (3)']
            
            print("\n🔍 Verification:")
            for template in expected_templates:
                if template in templates:
                    print(f"✅ {template} - Found")
                else:
                    print(f"❌ {template} - Missing")
            
            # Check for unexpected templates
            unexpected = [t for t in templates if t not in expected_templates and t != 'Unknown']
            if unexpected:
                print(f"⚠️  Unexpected templates found: {unexpected}")
            else:
                print("✅ No unexpected templates found")
            
            # Final result
            if set(templates) == set(expected_templates) or (len([t for t in templates if t in expected_templates]) == 2):
                print("\n🎉 SUCCESS: Only original 2 VMs are available as templates")
                return True
            else:
                print(f"\n❌ FAILED: Expected {expected_templates}, got {templates}")
                return False
                
        else:
            print("❌ Failed to connect to Nutanix mock server")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Nutanix templates: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Nutanix Template Selection Test")
    print("=" * 60)
    
    success = test_nutanix_templates()
    
    if success:
        print("\n✅ Test PASSED - Nutanix shows only original 2 VMs")
        return 0
    else:
        print("\n❌ Test FAILED - Check template configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())