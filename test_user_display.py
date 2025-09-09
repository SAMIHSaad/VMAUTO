#!/usr/bin/env python3
"""
Test script to verify that the username is correctly displayed from the JWT token.
"""

import requests
import json
import random
import string

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

def generate_random_user():
    """Generate a random test user to avoid conflicts"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "Nom": "TestLast",
        "Prenom": "TestFirst", 
        "Username": f"testuser_{random_suffix}",
        "password": "testpass123"
    }

def test_user_display():
    """Test that the username is correctly extracted from the JWT token"""
    
    print("🧪 Testing User Display from JWT Token")
    print("=" * 50)
    
    # Generate a unique test user
    TEST_USER = generate_random_user()
    print(f"Generated test user: {TEST_USER['Username']}")
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    register_response = requests.post(
        f"{BASE_URL}/api/register",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code == 201:
        print("✅ User registered successfully")
    else:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    # Step 2: Login with the test user
    print("2. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"Username": TEST_USER["Username"], "password": TEST_USER["password"]},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    print("✅ Login successful")
    
    # Extract cookies from login response
    cookies = login_response.cookies
    
    # Step 3: Get user profile to verify token content
    print("3. Getting user profile...")
    profile_response = requests.get(
        f"{BASE_URL}/api/profile",
        cookies=cookies
    )
    
    if profile_response.status_code != 200:
        print(f"❌ Profile request failed: {profile_response.text}")
        return False
    
    profile_data = profile_response.json()
    print("✅ Profile retrieved successfully")
    
    # Step 4: Verify the user data structure
    print("4. Verifying user data structure...")
    logged_in_user = profile_data.get("logged_in_as")
    
    if not logged_in_user:
        print("❌ No user data found in profile response")
        return False
    
    print(f"📋 User data structure: {json.dumps(logged_in_user, indent=2)}")
    
    # Check if all required fields are present
    required_fields = ["Username", "Nom", "Prenom"]
    missing_fields = []
    
    for field in required_fields:
        if field not in logged_in_user:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing fields in user data: {missing_fields}")
        return False
    
    # Step 5: Verify the username field specifically
    print("5. Verifying username field...")
    username = logged_in_user.get("Username")
    
    if username != TEST_USER["Username"]:
        print(f"❌ Username mismatch. Expected: {TEST_USER['Username']}, Got: {username}")
        return False
    
    print(f"✅ Username field correct: {username}")
    
    # Step 6: Test the display logic (simulating frontend logic)
    print("6. Testing display logic...")
    firstName = logged_in_user.get("Prenom", "")
    lastName = logged_in_user.get("Nom", "")
    username = logged_in_user.get("Username", "User")
    
    if firstName or lastName:
        display_name = f"{firstName} {lastName}".strip()
    else:
        display_name = username
    
    print(f"✅ Display name would be: '{display_name}'")
    
    # Step 7: Test the specific case that was fixed
    print("7. Testing the specific fix...")
    print(f"   - currentUser.Username (correct): '{logged_in_user.get('Username', 'NOT_FOUND')}'")
    print(f"   - currentUser.username (incorrect): '{logged_in_user.get('username', 'NOT_FOUND')}'")
    
    if logged_in_user.get("Username"):
        print("✅ The fix is working - Username field (capital U) is accessible")
    else:
        print("❌ The fix failed - Username field is not accessible")
        return False
    
    print("\n🎉 All tests passed! The username should now display correctly in the frontend.")
    return True

if __name__ == "__main__":
    try:
        success = test_user_display()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()