#!/usr/bin/env python3
"""
Guide pour utiliser Nutanix Test Drive - Aucune installation requise
"""

def show_testdrive_guide():
    """Guide pour Nutanix Test Drive"""
    print("🌐 NUTANIX TEST DRIVE - ACCÈS IMMÉDIAT")
    print("=" * 60)
    
    print("\n✨ AVANTAGES:")
    print("   ✅ Aucune installation requise")
    print("   ✅ Environnement pré-configuré")
    print("   ✅ Accès immédiat (5 minutes)")
    print("   ✅ VMs déjà créées pour tester")
    print("   ✅ Complètement gratuit")
    
    print("\n📋 ÉTAPES SIMPLES:")
    print("   1. 🌐 Aller sur: https://www.nutanix.com/test-drive")
    print("   2. 📧 S'inscrire avec votre email")
    print("   3. 🎯 Choisir 'Nutanix Cloud Platform'")
    print("   4. ⏱️ Attendre 2-5 minutes")
    print("   5. 🔑 Recevoir les credentials par email")
    
    print("\n🔑 VOUS RECEVREZ:")
    print("   • URL d'accès: https://xxx.xxx.xxx.xxx:9440")
    print("   • Username: admin")
    print("   • Password: [généré automatiquement]")
    print("   • Durée: 8 heures d'accès")
    
    print("\n🎯 UTILISATION AVEC NOTRE SYSTÈME:")
    print("   1. Copier l'IP reçue")
    print("   2. Ouvrir http://localhost:5000")
    print("   3. Aller dans Settings > Nutanix")
    print("   4. Entrer les credentials reçus")
    print("   5. Tester la liste des VMs!")
    
    return True

def create_testdrive_config():
    """Créer un template de configuration pour Test Drive"""
    print("\n🔧 TEMPLATE DE CONFIGURATION")
    print("=" * 40)
    
    config_template = {
        "prism_central_ip": "[IP_REÇUE_PAR_EMAIL]",
        "username": "admin", 
        "password": "[PASSWORD_REÇU_PAR_EMAIL]",
        "port": 9440
    }
    
    print("📝 Configuration à utiliser:")
    for key, value in config_template.items():
        print(f"   {key}: {value}")
    
    print("\n💡 EXEMPLE RÉEL:")
    print("   prism_central_ip: 34.123.45.67")
    print("   username: admin")
    print("   password: Nutanix123!")
    print("   port: 9440")

def main():
    """Main function"""
    show_testdrive_guide()
    create_testdrive_config()
    
    print("\n" + "=" * 60)
    print("🎉 SOLUTION RECOMMANDÉE: NUTANIX TEST DRIVE")
    print("=" * 60)
    print("⏱️ Temps requis: 5 minutes")
    print("💰 Coût: Gratuit")
    print("🔧 Installation: Aucune")
    print("🎯 Résultat: Environnement Nutanix complet")
    
    return 0

if __name__ == "__main__":
    main()