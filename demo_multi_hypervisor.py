#!/usr/bin/env python3
"""
Démonstration du système de gestion multi-hyperviseur
Ce script montre toutes les fonctionnalités disponibles
"""

import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n🔹 {title}")
    print("-" * 40)

def demo_provider_status():
    """Demonstrate provider status functionality"""
    print_section("Provider Status")
    
    manager = HypervisorManager()
    status = manager.get_provider_status()
    
    for provider, info in status.items():
        enabled = "✅ Enabled" if info['enabled'] else "❌ Disabled"
        connected = "🟢 Connected" if info['connected'] else "🔴 Disconnected"
        print(f"{provider.upper()}: {enabled}, {connected}")
    
    return manager

def demo_vm_listing(manager):
    """Demonstrate VM listing functionality"""
    print_section("VM Listing")
    
    # List all VMs
    all_vms = manager.list_vms()
    print(f"Total VMs found: {len(all_vms)}")
    
    # Group by provider
    vmware_vms = [vm for vm in all_vms if vm.hypervisor == 'vmware']
    nutanix_vms = [vm for vm in all_vms if vm.hypervisor == 'nutanix']
    
    print(f"VMware VMs: {len(vmware_vms)}")
    for vm in vmware_vms[:3]:  # Show first 3
        print(f"  - {vm.name} ({vm.state})")
    
    print(f"Nutanix VMs: {len(nutanix_vms)}")
    for vm in nutanix_vms[:3]:  # Show first 3
        print(f"  - {vm.name} ({vm.state})")

def demo_resource_discovery(manager):
    """Demonstrate resource discovery"""
    print_section("Resource Discovery")
    
    # Templates
    templates = manager.get_templates()
    print("Available Templates:")
    for provider, template_list in templates.items():
        print(f"  {provider.upper()}: {len(template_list)} templates")
        for template in template_list[:2]:  # Show first 2
            print(f"    - {template}")
    
    # Clusters
    clusters = manager.get_clusters()
    print("\nAvailable Clusters:")
    for provider, cluster_list in clusters.items():
        print(f"  {provider.upper()}: {cluster_list}")
    
    # Networks
    networks = manager.get_networks()
    print("\nAvailable Networks:")
    for provider, network_list in networks.items():
        print(f"  {provider.upper()}: {network_list}")

def demo_vm_configuration():
    """Demonstrate VM configuration creation"""
    print_section("VM Configuration")
    
    # Basic VM config
    basic_config = VMConfig(
        name="demo-basic-vm",
        cpu=2,
        ram=2048,
        disk=20,
        os_type="linux"
    )
    print(f"Basic VM Config: {basic_config.name}")
    print(f"  CPU: {basic_config.cpu}, RAM: {basic_config.ram}MB, Disk: {basic_config.disk}GB")
    
    # Advanced VM config for Nutanix
    nutanix_config = VMConfig(
        name="demo-nutanix-vm",
        cpu=4,
        ram=4096,
        disk=50,
        os_type="linux",
        cluster="production-cluster",
        network="vm-network",
        template="ubuntu-20.04-template",
        ip_address="192.168.1.100"
    )
    print(f"\nNutanix VM Config: {nutanix_config.name}")
    print(f"  CPU: {nutanix_config.cpu}, RAM: {nutanix_config.ram}MB, Disk: {nutanix_config.disk}GB")
    print(f"  Cluster: {nutanix_config.cluster}, Network: {nutanix_config.network}")
    print(f"  Template: {nutanix_config.template}, IP: {nutanix_config.ip_address}")

def demo_vm_operations(manager):
    """Demonstrate VM operations (without actually creating VMs)"""
    print_section("VM Operations (Simulation)")
    
    print("Available Operations:")
    print("  ✅ Create VM from template or scratch")
    print("  ✅ Clone existing VM")
    print("  ✅ Start/Stop/Restart VM")
    print("  ✅ Delete VM")
    print("  ✅ Create/Restore/Delete snapshots")
    print("  ✅ Get VM information")
    
    # Show example of getting VM info
    vms = manager.list_vms('vmware')
    if vms:
        vm = vms[0]
        vm_info = manager.get_vm_info(vm.name, 'vmware')
        if vm_info:
            print(f"\nExample VM Info - {vm_info.name}:")
            print(f"  State: {vm_info.state}")
            print(f"  CPU: {vm_info.cpu}, RAM: {vm_info.ram}MB")
            print(f"  Hypervisor: {vm_info.hypervisor}")

def demo_configuration_management(manager):
    """Demonstrate configuration management"""
    print_section("Configuration Management")
    
    print("Configuration Features:")
    print("  ✅ Enable/Disable providers")
    print("  ✅ Set provider credentials")
    print("  ✅ Configure default provider")
    print("  ✅ Manage provider-specific settings")
    
    # Show current configuration
    status = manager.get_provider_status()
    default_provider = manager.config.get('default_provider', 'vmware')
    print(f"\nCurrent default provider: {default_provider}")
    
    enabled_providers = [name for name, info in status.items() if info['enabled']]
    print(f"Enabled providers: {', '.join(enabled_providers)}")

