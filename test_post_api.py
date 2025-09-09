#!/usr/bin/env python3
"""
Test script for VM Creation POST API
Tests the /api/vms POST endpoint with various scenarios
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class VMAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def login(self, username: str = "testuser", password: str = "testpass") -> bool:
        """Login and get authentication token"""
        try:
            login_data = {
                "Username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def register_test_user(self, username: str = "testuser", password: str = "testpass") -> bool:
        """Register a test user if needed"""
        try:
            register_data = {
                "Nom": "Test",
                "Prenom": "User", 
                "Username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [201, 409]:  # 409 = user already exists
                print("✅ Test user ready")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def get_providers_status(self) -> Dict[str, Any]:
        """Get available providers and their status"""
        try:
            response = self.session.get(f"{self.base_url}/api/providers/status")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Providers status retrieved")
                return data.get('providers', {})
            else:
                print(f"❌ Failed to get providers: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Providers error: {e}")
            return {}
    
    def get_templates(self, provider: str) -> list:
        """Get available templates for a provider"""
        try:
            response = self.session.get(f"{self.base_url}/api/templates?provider={provider}")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('templates', [])
            else:
                print(f"❌ Failed to get templates: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Templates error: {e}")
            return []
    
    def create_vm_test(self, vm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test VM creation with given data"""
        try:
            print(f"🚀 Testing VM creation: {vm_data['vm_name']}")
            print(f"   Provider: {vm_data.get('provider', 'default')}")
            print(f"   CPU: {vm_data.get('cpu', 2)}, RAM: {vm_data.get('ram', 2048)}MB, Disk: {vm_data.get('disk', 20)}GB")
            
            response = self.session.post(
                f"{self.base_url}/api/vms",
                json=vm_data,
                headers={"Content-Type": "application/json"},
                timeout=3600  # 1 hour timeout for VM creation
            )
            
            result = {
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code == 200
            }
            
            if result['success']:
                print("✅ VM creation request successful")
            else:
                print(f"❌ VM creation failed: {response.status_code}")
                print(f"   Error: {result['response']}")
            
            return result
            
        except requests.exceptions.Timeout:
            print("⏰ VM creation timed out (this may be normal for long builds)")
            return {'status_code': 408, 'response': 'Timeout', 'success': False}
        except Exception as e:
            print(f"❌ VM creation error: {e}")
            return {'status_code': 500, 'response': str(e), 'success': False}
    
    def list_vms(self) -> Dict[str, Any]:
        """List all VMs"""
        try:
            response = self.session.get(f"{self.base_url}/api/vms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('vms', []))} VMs")
                return data
            else:
                print(f"❌ Failed to list VMs: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ List VMs error: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Run comprehensive API tests"""
        print("=" * 60)
        print("🧪 VM Creation API Comprehensive Test")
        print("=" * 60)
        
        # Step 1: Register and login
        print("\n1️⃣ Authentication Test")
        if not self.register_test_user():
            print("❌ Cannot proceed without test user")
            return False
            
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Get providers status
        print("\n2️⃣ Providers Status Test")
        providers = self.get_providers_status()
        if not providers:
            print("❌ No providers available")
            return False
        
        print("Available providers:")
        for provider, status in providers.items():
            enabled = "✅" if status.get('enabled') else "❌"
            connected = "🔗" if status.get('connected') else "🔌"
            print(f"   {enabled} {connected} {provider}: {status.get('status', 'unknown')}")
        
        # Find an enabled provider
        enabled_provider = None
        for provider, status in providers.items():
            if status.get('enabled') and status.get('connected'):
                enabled_provider = provider
                break
        
        if not enabled_provider:
            print("❌ No enabled and connected providers found")
            return False
        
        print(f"✅ Using provider: {enabled_provider}")
        
        # Step 3: Get templates
        print(f"\n3️⃣ Templates Test for {enabled_provider}")
        templates = self.get_templates(enabled_provider)
        print(f"Available templates: {templates}")
        
        # Step 4: Test VM creation scenarios
        print("\n4️⃣ VM Creation Tests")
        
        test_cases = [
            {
                "name": "Basic Linux VM",
                "data": {
                    "vm_name": f"test-vm-{int(time.time())}",
                    "provider": enabled_provider,
                    "cpu": 2,
                    "ram": 2048,
                    "disk": 20,
                    "os_type": "linux"
                }
            },
            {
                "name": "High-spec VM",
                "data": {
                    "vm_name": f"test-vm-high-{int(time.time())}",
                    "provider": enabled_provider,
                    "cpu": 4,
                    "ram": 4096,
                    "disk": 40,
                    "os_type": "linux"
                }
            }
        ]
        
        # Add template-based test if templates are available
        if templates:
            test_cases.append({
                "name": "Template-based VM",
                "data": {
                    "vm_name": f"test-vm-template-{int(time.time())}",
                    "provider": enabled_provider,
                    "template": templates[0],
                    "cpu": 2,
                    "ram": 2048,
                    "disk": 20,
                    "os_type": "linux"
                }
            })
        
        results = []
        for test_case in test_cases:
            print(f"\n   🧪 {test_case['name']}")
            result = self.create_vm_test(test_case['data'])
            results.append({
                'test': test_case['name'],
                'result': result
            })
            
            # Wait a bit between tests
            time.sleep(2)
        
        # Step 5: List VMs
        print("\n5️⃣ List VMs Test")
        self.list_vms()
        
        # Step 6: Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        successful_tests = sum(1 for r in results if r['result']['success'])
        total_tests = len(results)
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        
        for result in results:
            status = "✅" if result['result']['success'] else "❌"
            print(f"{status} {result['test']}")
        
        return successful_tests == total_tests

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"Testing API at: {base_url}")
    
    tester = VMAPITester(base_url)
    
    # Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print("✅ Server is responding")
    except Exception as e:
        print(f"❌ Server is not responding: {e}")
        print("Make sure the Flask app is running with: python app.py")
        return False
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)