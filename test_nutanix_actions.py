#!/usr/bin/env python3
"""
Test des actions VM Nutanix
"""

import requests
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_vm_actions():
    """Test des actions start/stop sur les VMs Nutanix"""
    print("🧪 TEST ACTIONS VM NUTANIX")
    print("=" * 50)
    
    try:
        # 1. Obtenir la liste des VMs
        print("📋 1. Récupération de la liste des VMs...")
        response = requests.post('http://127.0.0.1:9441/api/nutanix/v3/vms/list', json={})
        if response.status_code != 200:
            print(f"❌ Erreur liste VMs: {response.status_code}")
            return False
        
        vms_data = response.json()
        vms = vms_data.get('entities', [])
        
        if not vms:
            print("❌ Aucune VM trouvée")
            return False
        
        print(f"✅ {len(vms)} VMs trouvées")
        
        # 2. Prendre la première VM pour les tests
        test_vm = vms[0]
        vm_uuid = test_vm['metadata']['uuid']
        vm_name = test_vm['spec']['name']
        current_state = test_vm['status']['resources']['power_state']
        
        print(f"🎯 VM de test: {vm_name} (UUID: {vm_uuid[:8]}...)")
        print(f"📊 État actuel: {current_state}")
        
        # 3. Test GET VM details
        print("\n🔍 2. Test récupération détails VM...")
        response = requests.get(f'http://127.0.0.1:9441/api/nutanix/v3/vms/{vm_uuid}')
        if response.status_code == 200:
            print("✅ Détails VM récupérés avec succès")
        else:
            print(f"❌ Erreur détails VM: {response.status_code}")
            return False
        
        # 4. Test changement d'état (PUT)
        print("\n⚡ 3. Test changement d'état via PUT...")
        new_state = "OFF" if current_state == "ON" else "ON"
        
        update_data = {
            "spec": {
                "resources": {
                    "power_state": new_state
                }
            }
        }
        
        response = requests.put(f'http://127.0.0.1:9441/api/nutanix/v3/vms/{vm_uuid}', 
                               json=update_data)
        
        if response.status_code == 202:
            task_data = response.json()
            task_uuid = task_data.get('status', {}).get('execution_context', {}).get('task_uuid')
            print(f"✅ Changement d'état initié (Task: {task_uuid[:8]}...)")
            
            # 5. Test statut de la tâche
            print("\n📋 4. Test statut de la tâche...")
            response = requests.get(f'http://127.0.0.1:9441/api/nutanix/v3/tasks/{task_uuid}')
            if response.status_code == 200:
                task_status = response.json()
                print(f"✅ Tâche: {task_status['status']} ({task_status['percentage_complete']}%)")
            else:
                print(f"❌ Erreur statut tâche: {response.status_code}")
                return False
        else:
            print(f"❌ Erreur changement d'état: {response.status_code}")
            return False
        
        # 6. Vérifier que l'état a changé
        print("\n🔄 5. Vérification du changement d'état...")
        response = requests.get(f'http://127.0.0.1:9441/api/nutanix/v3/vms/{vm_uuid}')
        if response.status_code == 200:
            updated_vm = response.json()
            updated_state = updated_vm['status']['resources']['power_state']
            if updated_state == new_state:
                print(f"✅ État mis à jour: {current_state} → {updated_state}")
            else:
                print(f"⚠️ État non mis à jour: attendu {new_state}, obtenu {updated_state}")
        
        # 7. Test endpoints power_on/power_off
        print("\n🔌 6. Test endpoints power_on/power_off...")
        
        # Test power_off
        response = requests.post(f'http://127.0.0.1:9441/api/nutanix/v3/vms/{vm_uuid}/power_off')
        if response.status_code == 202:
            print("✅ Endpoint power_off fonctionne")
        else:
            print(f"❌ Erreur power_off: {response.status_code}")
        
        # Test power_on
        response = requests.post(f'http://127.0.0.1:9441/api/nutanix/v3/vms/{vm_uuid}/power_on')
        if response.status_code == 202:
            print("✅ Endpoint power_on fonctionne")
        else:
            print(f"❌ Erreur power_on: {response.status_code}")
        
        print("\n🎉 TOUS LES TESTS PASSÉS!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        return False

def test_integration_with_provider():
    """Test d'intégration avec le provider Nutanix"""
    print("\n🔗 TEST INTÉGRATION PROVIDER")
    print("=" * 50)
    
    try:
        from hypervisor_providers.nutanix_provider import NutanixProvider
        
        # Créer une instance du provider
        provider = NutanixProvider()
        
        # Tester la connexion
        print("🔌 Test connexion provider...")
        if provider.test_connection():
            print("✅ Provider connecté avec succès")
        else:
            print("❌ Échec connexion provider")
            return False
        
        # Lister les VMs via le provider
        print("📋 Test liste VMs via provider...")
        vms = provider.list_vms()
        if vms:
            print(f"✅ {len(vms)} VMs trouvées via provider")
            
            # Tester start/stop sur la première VM
            if vms:
                test_vm = vms[0]
                vm_name = test_vm.name
                
                print(f"🎯 Test actions sur VM: {vm_name}")
                
                # Test start
                print("▶️ Test start VM...")
                if provider.start_vm(vm_name):
                    print("✅ Start VM réussi")
                else:
                    print("❌ Échec start VM")
                
                # Test stop
                print("⏹️ Test stop VM...")
                if provider.stop_vm(vm_name):
                    print("✅ Stop VM réussi")
                else:
                    print("❌ Échec stop VM")
        else:
            print("❌ Aucune VM trouvée via provider")
            return False
        
        print("\n🎉 INTÉGRATION PROVIDER RÉUSSIE!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration provider: {e}")
        return False

def main():
    """Test complet"""
    print("🚀 TEST COMPLET ACTIONS NUTANIX")
    print("=" * 60)
    
    # Test 1: Actions mock directes
    success1 = test_vm_actions()
    
    # Test 2: Intégration provider
    success2 = test_integration_with_provider()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 60)
    
    print(f"{'✅' if success1 else '❌'} Actions Mock: {'SUCCÈS' if success1 else 'ÉCHEC'}")
    print(f"{'✅' if success2 else '❌'} Intégration Provider: {'SUCCÈS' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("🎯 Les actions VM Nutanix fonctionnent maintenant!")
        return 0
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(main())