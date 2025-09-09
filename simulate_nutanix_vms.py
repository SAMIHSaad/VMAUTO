#!/usr/bin/env python3
"""
Simulate Nutanix VMs for testing without real environment
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def simulate_nutanix_vms():
    """Simulate a list of Nutanix VMs"""
    print("🧪 SIMULATION : Liste des VMs Nutanix")
    print("=" * 50)
    
    # VMs simulées
    simulated_vms = [
        {
            "name": "web-server-01",
            "uuid": "12345678-1234-1234-1234-123456789001",
            "power_state": "ON",
            "cpu_cores": 4,
            "memory_mb": 8192,
            "disk_gb": 100,
            "ip_address": "192.168.1.10",
            "os": "Ubuntu 22.04",
            "cluster": "nutanix-cluster-01"
        },
        {
            "name": "database-server",
            "uuid": "12345678-1234-1234-1234-123456789002", 
            "power_state": "ON",
            "cpu_cores": 8,
            "memory_mb": 16384,
            "disk_gb": 500,
            "ip_address": "192.168.1.11",
            "os": "Windows Server 2022",
            "cluster": "nutanix-cluster-01"
        },
        {
            "name": "test-vm-ubuntu",
            "uuid": "12345678-1234-1234-1234-123456789003",
            "power_state": "OFF",
            "cpu_cores": 2,
            "memory_mb": 4096,
            "disk_gb": 50,
            "ip_address": "192.168.1.12",
            "os": "Ubuntu 20.04",
            "cluster": "nutanix-cluster-01"
        },
        {
            "name": "dev-environment",
            "uuid": "12345678-1234-1234-1234-123456789004",
            "power_state": "ON",
            "cpu_cores": 6,
            "memory_mb": 12288,
            "disk_gb": 200,
            "ip_address": "192.168.1.13",
            "os": "CentOS 8",
            "cluster": "nutanix-cluster-01"
        }
    ]
    
    print(f"📊 Trouvé {len(simulated_vms)} VMs Nutanix (simulées)")
    print("-" * 50)
    
    # Affichage formaté
    for vm in simulated_vms:
        status_icon = "🟢" if vm["power_state"] == "ON" else "🔴"
        print(f"{status_icon} {vm['name']}")
        print(f"   UUID: {vm['uuid']}")
        print(f"   État: {vm['power_state']}")
        print(f"   CPU: {vm['cpu_cores']} cores")
        print(f"   RAM: {vm['memory_mb']} MB")
        print(f"   Disque: {vm['disk_gb']} GB")
        print(f"   IP: {vm['ip_address']}")
        print(f"   OS: {vm['os']}")
        print(f"   Cluster: {vm['cluster']}")
        print()
    
    # Statistiques
    running_vms = len([vm for vm in simulated_vms if vm["power_state"] == "ON"])
    stopped_vms = len([vm for vm in simulated_vms if vm["power_state"] == "OFF"])
    
    print("📈 Statistiques:")
    print(f"   🟢 VMs en marche: {running_vms}")
    print(f"   🔴 VMs arrêtées: {stopped_vms}")
    print(f"   📊 Total: {len(simulated_vms)}")
    
    return simulated_vms

def simulate_nutanix_resources():
    """Simulate Nutanix clusters, networks, templates"""
    print("\n🌐 RESSOURCES NUTANIX SIMULÉES")
    print("=" * 50)
    
    # Clusters simulés
    clusters = ["nutanix-cluster-01", "nutanix-cluster-02"]
    print(f"🏢 Clusters: {clusters}")
    
    # Réseaux simulés
    networks = ["vlan-100-prod", "vlan-200-dev", "vlan-300-test"]
    print(f"🌐 Réseaux: {networks}")
    
    # Templates simulés
    templates = [
        "ubuntu-22.04-template",
        "windows-server-2022-template", 
        "centos-8-template",
        "rhel-9-template"
    ]
    print(f"📋 Templates: {templates}")

def main():
    """Main function"""
    print("🚀 SIMULATION NUTANIX - LISTE DES VMs")
    print("=" * 60)
    
    # Simuler les VMs
    vms = simulate_nutanix_vms()
    
    # Simuler les ressources
    simulate_nutanix_resources()
    
    print("\n" + "=" * 60)
    print("💡 POUR VOIR DE VRAIES VMs NUTANIX:")
    print("=" * 60)
    print("1. 🆓 Installer Nutanix CE (gratuit)")
    print("2. 🌐 Utiliser Nutanix Test Drive")
    print("3. 🏢 Accéder à un cluster d'entreprise")
    print("4. ☁️ Utiliser Nutanix Cloud")
    
    print("\n🔧 COMMANDES DISPONIBLES:")
    print("   python vm_manager_new.py list nutanix")
    print("   python vm_manager_new.py status nutanix") 
    print("   python vm_manager_new.py templates nutanix")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())