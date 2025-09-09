#!/usr/bin/env python3
"""
Quick test to simulate Nutanix without real environment
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hypervisor_manager import HypervisorManager

def simulate_nutanix_config():
    """Simulate Nutanix configuration for testing"""
    print("🧪 SIMULATION : Configuration Nutanix pour Tests")
    print("=" * 60)
    
    manager = HypervisorManager()
    
    # Configuration de test (ne se connectera pas vraiment)
    test_config = {
        'enabled': True,
        'prism_central_ip': '192.168.1.100',  # IP fictive
        'username': 'admin',
        'password': 'test123',
        'port': 9440
    }
    
    print("📝 Configuration de test :")
    print(f"   IP : {test_config['prism_central_ip']}")
    print(f"   User : {test_config['username']}")
    print(f"   Port : {test_config['port']}")
    
    # Appliquer la configuration
    success = manager.update_provider_config('nutanix', test_config)
    
    if success:
        print("✅ Configuration appliquée (mode simulation)")
    else:
        print("❌ Erreur de configuration")
        return False
    
    # Vérifier le statut
    status = manager.get_provider_status()
    nutanix_status = status.get('nutanix', {})
    
    print(f"\n📊 Statut Nutanix :")
    print(f"   Enabled : {'✅' if nutanix_status.get('enabled') else '❌'}")
    print(f"   Connected : {'🟢' if nutanix_status.get('connected') else '🔴'} (Normal en simulation)")
    
    print(f"\n🌐 Dans l'interface web, vous verrez maintenant :")
    print(f"   VMware Workstation (Ready)")
    print(f"   Nutanix AHV (Not Connected) - Normal sans vrai cluster")
    
    print(f"\n💡 Pour un vrai environnement Nutanix :")
    print(f"   1. Installer Nutanix CE (gratuit)")
    print(f"   2. Ou utiliser Nutanix Test Drive")
    print(f"   3. Ou demander accès à un cluster existant")
    
    return True

def main():
    """Main function"""
    try:
        simulate_nutanix_config()
        
        print("\n" + "=" * 60)
        print("🎯 SYSTÈME PRÊT POUR TESTS")
        print("=" * 60)
        print("✅ VMware : Fonctionnel")
        print("⚙️ Nutanix : Configuré (simulation)")
        print("🌐 Interface : http://localhost:5000")
        print("\n🚀 Vous pouvez maintenant tester l'interface multi-hypervisor !")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())