#!/usr/bin/env python3
"""
Nutanix Mock Server Persistant - Reste en vie même si la fenêtre se ferme
"""

from flask import Flask, request, jsonify
import json
import uuid
import threading
import time
import sys
import os

app = Flask(__name__)

# VMs simulées format Nutanix
MOCK_VMS = [
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "web-server-prod-01",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 2,
                "memory_size_mib": 8192
            }
        },
        "status": {
            "resources": {"power_state": "ON"}
        }
    },
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "database-server-prod",
            "resources": {
                "num_vcpus_per_socket": 4,
                "num_sockets": 2,
                "memory_size_mib": 32768
            }
        },
        "status": {
            "resources": {"power_state": "ON"}
        }
    },
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "dev-environment-01",
            "resources": {
                "num_vcpus_per_socket": 3,
                "num_sockets": 2,
                "memory_size_mib": 16384
            }
        },
        "status": {
            "resources": {"power_state": "ON"}
        }
    },
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "test-vm-centos",
            "resources": {
                "num_vcpus_per_socket": 1,
                "num_sockets": 2,
                "memory_size_mib": 4096
            }
        },
        "status": {
            "resources": {"power_state": "OFF"}
        }
    },
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "backup-server",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 2,
                "memory_size_mib": 12288
            }
        },
        "status": {
            "resources": {"power_state": "ON"}
        }
    },
    {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": "monitoring-stack",
            "resources": {
                "num_vcpus_per_socket": 3,
                "num_sockets": 2,
                "memory_size_mib": 24576
            }
        },
        "status": {
            "resources": {"power_state": "ON"}
        }
    }
]

@app.route('/api/nutanix/v3/vms/list', methods=['POST', 'GET'])
def list_vms():
    """Lister toutes les VMs avec support de filtrage par nom"""
    try:
        # Vérifier si c'est une requête de filtrage par nom
        if request.method == 'POST':
            data = request.get_json() or {}
            filter_criteria = data.get('filter')
            
            if filter_criteria and 'vm_name' in filter_criteria:
                # Filtrer par nom de VM
                vm_name = filter_criteria.split('==')[1].strip().strip("'\"")
                filtered_vms = [vm for vm in MOCK_VMS if vm['spec']['name'] == vm_name]
                return jsonify({
                    "metadata": {"total_matches": len(filtered_vms)},
                    "entities": filtered_vms
                })
        
        # Retourner toutes les VMs
        return jsonify({
            "metadata": {"total_matches": len(MOCK_VMS)},
            "entities": MOCK_VMS
        })
        
    except Exception as e:
        print(f"Erreur dans list_vms: {e}")
        return jsonify({
            "metadata": {"total_matches": len(MOCK_VMS)},
            "entities": MOCK_VMS
        })

@app.route('/api/nutanix/v3/clusters/list', methods=['POST', 'GET'])
def list_clusters():
    return jsonify({
        "metadata": {"total_matches": 2},
        "entities": [
            {"metadata": {"uuid": "cluster-1"}, "spec": {"name": "Production-Cluster"}},
            {"metadata": {"uuid": "cluster-2"}, "spec": {"name": "Development-Cluster"}}
        ]
    })

@app.route('/api/nutanix/v3/subnets/list', methods=['POST', 'GET'])
def list_networks():
    return jsonify({
        "metadata": {"total_matches": 3},
        "entities": [
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "Production-VLAN-100"}},
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "Development-VLAN-200"}},
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "Management-VLAN-10"}}
        ]
    })

@app.route('/api/nutanix/v3/images/list', methods=['POST', 'GET'])
def list_images():
    return jsonify({
        "metadata": {"total_matches": 3},
        "entities": [
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "Ubuntu-22.04-Template"}},
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "Windows-Server-2022-Template"}},
            {"metadata": {"uuid": str(uuid.uuid4())}, "spec": {"name": "CentOS-8-Template"}}
        ]
    })

