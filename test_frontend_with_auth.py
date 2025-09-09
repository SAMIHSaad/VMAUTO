#!/usr/bin/env python3
"""
Test Frontend Template Selection with Authentication
"""

import requests
import json

def login_and_get_session():
    """Login and get authenticated session"""
    session = requests.Session()
    
    # Login
    login_data = {
        "Username": "admin",
        "password": "admin"
    }
    
    response = session.post('http://127.0.0.1:5000/api/login', 
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        print("✅ Login successful")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_nutanix_templates_with_auth():
    """Test Nutanix templates with authentication"""
    print("🧪 Testing Nutanix Templates with Authentication")
    print("=" * 60)
    
    # Get authenticated session
    session = login_and_get_session()
    if not session:
        return False
    
    # Test Nutanix templates
    try:
        response = session.get('http://127.0.0.1:5000/api/templates?provider=nutanix')
        print(f"📡 Nutanix Templates API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 API Response: {json.dumps(data, indent=2)}")
            
            if data.get('success') and 'templates' in data:
                templates = data['templates']
                print(f"✅ Nutanix Templates: {templates}")
                
                # Check if only the original 2 VMs are present
                expected = ['Windows Server 2019', 'Ubuntu 64-bit (3)']
                
                if set(templates) == set(expected):
                    print("🎉 SUCCESS: Nutanix shows only original 2 VMs!")
                    return True
                else:
                    print(f"❌ FAILED: Expected {expected}, got {templates}")
                    return False
            else:
                print(f"❌ API returned error: {data}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Nutanix templates: {e}")
        return False

def test_vmware_templates_with_auth():
    """Test VMware templates with authentication"""
    print("\n🧪 Testing VMware Templates with Authentication")
    print("=" * 60)
    
    # Get authenticated session
    session = login_and_get_session()
    if not session:
        return False
    
    try:
        response = session.get('http://127.0.0.1:5000/api/templates?provider=vmware')
        print(f"📡 VMware Templates API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'templates' in data:
                templates = data['templates']
                print(f"📋 VMware Templates: {templates}")
                return True
            else:
                print(f"❌ VMware API error: {data}")
                return False
        else:
            print(f"❌ VMware API failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing VMware templates: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Authenticated Template Selection Test")
    print("=" * 70)
    
    # Test Nutanix templates
    nutanix_success = test_nutanix_templates_with_auth()
    
    # Test VMware templates
    vmware_success = test_vmware_templates_with_auth()
    
    print("\n📊 Final Results:")
    print("=" * 40)
    print(f"✅ Nutanix Templates: {'PASS' if nutanix_success else 'FAIL'}")
    print(f"✅ VMware Templates: {'PASS' if vmware_success else 'FAIL'}")
    
    if nutanix_success:
        print("\n🎉 SUCCESS: Nutanix provider correctly shows only 2 original VMs!")
        print("   When selecting Nutanix as provider, users will see:")
        print("   - Windows Server 2019")
        print("   - Ubuntu 64-bit (3)")
        print("   No additional template VMs are shown.")
        return 0
    else:
        print("\n❌ FAILED: Nutanix template selection issue")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())