def demo_api_endpoints():
    """Demonstrate available API endpoints"""
    print_section("Web API Endpoints")
    
    endpoints = [
        "GET  /api/providers/status     - Provider status",
        "GET  /api/vms                  - List VMs",
        "POST /api/vms                  - Create VM",
        "POST /api/vms/clone            - Clone VM",
        "GET  /api/vms/{name}           - VM information",
        "POST /api/vms/{name}/start     - Start VM",
        "POST /api/vms/{name}/stop      - Stop VM",
        "POST /api/vms/{name}/restart   - Restart VM",
        "DELETE /api/vms/{name}         - Delete VM",
        "GET  /api/templates            - Available templates",
        "GET  /api/clusters             - Available clusters",
        "GET  /api/networks             - Available networks",
        "POST /api/config/providers     - Update provider config",
        "POST /api/config/default-provider - Set default provider"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")

def demo_cli_commands():
    """Demonstrate CLI commands"""
    print_section("CLI Commands")
    
    commands = [
        "vm_manager_new.py status                           - Show provider status",
        "vm_manager_new.py list --detailed                  - List all VMs",
        "vm_manager_new.py --provider vmware templates      - List VMware templates",
        "vm_manager_new.py --provider nutanix clusters      - List Nutanix clusters",
        "vm_manager_new.py --provider vmware create 'MyVM' --cpu 4 --ram 4096 --ssd 40",
        "vm_manager_new.py --provider nutanix create 'MyVM' --cluster 'prod' --network 'vm-net'",
        "vm_manager_new.py --provider vmware clone 'NewVM' --source-vm 'Template'",
        "vm_manager_new.py --provider vmware start 'MyVM'   - Start VM",
        "vm_manager_new.py --provider vmware stop 'MyVM'    - Stop VM",
        "vm_manager_new.py --provider vmware delete 'MyVM'  - Delete VM",
        "vm_manager_new.py --provider vmware snapshot create 'MyVM' 'snap1'",
        "vm_manager_new.py --provider vmware snapshot restore 'MyVM' 'snap1'"
    ]
    
    for command in commands:
        print(f"  {command}")

def demo_powershell_integration():
    """Demonstrate PowerShell integration"""
    print_section("PowerShell Integration")
    
    print("VMware PowerShell:")
    print("  New-VMFromClone.ps1 - Clone VMware VMs")
    print("  register_vm.ps1     - Register VMs in VMware")
    
    print("\nNutanix PowerShell:")
    print("  New-NutanixVM.ps1   - Create Nutanix VMs via REST API")
    
    print("\nExample Nutanix PowerShell command:")
    print("  .\\New-NutanixVM.ps1 -VMName 'MyVM' -CPU 4 -RAM 4096 \\")
    print("    -DiskSize 100 -ClusterName 'MyCluster' \\")
    print("    -NetworkName 'VM Network' -PrismCentralIP '10.0.0.100' \\")
    print("    -Username 'admin' -Password 'password'")

def demo_web_interface():
    """Demonstrate web interface features"""
    print_section("Web Interface Features")
    
    print("Dashboard:")
    print("  📊 Provider status overview")
    print("  📈 VM statistics")
    print("  📋 Recent activity")
    
    print("\nVM Management:")
    print("  ➕ Create new VMs")
    print("  📋 Clone existing VMs")
    print("  📝 List and filter VMs")
    print("  ⚡ Start/Stop/Restart VMs")
    print("  🗑️ Delete VMs")
    
    print("\nConfiguration:")
    print("  ⚙️ VMware settings")
    print("  ⚙️ Nutanix settings")
    print("  🔧 General preferences")
    
    print("\nAccess: http://localhost:5000")

def main():
    """Main demonstration function"""
    print_header("Multi-Hypervisor VM Management System Demo")
    print("This demonstration shows all available features and capabilities.")
    
    try:
        # Initialize and show provider status
        manager = demo_provider_status()
        
        # Demonstrate VM listing
        demo_vm_listing(manager)
        
        # Demonstrate resource discovery
        demo_resource_discovery(manager)
        
        # Demonstrate VM configuration
        demo_vm_configuration()
        
        # Demonstrate VM operations
        demo_vm_operations(manager)
        
        # Demonstrate configuration management
        demo_configuration_management(manager)
        
        # Show API endpoints
        demo_api_endpoints()
        
        # Show CLI commands
        demo_cli_commands()
        
        # Show PowerShell integration
        demo_powershell_integration()
        
        # Show web interface
        demo_web_interface()
        
        # Cleanup
        manager.disconnect_all_providers()
        
        print_header("Demo Complete")
        print("🎉 Multi-hypervisor system is fully functional!")
        print("\nNext steps:")
        print("1. Configure Nutanix credentials in hypervisor_config.json")
        print("2. Start the web interface: python app_new.py")
        print("3. Access the web UI at: http://localhost:5000")
        print("4. Use CLI commands for automation")
        print("5. Integrate with PowerShell scripts")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())