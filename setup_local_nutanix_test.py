#!/usr/bin/env python3
"""
Setup local Nutanix test environment - No real Nutanix required
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def setup_local_test():
    """Configure local test environment"""
    print("🔧 CONFIGURATION ENVIRONNEMENT DE TEST LOCAL")
    print("=" * 60)
    
    # Configuration de test avec IP locale
    test_config = {
        'enabled': True,
        'prism_central_ip': '127.0.0.1',  # IP locale
        'username': 'admin',
        'password': 'test123',
        'port': 9440
    }
    
    print("📝 Configuration de test locale :")
    for key, value in test_config.items():
        if key != 'password':
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {'*' * len(str(value))}")
    
    # Appliquer la configuration
    manager = HypervisorManager()
    success = manager.update_provider_config('nutanix', test_config)
    
    if success:
        print("✅ Configuration appliquée avec succès")
    else:
        print("❌ Erreur lors de la configuration")
        return False
    
    # Vérifier le statut
    print("\n📊 Statut des providers :")
    status = manager.get_provider_status()
    for provider, info in status.items():
        enabled = "✅ Activé" if info['enabled'] else "❌ Désactivé"
        connected = "🟢 Connecté" if info['connected'] else "🔴 Non connecté"
        print(f"   {provider.upper()}: {enabled}, {connected}")
    
    return True

def test_commands():
    """Tester les commandes disponibles"""
    print("\n🧪 TEST DES COMMANDES DISPONIBLES")
    print("=" * 50)
    
    commands = [
        "python vm_manager_new.py --provider nutanix list",
        "python vm_manager_new.py --provider nutanix status", 
        "python vm_manager_new.py --provider nutanix templates",
        "python vm_manager_new.py --provider nutanix clusters",
        "python vm_manager_new.py --provider nutanix networks"
    ]
    
    print("📋 Commandes testables :")
    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. {cmd}")
    
    print("\n💡 Ces commandes fonctionneront avec la configuration locale")
    print("   (Elles montreront des erreurs de connexion, c'est normal)")

def show_web_interface_guide():
    """Guide pour l'interface web"""
    print("\n🌐 GUIDE INTERFACE WEB")
    print("=" * 40)
    
    print("1. 🚀 Ouvrir http://localhost:5000")
    print("2. 🔐 Se connecter avec vos credentials")
    print("3. ⚙️ Aller dans Settings")
    print("4. 🔧 Section Nutanix Configuration :")
    print("   ✅ Cocher 'Enable Nutanix Provider'")
    print("   📍 IP: 127.0.0.1 (ou IP Test Drive)")
    print("   👤 Username: admin")
    print("   🔐 Password: test123 (ou password Test Drive)")
    print("   🌐 Port: 9440")
    print("5. 💾 Cliquer 'Save Nutanix Config'")
    print("6. 🎯 Tester la création de VM avec Nutanix")

def main():
    """Fonction principale"""
    print("🚀 SETUP ENVIRONNEMENT NUTANIX LOCAL")
    print("=" * 60)
    
    # Configuration locale
    if not setup_local_test():
        return 1
    
    # Guide des commandes
    test_commands()
    
    # Guide interface web
    show_web_interface_guide()
    
    print("\n" + "=" * 60)
    print("🎉 ENVIRONNEMENT DE TEST CONFIGURÉ!")
    print("=" * 60)
    
    print("\n🎯 PROCHAINES ÉTAPES :")
    print("1. 🧪 Tester avec simulateur: python nutanix_simulator.py")
    print("2. 🌐 Tester interface web: http://localhost:5000")
    print("3. 💻 Tester CLI: python vm_manager_new.py --provider nutanix list")
    print("4. 🚀 Optionnel: Nutanix Test Drive pour vrai environnement")
    
    print("\n✨ Système multi-hypervisor prêt pour tests!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())