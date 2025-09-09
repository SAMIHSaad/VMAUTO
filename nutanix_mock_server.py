#!/usr/bin/env python3
"""
Nutanix Mock Server - Simule un vrai serveur Nutanix Prism Central
Répond aux mêmes APIs que Nutanix pour que notre système le voit comme réel
"""

from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime
import ssl
import threading
import time

app = Flask(__name__)

# Données simulées qui ressemblent à de vraies VMs Nutanix
MOCK_VMS = [
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2025-09-03T12:00:00Z",
            "last_update_time": "2025-09-03T12:00:00Z"
        },
        "spec": {
            "name": "Windows Server 2019",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 1,
                "memory_size_mib": 4096,
                "disk_list": [
                    {
                        "disk_size_mib": 81920,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.1.10"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "OFF"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2025-09-03T12:00:00Z",
            "last_update_time": "2025-09-03T12:00:00Z"
        },
        "spec": {
            "name": "Ubuntu 64-bit (3)",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 1,
                "memory_size_mib": 2048,
                "disk_list": [
                    {
                        "disk_size_mib": 40960,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.1.11"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "OFF"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-01-15T10:30:00Z",
            "last_update_time": "2024-01-15T10:30:00Z"
        },
        "spec": {
            "name": "web-server-prod-01",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 2,
                "memory_size_mib": 8192,
                "disk_list": [
                    {
                        "disk_size_mib": 102400,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.100.10"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "ON"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-01-10T14:20:00Z",
            "last_update_time": "2024-01-10T14:20:00Z"
        },
        "spec": {
            "name": "database-server-prod",
            "resources": {
                "num_vcpus_per_socket": 4,
                "num_sockets": 2,
                "memory_size_mib": 32768,
                "disk_list": [
                    {
                        "disk_size_mib": 512000,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.100.11"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "ON"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-02-01T09:15:00Z",
            "last_update_time": "2024-02-01T09:15:00Z"
        },
        "spec": {
            "name": "dev-environment-01",
            "resources": {
                "num_vcpus_per_socket": 3,
                "num_sockets": 2,
                "memory_size_mib": 16384,
                "disk_list": [
                    {
                        "disk_size_mib": 204800,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.200.20"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-dev-001",
                "name": "Development-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "ON"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-02-05T16:45:00Z",
            "last_update_time": "2024-02-05T16:45:00Z"
        },
        "spec": {
            "name": "test-vm-centos",
            "resources": {
                "num_vcpus_per_socket": 1,
                "num_sockets": 2,
                "memory_size_mib": 4096,
                "disk_list": [
                    {
                        "disk_size_mib": 51200,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "192.168.200.21"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-dev-001",
                "name": "Development-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "OFF"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-01-20T11:00:00Z",
            "last_update_time": "2024-01-20T11:00:00Z"
        },
        "spec": {
            "name": "backup-server",
            "resources": {
                "num_vcpus_per_socket": 2,
                "num_sockets": 2,
                "memory_size_mib": 12288,
                "disk_list": [
                    {
                        "disk_size_mib": 1024000,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "10.0.10.50"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "ON"
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": "2024-01-25T13:30:00Z",
            "last_update_time": "2024-01-25T13:30:00Z"
        },
        "spec": {
            "name": "monitoring-stack",
            "resources": {
                "num_vcpus_per_socket": 3,
                "num_sockets": 2,
                "memory_size_mib": 24576,
                "disk_list": [
                    {
                        "disk_size_mib": 307200,
                        "device_properties": {
                            "device_type": "DISK"
                        }
                    }
                ],
                "nic_list": [
                    {
                        "ip_endpoint_list": [
                            {
                                "ip": "10.0.10.51"
                            }
                        ]
                    }
                ]
            },
            "cluster_reference": {
                "uuid": "cluster-prod-001",
                "name": "Production-Cluster"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "ON"
            }
        }
    }
]

MOCK_CLUSTERS = [
    {
        "metadata": {
            "uuid": "cluster-prod-001"
        },
        "spec": {
            "name": "Production-Cluster",
            "resources": {
                "config": {
                    "service_list": ["AOS"]
                }
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "nodes": {
                    "hypervisor_server_list": [
                        {"ip": "192.168.1.101"},
                        {"ip": "192.168.1.102"},
                        {"ip": "192.168.1.103"},
                        {"ip": "192.168.1.104"}
                    ]
                }
            }
        }
    },
    {
        "metadata": {
            "uuid": "cluster-dev-001"
        },
        "spec": {
            "name": "Development-Cluster",
            "resources": {
                "config": {
                    "service_list": ["AOS"]
                }
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "nodes": {
                    "hypervisor_server_list": [
                        {"ip": "192.168.1.201"},
                        {"ip": "192.168.1.202"}
                    ]
                }
            }
        }
    }
]

MOCK_NETWORKS = [
    {
        "metadata": {
            "uuid": str(uuid.uuid4())
        },
        "spec": {
            "name": "Production-VLAN-100",
            "resources": {
                "vlan_id": 100,
                "subnet_list": [
                    {
                        "subnet_ip": "192.168.100.0",
                        "prefix_length": 24,
                        "default_gateway_ip": "192.168.100.1"
                    }
                ]
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4())
        },
        "spec": {
            "name": "Development-VLAN-200",
            "resources": {
                "vlan_id": 200,
                "subnet_list": [
                    {
                        "subnet_ip": "192.168.200.0",
                        "prefix_length": 24,
                        "default_gateway_ip": "192.168.200.1"
                    }
                ]
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4())
        },
        "spec": {
            "name": "Management-VLAN-10",
            "resources": {
                "vlan_id": 10,
                "subnet_list": [
                    {
                        "subnet_ip": "10.0.10.0",
                        "prefix_length": 24,
                        "default_gateway_ip": "10.0.10.1"
                    }
                ]
            }
        }
    }
]

MOCK_IMAGES = [
    {
        "metadata": {
            "uuid": str(uuid.uuid4())
        },
        "spec": {
            "name": "Windows Server 2019",
            "resources": {
                "image_type": "DISK_IMAGE",
                "source_uri": "nfs://storage/windows-server-2019.qcow2"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "size_bytes": 64424509440  # 60 GB
            }
        }
    },
    {
        "metadata": {
            "uuid": str(uuid.uuid4())
        },
        "spec": {
            "name": "Ubuntu 64-bit (3)",
            "resources": {
                "image_type": "DISK_IMAGE",
                "source_uri": "nfs://storage/ubuntu-64bit.qcow2"
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "size_bytes": 21474836480  # 20 GB
            }
        }
    }
]

# Template VMs for cloning
MOCK_TEMPLATES = [
    "Windows Server 2019",
    "Ubuntu 64-bit (3)"
]

# Root route
@app.route('/')
def index():
    """Page d'accueil du serveur mock Nutanix"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nutanix Mock Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ color: #2c5aa0; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px; }}
            .status {{ color: #28a745; font-weight: bold; }}
            .endpoint {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #2c5aa0; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat {{ background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 Nutanix Mock Server</h1>
            <p class="status">✅ Server is running and healthy</p>
            
            <div class="stats">
                <div class="stat">
                    <h3>{len(MOCK_VMS)}</h3>
                    <p>Mock VMs</p>
                </div>
                <div class="stat">
                    <h3>{len(MOCK_CLUSTERS)}</h3>
                    <p>Clusters</p>
                </div>
                <div class="stat">
                    <h3>{len(MOCK_NETWORKS)}</h3>
                    <p>Networks</p>
                </div>
                <div class="stat">
                    <h3>{len(MOCK_TEMPLATES)}</h3>
                    <p>Templates</p>
                </div>
            </div>
            
            <h2>Available API Endpoints</h2>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/vms/list - List VMs</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/clusters/list - List Clusters</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/subnets/list - List Networks</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/images/list - List Images</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/templates/list - List Templates</div>
            <div class="endpoint"><strong>GET</strong> /api/nutanix/v3/vms/&lt;uuid&gt; - Get VM Details</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/vms - Create VM</div>
            <div class="endpoint"><strong>PUT</strong> /api/nutanix/v3/vms/&lt;uuid&gt; - Update VM</div>
            <div class="endpoint"><strong>DELETE</strong> /api/nutanix/v3/vms/&lt;uuid&gt; - Delete VM</div>
            <div class="endpoint"><strong>POST</strong> /api/nutanix/v3/vms/&lt;uuid&gt;/clone - Clone VM</div>
            <div class="endpoint"><strong>GET</strong> /api/nutanix/v3/tasks/&lt;uuid&gt; - Get Task Status</div>
            
            <h2>Mock Data</h2>
            <p><strong>VMs:</strong> {', '.join([vm['spec']['name'] for vm in MOCK_VMS])}</p>
            <p><strong>Templates:</strong> {', '.join(MOCK_TEMPLATES)}</p>
            <p><strong>Clusters:</strong> {', '.join([cluster['spec']['name'] for cluster in MOCK_CLUSTERS])}</p>
            
            <hr style="margin: 30px 0;">
            <p><em>This is a mock server for testing purposes. It simulates Nutanix Prism Central API v3.</em></p>
        </div>
    </body>
    </html>
    """

# Routes API Nutanix v3
@app.route('/api/nutanix/v3/vms/list', methods=['POST'])
def list_vms():
    """Liste des VMs - Format Nutanix v3 API"""
    return jsonify({
        "api_version": "3.1",
        "metadata": {
            "total_matches": len(MOCK_VMS),
            "length": len(MOCK_VMS)
        },
        "entities": MOCK_VMS
    })

@app.route('/api/nutanix/v3/clusters/list', methods=['POST'])
def list_clusters():
    """Liste des clusters - Format Nutanix v3 API"""
    return jsonify({
        "api_version": "3.1",
        "metadata": {
            "total_matches": len(MOCK_CLUSTERS),
            "length": len(MOCK_CLUSTERS)
        },
        "entities": MOCK_CLUSTERS
    })

@app.route('/api/nutanix/v3/subnets/list', methods=['POST'])
def list_networks():
    """Liste des réseaux - Format Nutanix v3 API"""
    return jsonify({
        "api_version": "3.1",
        "metadata": {
            "total_matches": len(MOCK_NETWORKS),
            "length": len(MOCK_NETWORKS)
        },
        "entities": MOCK_NETWORKS
    })

@app.route('/api/nutanix/v3/images/list', methods=['POST'])
def list_images():
    """Liste des images/templates - Format Nutanix v3 API"""
    return jsonify({
        "api_version": "3.1",
        "metadata": {
            "total_matches": len(MOCK_IMAGES),
            "length": len(MOCK_IMAGES)
        },
        "entities": MOCK_IMAGES
    })

@app.route('/api/nutanix/v3/templates/list', methods=['POST'])
def list_templates():
    """Liste des templates - Format Nutanix v3 API"""
    return jsonify({
        "api_version": "3.1",
        "metadata": {
            "total_matches": len(MOCK_TEMPLATES),
            "length": len(MOCK_TEMPLATES)
        },
        "entities": MOCK_TEMPLATES
    })

@app.route('/api/nutanix/v3/vms/<vm_uuid>', methods=['GET'])
def get_vm(vm_uuid):
    """Détails d'une VM spécifique"""
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            return jsonify(vm)
    return jsonify({"error": "VM not found"}), 404

@app.route('/api/nutanix/v3/vms', methods=['POST'])
def create_vm():
    """Créer une nouvelle VM"""
    data = request.get_json()
    
    new_vm = {
        "metadata": {
            "uuid": str(uuid.uuid4()),
            "creation_time": datetime.utcnow().isoformat() + "Z",
            "last_update_time": datetime.utcnow().isoformat() + "Z"
        },
        "spec": data.get("spec", {}),
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "OFF"
            }
        }
    }
    
    MOCK_VMS.append(new_vm)
    return jsonify(new_vm), 201

@app.route('/api/nutanix/v3/vms/<vm_uuid>', methods=['PUT'])
def update_vm(vm_uuid):
    """Mettre à jour une VM (démarrer/arrêter)"""
    data = request.get_json()
    print(f"🔄 Update VM request for UUID: {vm_uuid}")
    print(f"📋 Update data: {data}")
    
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            # Update VM spec
            if 'spec' in data:
                vm['spec'].update(data['spec'])
                
                # Update power state in status as well
                if 'resources' in data['spec'] and 'power_state' in data['spec']['resources']:
                    power_state = data['spec']['resources']['power_state']
                    vm['status']['resources']['power_state'] = power_state
                    print(f"🔋 Updated power state to: {power_state}")
            
            vm['metadata']['last_update_time'] = datetime.utcnow().isoformat() + "Z"
            
            # Return task response (like real Nutanix)
            task_uuid = str(uuid.uuid4())
            task_response = {
                "status": {
                    "state": "QUEUED",
                    "execution_context": {
                        "task_uuid": task_uuid
                    }
                }
            }
            
            # Store task for later retrieval
            MOCK_TASKS[task_uuid] = {
                "uuid": task_uuid,
                "status": "SUCCEEDED",
                "percentage_complete": 100,
                "operation_type": "UPDATE",
                "entity_list": [{"entity_type": "vm", "entity_id": vm_uuid}]
            }
            
            print(f"✅ VM update task created: {task_uuid}")
            return jsonify(task_response), 202
    
    return jsonify({"error": "VM not found"}), 404

@app.route('/api/nutanix/v3/vms/<vm_uuid>', methods=['DELETE'])
def delete_vm(vm_uuid):
    """Supprimer une VM"""
    global MOCK_VMS
    MOCK_VMS = [vm for vm in MOCK_VMS if vm['metadata']['uuid'] != vm_uuid]
    return jsonify({"message": "VM deleted"}), 200

@app.route('/api/nutanix/v3/vms/<vm_uuid>/clone', methods=['POST'])
def clone_vm(vm_uuid):
    """Cloner une VM existante"""
    data = request.get_json()
    print(f"🔄 Clone VM request for UUID: {vm_uuid}")
    print(f"📋 Clone data: {data}")
    
    # Find source VM
    source_vm = None
    for vm in MOCK_VMS:
        if vm['metadata']['uuid'] == vm_uuid:
            source_vm = vm
            break
    
    if not source_vm:
        print(f"❌ Source VM not found: {vm_uuid}")
        return jsonify({"error": "Source VM not found"}), 404
    
    # Get clone specifications
    spec_list = data.get('spec_list', [])
    if not spec_list:
        print("❌ No clone specifications provided")
        return jsonify({"error": "No clone specifications provided"}), 400
    
    clone_spec = spec_list[0]  # Take the first spec
    clone_name = clone_spec.get('name', f"clone-of-{source_vm['spec']['name']}")
    
    print(f"🔄 Cloning '{source_vm['spec']['name']}' to '{clone_name}'")
    
    # Create cloned VM
    clone_uuid = str(uuid.uuid4())
    clone_vm_data = {
        "api_version": "3.1.0",
        "metadata": {
            "kind": "vm",
            "uuid": clone_uuid,
            "creation_time": datetime.utcnow().isoformat() + "Z",
            "last_update_time": datetime.utcnow().isoformat() + "Z",
            "spec_version": 1
        },
        "spec": {
            "name": clone_name,
            "resources": {
                "num_vcpus_per_socket": clone_spec.get('num_vcpus_per_socket', source_vm['spec']['resources']['num_vcpus_per_socket']),
                "num_sockets": clone_spec.get('num_sockets', source_vm['spec']['resources']['num_sockets']),
                "memory_size_mib": clone_spec.get('memory_size_mib', source_vm['spec']['resources']['memory_size_mib']),
                "power_state": "OFF",
                "cluster_reference": source_vm['spec']['resources'].get('cluster_reference', {
                    "kind": "cluster",
                    "uuid": "cluster-1"
                }),
                "nic_list": source_vm['spec']['resources'].get('nic_list', []),
                "disk_list": source_vm['spec']['resources'].get('disk_list', [])
            }
        },
        "status": {
            "state": "COMPLETE",
            "resources": {
                "power_state": "OFF"
            }
        }
    }
    
    # Add to mock VMs list
    MOCK_VMS.append(clone_vm_data)
    
    # Create task response (Nutanix returns a task for clone operations)
    task_uuid = str(uuid.uuid4())
    task_response = {
        "status": {
            "state": "SUCCEEDED",
            "execution_context": {
                "task_uuid": task_uuid
            }
        },
        "api_version": "3.1.0",
        "metadata": {
            "kind": "task",
            "uuid": task_uuid
        }
    }
    
    print(f"✅ VM cloned successfully: {clone_name} (UUID: {clone_uuid})")
    print(f"📋 Task UUID: {task_uuid}")
    
    return jsonify(task_response), 202

@app.route('/api/nutanix/v3/tasks/<task_uuid>', methods=['GET'])
def get_task_status(task_uuid):
    """Obtenir le statut d'une tâche"""
    print(f"📋 Task status request for UUID: {task_uuid}")
    
    # For simplicity, all tasks are considered completed successfully
    # In a real Nutanix environment, tasks would have different states
    task_data = {
        "api_version": "3.1.0",
        "metadata": {
            "kind": "task",
            "uuid": task_uuid,
            "creation_time": datetime.utcnow().isoformat() + "Z",
            "last_update_time": datetime.utcnow().isoformat() + "Z"
        },
        "status": "SUCCEEDED",
        "progress_message": "Task completed successfully",
        "percentage_complete": 100,
        "operation_type": "CLONE_VM",
        "start_time": datetime.utcnow().isoformat() + "Z",
        "completion_time": datetime.utcnow().isoformat() + "Z"
    }
    
    print(f"✅ Task {task_uuid} status: SUCCEEDED")
    return jsonify(task_data), 200

# Route de santé
@app.route('/api/nutanix/v3/clusters/list', methods=['GET'])
def health_check():
    """Check de santé pour la connexion"""
    return jsonify({"status": "healthy", "version": "mock-1.0"})

def run_mock_server():
    """Démarrer le serveur mock"""
    print("🚀 DÉMARRAGE SERVEUR MOCK NUTANIX")
    print("=" * 50)
    print("🌐 URL: http://127.0.0.1:9441")
    print("📊 VMs simulées: 6")
    print("🏢 Clusters: 2")
    print("🌐 Réseaux: 3")
    print(f"📋 Templates: {len(MOCK_TEMPLATES)}")
    print("=" * 50)
    
    # Run without SSL on port 9441 to match hypervisor_config.json
    app.run(host='127.0.0.1', port=9441, debug=False, threaded=True)

if __name__ == '__main__':
    run_mock_server()