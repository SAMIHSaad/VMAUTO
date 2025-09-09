#!/usr/bin/env python3
"""
Configuration finale Nutanix - Rendre les VMs Nutanix visibles comme VMware
"""

import sys
import time
import requests
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def configure_nutanix_final():
    """Configuration finale pour Nutanix mock"""
    print("🔧 CONFIGURATION FINALE NUTANIX")
    print("=" * 50)
    
    # Configuration pour le serveur mock sur port 9441
    config = {
        'enabled': True,
        'prism_central_ip': '127.0.0.1',
        'username': 'admin',
        'password': 'nutanix123',
        'port': 9441,
        'use_ssl': False,
        'verify_ssl': False
    }
    
    print("📝 Configuration appliquée:")
    for key, value in config.items():
        if key != 'password':
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {'*' * len(str(value))}")
    
    try:
        manager = HypervisorManager()
        success = manager.update_provider_config('nutanix', config)
        
        if success:
            print("✅ Configuration Nutanix mise à jour")
            return True
        else:
            print("❌ Erreur de configuration")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_nutanix_final():
    """Test final de Nutanix"""
    print("\n🧪 TEST FINAL NUTANIX")
    print("=" * 40)
    
    # Test direct de l'API
    try:
        response = requests.post(
            'http://127.0.0.1:9441/api/nutanix/v3/vms/list',
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            vm_count = data.get('metadata', {}).get('total_matches', 0)
            print(f"✅ API Mock répond: {vm_count} VMs trouvées")
            
            # Afficher les VMs
            entities = data.get('entities', [])
            for i, vm in enumerate(entities):
                name = vm.get('spec', {}).get('name', 'Unknown')
                power_state = vm.get('status', {}).get('resources', {}).get('power_state', 'Unknown')
                cpu_cores = vm.get('spec', {}).get('resources', {}).get('num_vcpus_per_socket', 0) * vm.get('spec', {}).get('resources', {}).get('num_sockets', 0)
                memory_mb = vm.get('spec', {}).get('resources', {}).get('memory_size_mib', 0)
                
                status_icon = "🟢" if power_state == "ON" else "🔴"
                print(f"   {status_icon} {name}")
                print(f"      État: {power_state}")
                print(f"      CPU: {cpu_cores} cores")
                print(f"      RAM: {memory_mb} MB")
                print()
            
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def test_system_status_final():
    """Test final du statut système"""
    print("📊 TEST STATUT SYSTÈME FINAL")
    print("=" * 40)
    
    try:
        manager = HypervisorManager()
        status = manager.get_provider_status()
        
        print("🔍 Statut des providers:")
        for provider, info in status.items():
            enabled_icon = "✅" if info['enabled'] else "❌"
            connected_icon = "🟢" if info['connected'] else "🔴"
            print(f"   {provider.upper()}: {enabled_icon} Activé, {connected_icon} Connecté")
        
        # Vérifier que Nutanix est connecté
        nutanix_status = status.get('nutanix', {})
        if nutanix_status.get('connected'):
            print("\n🎉 NUTANIX CONNECTÉ AVEC SUCCÈS!")
            return True
        else:
            print("\n❌ Nutanix non connecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Configuration finale complète"""
    print("🚀 CONFIGURATION FINALE - NUTANIX VISIBLE")
    print("=" * 60)
    print("🎯 Rendre les VMs Nutanix visibles comme VMware")
    print("=" * 60)
    
    # Attendre un peu pour que le serveur mock soit prêt
    print("⏳ Attente du serveur mock (3 secondes)...")
    time.sleep(3)
    
    # Configuration
    if not configure_nutanix_final():
        print("❌ Échec de la configuration")
        return 1
    
    # Test API
    if not test_nutanix_final():
        print("❌ Échec du test API")
        return 1
    
    # Test système
    if not test_system_status_final():
        print("❌ Échec du test système")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 NUTANIX MAINTENANT VISIBLE COMME VMWARE!")
    print("=" * 60)
    
    print("\n✅ RÉSULTAT:")
    print("   🌐 Interface Web: http://127.0.0.1:5000")
    print("   ⚙️ VMware: 6 VMs réelles")
    print("   🔧 Nutanix: 6 VMs simulées (visibles)")
    print("   🎯 Les deux providers sont maintenant actifs")
    
    print("\n🎯 MAINTENANT VOUS POUVEZ:")
    print("   1. 🌐 Ouvrir http://127.0.0.1:5000")
    print("   2. 👀 Voir les VMs des DEUX providers")
    print("   3. 🔧 Créer des VMs sur VMware OU Nutanix")
    print("   4. 📊 Gérer les VMs des deux côtés")
    
    print("\n🧪 COMMANDES DE TEST:")
    print("   python vm_manager_new.py status")
    print("   python vm_manager_new.py --provider vmware list")
    print("   python vm_manager_new.py --provider nutanix list")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())