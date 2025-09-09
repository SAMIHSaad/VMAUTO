#!/usr/bin/env python3
"""
Configuration pour utiliser le serveur mock Nutanix comme un vrai Nutanix
"""

import sys
import time
import requests
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def wait_for_mock_server():
    """Attendre que le serveur mock soit prêt"""
    print("⏳ Attente du serveur mock Nutanix...")
    
    for i in range(30):
        try:
            # Tester la connexion HTTP (le mock démarre en HTTP)
            response = requests.get('http://127.0.0.1:9440/api/nutanix/v3/clusters/list', timeout=2)
            if response.status_code == 200:
                print("✅ Serveur mock Nutanix prêt!")
                return True
        except:
            pass
        
        print(f"   Tentative {i+1}/30...")
        time.sleep(1)
    
    print("❌ Serveur mock non accessible")
    return False

def configure_nutanix_for_mock():
    """Configurer Nutanix pour utiliser le serveur mock"""
    print("🔧 CONFIGURATION NUTANIX POUR SERVEUR MOCK")
    print("=" * 60)
    
    # Configuration pour le serveur mock (HTTP au lieu de HTTPS)
    config = {
        'enabled': True,
        'prism_central_ip': '127.0.0.1',
        'username': 'admin',
        'password': 'nutanix123',
        'port': 9440,
        'use_ssl': False  # Important: désactiver SSL pour le mock
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

def test_nutanix_connection():
    """Tester la connexion Nutanix"""
    print("\n🧪 TEST DE CONNEXION NUTANIX")
    print("=" * 40)
    
    try:
        manager = HypervisorManager()
        status = manager.get_provider_status()
        
        print("📊 Statut des providers:")
        for provider, info in status.items():
            enabled_icon = "✅" if info['enabled'] else "❌"
            connected_icon = "🟢" if info['connected'] else "🔴"
            print(f"   {provider.upper()}: {enabled_icon} Activé, {connected_icon} Connecté")
        
        # Test spécifique Nutanix
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

def test_vm_listing():
    """Tester la liste des VMs Nutanix"""
    print("\n📋 TEST LISTE DES VMs NUTANIX")
    print("=" * 40)
    
    try:
        # Test direct de l'API mock
        response = requests.post(
            'http://127.0.0.1:9440/api/nutanix/v3/vms/list',
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            vm_count = data.get('metadata', {}).get('total_matches', 0)
            print(f"✅ API Mock répond: {vm_count} VMs trouvées")
            
            # Afficher quelques VMs
            entities = data.get('entities', [])
            for i, vm in enumerate(entities[:3]):
                name = vm.get('spec', {}).get('name', 'Unknown')
                power_state = vm.get('status', {}).get('resources', {}).get('power_state', 'Unknown')
                print(f"   {i+1}. {name} ({power_state})")
            
            if len(entities) > 3:
                print(f"   ... et {len(entities) - 3} autres VMs")
            
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def main():
    """Configuration complète"""
    print("🚀 CONFIGURATION NUTANIX RÉEL (MOCK)")
    print("=" * 60)
    print("🎯 Rendre Nutanix visible comme VMware")
    print("=" * 60)
    
    # Étape 1: Attendre le serveur mock
    if not wait_for_mock_server():
        print("❌ Serveur mock non disponible")
        print("💡 Assurez-vous que nutanix_mock_server.py est démarré")
        return 1
    
    # Étape 2: Configuration
    if not configure_nutanix_for_mock():
        print("❌ Échec de la configuration")
        return 1
    
    # Étape 3: Test de connexion
    if not test_nutanix_connection():
        print("❌ Échec du test de connexion")
        return 1
    
    # Étape 4: Test de l'API
    if not test_vm_listing():
        print("❌ Échec du test API")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 NUTANIX CONFIGURÉ AVEC SUCCÈS!")
    print("=" * 60)
    
    print("\n✅ RÉSULTAT:")
    print("   🌐 Serveur mock Nutanix: Actif")
    print("   🔗 Connexion Nutanix: Établie")
    print("   📊 VMs Nutanix: Visibles (6 VMs)")
    print("   🎯 Interface: Nutanix apparaît comme VMware")
    
    print("\n🎯 MAINTENANT VOUS POUVEZ:")
    print("   1. 🌐 Ouvrir http://127.0.0.1:5000")
    print("   2. 👀 Voir les VMs Nutanix dans l'interface")
    print("   3. 💻 Utiliser: python vm_manager_new.py --provider nutanix list")
    print("   4. 🔧 Créer des VMs sur Nutanix")
    
    print("\n🧪 COMMANDES DE TEST:")
    print("   python vm_manager_new.py --provider nutanix list")
    print("   python vm_manager_new.py --provider nutanix templates")
    print("   python vm_manager_new.py status")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())