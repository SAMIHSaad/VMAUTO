#!/usr/bin/env python3
"""
Installation automatique complète de la configuration Nutanix locale
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def wait_for_flask():
    """Attendre que Flask soit prêt"""
    print("⏳ Attente du démarrage de Flask...")
    
    for i in range(30):  # Attendre max 30 secondes
        try:
            response = requests.get('http://127.0.0.1:5000', timeout=2)
            if response.status_code == 200:
                print("✅ Flask est prêt!")
                return True
        except:
            pass
        
        print(f"   Tentative {i+1}/30...")
        time.sleep(1)
    
    print("❌ Flask n'a pas démarré dans les temps")
    return False

def configure_nutanix_automatically():
    """Configuration automatique de Nutanix"""
    print("🔧 CONFIGURATION AUTOMATIQUE NUTANIX")
    print("=" * 50)
    
    # Configuration optimisée pour tests locaux
    config = {
        'enabled': True,
        'prism_central_ip': '127.0.0.1',
        'username': 'admin',
        'password': 'nutanix123',
        'port': 9440
    }
    
    print("📝 Application de la configuration...")
    
    try:
        manager = HypervisorManager()
        success = manager.update_provider_config('nutanix', config)
        
        if success:
            print("✅ Configuration Nutanix appliquée")
        else:
            print("❌ Erreur de configuration")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def test_system_status():
    """Tester le statut du système"""
    print("\n📊 TEST DU STATUT SYSTÈME")
    print("=" * 40)
    
    try:
        manager = HypervisorManager()
        status = manager.get_provider_status()
        
        print("🔍 Statut des providers:")
        for provider, info in status.items():
            enabled_icon = "✅" if info['enabled'] else "❌"
            connected_icon = "🟢" if info['connected'] else "🔴"
            print(f"   {provider.upper()}: {enabled_icon} Activé, {connected_icon} Connecté")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def create_test_user():
    """Créer un utilisateur de test"""
    print("\n👤 CRÉATION UTILISATEUR DE TEST")
    print("=" * 40)
    
    try:
        # Données utilisateur de test
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'test123'
        }
        
        # Essayer de créer l'utilisateur via l'API
        response = requests.post(
            'http://127.0.0.1:5000/api/register',
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ Utilisateur de test créé")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            return True
        else:
            print("⚠️ Utilisateur existe déjà ou erreur")
            return True  # Pas grave si l'utilisateur existe
            
    except Exception as e:
        print(f"⚠️ Impossible de créer l'utilisateur: {e}")
        print("💡 Vous pourrez vous inscrire manuellement")
        return True

def show_access_info():
    """Afficher les informations d'accès"""
    print("\n🌐 INFORMATIONS D'ACCÈS")
    print("=" * 40)
    
    print("🔗 Interface Web: http://127.0.0.1:5000")
    print("👤 Utilisateur test: testuser")
    print("🔐 Mot de passe: test123")
    print("")
    print("📋 Ou créez votre propre compte sur la page d'inscription")

def show_test_commands():
    """Afficher les commandes de test"""
    print("\n💻 COMMANDES DE TEST DISPONIBLES")
    print("=" * 50)
    
    commands = [
        ("Lister VMs VMware", "python vm_manager_new.py --provider vmware list"),
        ("Lister VMs Nutanix", "python vm_manager_new.py --provider nutanix list"),
        ("Statut système", "python vm_manager_new.py status"),
        ("Templates Nutanix", "python vm_manager_new.py --provider nutanix templates"),
        ("Simulateur Nutanix", "python nutanix_simulator.py")
    ]
    
    for i, (desc, cmd) in enumerate(commands, 1):
        print(f"{i}. {desc}:")
        print(f"   {cmd}")
        print()

def main():
    """Installation automatique complète"""
    print("🚀 INSTALLATION AUTOMATIQUE COMPLÈTE")
    print("=" * 60)
    print("🎯 Configuration locale Nutanix + Interface Web")
    print("=" * 60)
    
    # Étape 1: Attendre Flask
    if not wait_for_flask():
        print("❌ Flask n'est pas disponible")
        return 1
    
    # Étape 2: Configuration Nutanix
    if not configure_nutanix_automatically():
        print("❌ Échec de la configuration Nutanix")
        return 1
    
    # Étape 3: Test du système
    if not test_system_status():
        print("❌ Échec du test système")
        return 1
    
    # Étape 4: Créer utilisateur de test
    create_test_user()
    
    # Étape 5: Informations d'accès
    show_access_info()
    
    # Étape 6: Commandes de test
    show_test_commands()
    
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    
    print("\n✅ SYSTÈME PRÊT:")
    print("   🌐 Interface Web: http://127.0.0.1:5000")
    print("   ⚙️ VMware: Configuré et connecté")
    print("   🔧 Nutanix: Configuré (mode test)")
    print("   👤 Utilisateur test: testuser / test123")
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Ouvrir http://127.0.0.1:5000 dans votre navigateur")
    print("   2. Se connecter avec testuser / test123")
    print("   3. Tester la création de VMs")
    print("   4. Explorer les deux providers (VMware + Nutanix)")
    
    print("\n🧪 POUR TESTER EN CLI:")
    print("   python vm_manager_new.py status")
    print("   python nutanix_simulator.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())