#!/usr/bin/env python3
"""
Final Test: Verify Nutanix shows only original 2 VMs
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from hypervisor_manager import HypervisorManager

def test_nutanix_source_vms():
    """Test that Nutanix only shows the original 2 VMs as source VMs"""
    print("🚀 Final Nutanix Source VM Test")
    print("=" * 60)
    
    try:
        # Initialize hypervisor manager
        hypervisor_manager = HypervisorManager()
        print("✅ Hypervisor manager initialized")
        
        # Get Nutanix templates
        nutanix_templates_dict = hypervisor_manager.get_templates('nutanix')
        print(f"📋 Nutanix Templates Dict: {nutanix_templates_dict}")
        
        # Extract the actual templates list
        nutanix_templates = nutanix_templates_dict.get('nutanix', [])
        print(f"📋 Nutanix Templates List: {nutanix_templates}")
        
        # Expected templates (only the original 2)
        expected_templates = ['Windows Server 2019', 'Ubuntu 64-bit (3)']
        
        print("\n🔍 Verification:")
        success = True
        
        # Check each expected template
        for template in expected_templates:
            if template in nutanix_templates:
                print(f"✅ {template} - Found")
            else:
                print(f"❌ {template} - Missing")
                success = False
        
        # Check for unexpected templates
        unexpected = [t for t in nutanix_templates if t not in expected_templates]
        if unexpected:
            print(f"⚠️  Unexpected templates found: {unexpected}")
            print("   These should be removed for clean source VM selection")
            success = False
        else:
            print("✅ No unexpected templates found")
        
        # Final result
        if success and len(nutanix_templates) == 2:
            print("\n🎉 SUCCESS: Nutanix shows exactly the original 2 VMs!")
            print("   Frontend will now show only:")
            print("   - Windows Server 2019")
            print("   - Ubuntu 64-bit (3)")
            print("   when Nutanix is selected as the provider.")
            return True
        else:
            print(f"\n❌ FAILED: Expected exactly 2 templates {expected_templates}")
            print(f"   Got: {nutanix_templates}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Nutanix templates: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vmware_comparison():
    """Test VMware templates for comparison"""
    print("\n🔧 VMware Templates (for comparison)")
    print("=" * 50)
    
    try:
        hypervisor_manager = HypervisorManager()
        vmware_templates_dict = hypervisor_manager.get_templates('vmware')
        vmware_templates = vmware_templates_dict.get('vmware', [])
        print(f"📋 VMware Templates: {vmware_templates}")
        print("   (VMware may show more templates - this is expected)")
        return True
    except Exception as e:
        print(f"⚠️  VMware test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 FINAL VERIFICATION: Nutanix Source VM Selection")
    print("=" * 70)
    
    # Test Nutanix
    nutanix_success = test_nutanix_source_vms()
    
    # Test VMware for comparison
    vmware_success = test_vmware_comparison()
    
    print("\n📊 Test Summary:")
    print("=" * 40)
    print(f"Nutanix Source VMs: {'✅ CORRECT' if nutanix_success else '❌ NEEDS FIX'}")
    print(f"VMware Templates: {'✅ OK' if vmware_success else '⚠️  CHECK'}")
    
    if nutanix_success:
        print("\n🎯 SOLUTION CONFIRMED:")
        print("   ✅ Nutanix provider shows only original 2 VMs")
        print("   ✅ No additional template VMs are included")
        print("   ✅ Frontend source VM selection will work correctly")
        print("   ✅ Users can now clone from the original VMs only")
        return 0
    else:
        print("\n❌ ISSUE: Nutanix still shows additional templates")
        return 1

if __name__ == "__main__":
    sys.exit(main())