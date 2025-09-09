#!/usr/bin/env python3
"""
Simple Nutanix Mock Server - Version simplifiée qui fonctionne
"""

from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime

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

if __name__ == '__main__':
    print("🚀 SERVEUR MOCK NUTANIX SIMPLE")
    print("=" * 40)
    print("🌐 URL: http://127.0.0.1:9440")
    print("📊 VMs: 6")
    print("🏢 Clusters: 2")
    print("=" * 40)
    app.run(host='127.0.0.1', port=9440, debug=False)