@app.route('/api/nutanix/v3/vms', methods=['POST'])
def create_vm():
    """Simuler la création d'une VM"""
    data = request.get_json()
    vm_name = data.get('spec', {}).get('name', 'new-vm')
    
    new_vm = {
        "metadata": {"uuid": str(uuid.uuid4())},
        "spec": {
            "name": vm_name,
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 1,
                "memory_size_mib": 4096
            }
        },
        "status": {
            "resources": {"power_state": "OFF"}
        }
    }
    
    MOCK_VMS.append(new_vm)
    return jsonify(new_vm), 201

@app.route('/api/nutanix/v3/vms/<vm_uuid>', methods=['GET'])
def get_vm_details(vm_uuid):
    """Obtenir les détails d'une VM"""
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            return jsonify(vm)
    return jsonify({"error": "VM not found"}), 404

@app.route('/api/nutanix/v3/vms/<vm_uuid>', methods=['PUT'])
def update_vm(vm_uuid):
    """Mettre à jour une VM (utilisé pour changer l'état d'alimentation)"""
    try:
        data = request.get_json()
        
        for vm in MOCK_VMS:
            if vm['metadata']['uuid'] == vm_uuid:
                # Mettre à jour l'état d'alimentation si fourni
                if 'spec' in data and 'resources' in data['spec'] and 'power_state' in data['spec']['resources']:
                    new_power_state = data['spec']['resources']['power_state']
                    vm['status']['resources']['power_state'] = new_power_state
                    
                    # Simuler une tâche asynchrone
                    task_uuid = str(uuid.uuid4())
                    return jsonify({
                        "status": {
                            "state": "QUEUED",
                            "execution_context": {
                                "task_uuid": task_uuid
                            }
                        }
                    }), 202
                
                return jsonify(vm)
        
        return jsonify({"error": "VM not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/nutanix/v3/tasks/<task_uuid>', methods=['GET'])
def get_task_status(task_uuid):
    """Obtenir le statut d'une tâche (toujours succès pour la simulation)"""
    return jsonify({
        "status": "SUCCEEDED",
        "percentage_complete": 100,
        "operation_type": "UPDATE",
        "start_time": "2025-01-01T00:00:00Z",
        "completion_time": "2025-01-01T00:00:01Z"
    })

@app.route('/api/nutanix/v3/vms/<vm_uuid>/power_on', methods=['POST'])
def power_on_vm(vm_uuid):
    """Simuler le démarrage d'une VM"""
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            vm['status']['resources']['power_state'] = 'ON'
            task_uuid = str(uuid.uuid4())
            return jsonify({
                "status": {
                    "state": "QUEUED",
                    "execution_context": {
                        "task_uuid": task_uuid
                    }
                }
            }), 202
    return jsonify({"error": "VM not found"}), 404

@app.route('/api/nutanix/v3/vms/<vm_uuid>/power_off', methods=['POST'])
def power_off_vm(vm_uuid):
    """Simuler l'arrêt d'une VM"""
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            vm['status']['resources']['power_state'] = 'OFF'
            task_uuid = str(uuid.uuid4())
            return jsonify({
                "status": {
                    "state": "QUEUED",
                    "execution_context": {
                        "task_uuid": task_uuid
                    }
                }
            }), 202
    return jsonify({"error": "VM not found"}), 404

@app.route('/')
def health():
    return jsonify({
        "status": "Nutanix Mock Server Running", 
        "vms": len(MOCK_VMS),
        "persistent": True
    })

@app.route('/status')
def status():
    return jsonify({
        "server": "Nutanix Mock Persistent",
        "port": 9441,
        "vms": len(MOCK_VMS),
        "uptime": "Running",
        "endpoints": [
            "/api/nutanix/v3/vms/list",
            "/api/nutanix/v3/clusters/list",
            "/api/nutanix/v3/subnets/list",
            "/api/nutanix/v3/images/list"
        ]
    })

if __name__ == '__main__':
    print("🚀 SERVEUR MOCK NUTANIX PERSISTANT")
    print("=" * 50)
    print("🌐 URL: http://127.0.0.1:9441")
    print("📊 VMs: 6")
    print("🏢 Clusters: 2")
    print("🔒 Mode: Persistant (ne s'arrête pas)")
    print("=" * 50)
    
    # Démarrer le serveur en mode persistant
    try:
        app.run(
            host='127.0.0.1', 
            port=9441, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur mock")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        sys.exit(1)