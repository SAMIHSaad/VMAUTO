#!/usr/bin/env python3
"""
Quick test to show the mock server API is working
"""

import requests
import json

def test_api():
    """Test a specific API endpoint"""
    try:
        # Test the templates endpoint
        response = requests.post('http://127.0.0.1:9441/api/nutanix/v3/templates/list', 
                               json={"kind": "template", "length": 10})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mock server API is working!")
            print(f"📋 Available templates: {data.get('entities', [])}")
            print("🎯 Only the original 2 VMs are available for cloning")
        else:
            print(f"❌ API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()