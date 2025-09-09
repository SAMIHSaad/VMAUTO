#!/usr/bin/env python3
"""
Check system status after restart
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hypervisor_manager import HypervisorManager
from ip_manager import initialize_ip_pool, get_available_ip

def check_system_status():
    print("=== System Status Check After Restart ===")
    
    # Check IP pool
    print("1. IP Pool Status:")
    try:
        initialize_ip_pool()
        ip = get_available_ip()
        print(f"   Available IP: {ip}")
        if not ip:
            print("   WARNING: No available IPs!")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Check hypervisor manager
    print("2. Hypervisor Manager:")
    try:
        hm = HypervisorManager()
        status = hm.get_provider_status()
        print(f"   Providers found: {list(status.keys())}")
        
        for name, stat in status.items():
            enabled = stat.get('enabled', False)
            connected = stat.get('connected', False)
            print(f"   {name}: enabled={enabled}, connected={connected}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Check VM list
    print("3. VM List:")
    try:
        vms = hm.list_vms()
        print(f"   Total VMs: {len(vms)}")
        
        if len(vms) > 0:
            print("   Recent VMs:")
            for vm in vms[:10]:  # Show first 10
                name = vm.get('name', 'Unknown')
                hypervisor = vm.get('hypervisor', 'Unknown')
                state = vm.get('state', 'Unknown')
                print(f"   - {name} [{hypervisor}] - {state}")
            
            if len(vms) > 10:
                print(f"   ... and {len(vms) - 10} more")
        else:
            print("   No VMs found!")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Check if mock server is responding
    print("4. Mock Server Status:")
    try:
        import requests
        response = requests.get('http://127.0.0.1:9441/api/nutanix/v3/clusters/list', timeout=5)
        if response.status_code == 200:
            print("   ✅ Nutanix mock server is responding")
        else:
            print(f"   ❌ Mock server returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Mock server not accessible: {e}")
    
    print("\n=== Recommendations ===")
    if not ip:
        print("- Release some IPs from the pool for testing")
    print("- Ensure both Flask app and mock server are running")
    print("- Clean output directories before VM creation")

if __name__ == "__main__":
    check_system_status()