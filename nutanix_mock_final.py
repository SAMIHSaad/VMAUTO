#!/usr/bin/env python3
"""
Nutanix Mock Server Final - Port différent pour éviter les conflits
"""

from flask import Flask, request, jsonify
import json
import uuid
import threading
import time

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

@app.route('/')
def health():
    return jsonify({"status": "Mock Nutanix Server Running", "vms": len(MOCK_VMS)})

def run_server():
    """Démarrer le serveur dans un thread"""
    app.run(host='127.0.0.1', port=9441, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("🚀 SERVEUR MOCK NUTANIX FINAL")
    print("=" * 40)
    print("🌐 URL: http://127.0.0.1:9441")
    print("📊 VMs: 6")
    print("🏢 Clusters: 2")
    print("=" * 40)
    
    # Démarrer dans un thread pour éviter les blocages
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Attendre un peu puis tester
    time.sleep(2)
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:9441')
        if response.status_code == 200:
            print("✅ Serveur mock démarré avec succès!")
            print("🎯 Prêt pour les tests Nutanix")
        else:
            print("❌ Problème avec le serveur mock")
    except:
        print("⚠️ Impossible de tester le serveur")
    
    # Garder le serveur en vie
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur mock")