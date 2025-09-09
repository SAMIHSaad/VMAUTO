#!/usr/bin/env python3
"""
Test Frontend Template Selection - Verify Nutanix shows only original 2 VMs
"""

import requests
import json

def test_templates_api():
    """Test the templates API endpoint"""
    print("🧪 Testing Templates API")
    print("=" * 50)
    
    # Test Nutanix templates
    try:
        response = requests.get('http://127.0.0.1:5000/api/templates?provider=nutanix')
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 API Response: {json.dumps(data, indent=2)}")
            
            if data.get('success') and 'templates' in data:
                templates = data['templates']
                print(f"✅ Templates found: {templates}")
                
                # Check if only the original 2 VMs are present
                expected = ['Windows Server 2019', 'Ubuntu 64-bit (3)']
                
                if set(templates) == set(expected):
                    print("🎉 SUCCESS: Only original 2 VMs are returned!")
                    return True
                else:
                    print(f"❌ FAILED: Expected {expected}, got {templates}")
                    return False
            else:
                print(f"❌ API returned error: {data}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing templates API: {e}")
        return False

def test_vmware_templates():
    """Test VMware templates for comparison"""
    print("\n🧪 Testing VMware Templates (for comparison)")
    print("=" * 50)
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/templates?provider=vmware')
        print(f"📡 VMware API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'templates' in data:
                templates = data['templates']
                print(f"📋 VMware Templates: {templates}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing VMware templates: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Frontend Template Selection Test")
    print("=" * 60)
    
    # Test Nutanix templates
    nutanix_success = test_templates_api()
    
    # Test VMware templates for comparison
    vmware_success = test_vmware_templates()
    
    print("\n📊 Test Results:")
    print("=" * 30)
    print(f"✅ Nutanix Templates: {'PASS' if nutanix_success else 'FAIL'}")
    print(f"✅ VMware Templates: {'PASS' if vmware_success else 'FAIL'}")
    
    if nutanix_success:
        print("\n🎉 SUCCESS: Nutanix provider now shows only the original 2 VMs!")
        print("   - Windows Server 2019")
        print("   - Ubuntu 64-bit (3)")
        return 0
    else:
        print("\n❌ FAILED: Nutanix template selection needs fixing")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())