#!/usr/bin/env python3
"""
Simple script to start the Nutanix mock server
"""

import subprocess
import sys
import time
import requests

def check_mock_server_health():
    """Check if the mock server is running and accessible"""
    try:
        response = requests.get('http://127.0.0.1:9441/api/nutanix/v3/clusters/list', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def start_mock_server():
    """Start the mock server if it's not already running"""
    
    # Check if already running
    if check_mock_server_health():
        print("✅ Nutanix mock server is already running and healthy")
        return True
    
    print("Starting Nutanix mock server...")
    
    try:
        # Start the mock server
        process = subprocess.Popen(
            [sys.executable, 'nutanix_mock_server.py'],
            cwd='c:\\Users\\saads\\OneDrive\\Documents\\Coding\\Auto-Creation-VM'
        )
        
        print(f"Mock server started with PID: {process.pid}")
        
        # Wait for it to start
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            if check_mock_server_health():
                print("✅ Nutanix mock server is running and healthy")
                return True
            print(f"Waiting for server to start... ({i+1}/10)")
        
        print("❌ Mock server failed to become healthy")
        return False
        
    except Exception as e:
        print(f"Failed to start mock server: {e}")
        return False

if __name__ == '__main__':
    start_mock_server()