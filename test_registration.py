#!/usr/bin/env python3
"""
Test script to verify registration functionality
"""
import requests
import json

def test_registration():
    """Test the registration endpoint"""
    base_url = "http://localhost:5000"
    
    # Test data
    test_user = {
        "Nom": "Test",
        "Prenom": "User", 
        "Username": "testuser123",
        "password": "testpass123"
    }
    
    print("Testing registration endpoint...")
    print(f"URL: {base_url}/api/register")
    print(f"Data: {json.dumps(test_user, indent=2)}")
    
    try:
        # Make registration request
        response = requests.post(
            f"{base_url}/api/register",
            headers={"Content-Type": "application/json"},
            json=test_user,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        elif response.status_code == 409:
            print("⚠️ User already exists (this is expected if running multiple times)")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
        return False

def test_login():
    """Test login with the registered user"""
    base_url = "http://localhost:5000"
    
    login_data = {
        "Username": "testuser123",
        "password": "testpass123"
    }
    
    print("\nTesting login endpoint...")
    print(f"URL: {base_url}/api/login")
    print(f"Data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/api/login",
            headers={"Content-Type": "application/json"},
            json=login_data,
            timeout=10
        )
        
        print(f"\nLogin Response Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Login Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Login Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Registration and Login Functionality")
    print("=" * 50)
    
    # Test registration
    reg_success = test_registration()
    
    # Test login if registration was successful
    if reg_success:
        login_success = test_login()
        
        if reg_success and login_success:
            print("\n🎉 All tests passed! Registration and login are working correctly.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Registration test failed. Cannot proceed with login test.")