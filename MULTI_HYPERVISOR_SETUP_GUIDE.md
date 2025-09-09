# Multi-Hypervisor VM Management Setup Guide

Ce guide vous aidera à configurer et utiliser le système de gestion de VMs multi-hyperviseur qui supporte VMware Workstation et Nutanix AHV.

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration VMware](#configuration-vmware)
4. [Configuration Nutanix](#configuration-nutanix)
5. [Utilisation CLI](#utilisation-cli)
6. [Utilisation Web](#utilisation-web)
7. [Tests](#tests)
8. [Dépannage](#dépannage)

## 🔧 Prérequis

### Système
- Windows 10/11
- Python 3.8 ou supérieur
- PowerShell 5.1 ou supérieur

### VMware (optionnel)
- VMware Workstation Pro/Player installé
- vmrun.exe accessible dans le PATH ou à l'emplacement par défaut

### Nutanix (optionnel)
- Accès à un cluster Nutanix avec Prism Central
- Credentials d'administration
- Connectivité réseau vers Prism Central (port 9440)

### Python Dependencies
```bash
pip install requests urllib3 flask flask-mysqldb flask-jwt-extended bcrypt
```

## 🚀 Installation

1. **Cloner ou télécharger le projet**
   ```bash
   cd c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM
   ```

2. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Vérifier la structure des fichiers**
   ```
   Auto-Creation-VM/
   ├── hypervisor_providers/
   │   ├── __init__.py
   │   ├── base_provider.py
   │   ├── vmware_provider.py
   │   └── nutanix_provider.py
   ├── hypervisor_manager.py
   ├── vm_manager_new.py
   ├── app_new.py
   ├── frontend/
   │   ├── index_new.html
   │   ├── style_new.css
   │   └── script_new.js
   ├── hypervisor_config.json
   └── test_multi_hypervisor.py
   ```

## ⚙️ Configuration VMware

### 1. Configuration automatique
Le système détecte automatiquement VMware Workstation s'il est installé dans l'emplacement par défaut.

### 2. Configuration manuelle
Éditez `hypervisor_config.json` :

```json
{
  "providers": {
    "vmware": {
      "enabled": true,
      "vmrun_path": "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe",
      "base_directory": "c:\\Users\\saads\\OneDrive\\Documents\\Coding\\Auto-Creation-VM",
      "templates_directory": "C:\\Users\\saads\\OneDrive\\Documents\\Virtual Machines"
    }
  }
}
```

### 3. Vérification
```bash
python test_multi_hypervisor.py
```

## 🌐 Configuration Nutanix

### 1. Configuration initiale
Éditez `hypervisor_config.json` :

```json
{
  "providers": {
    "nutanix": {
      "enabled": true,
      "prism_central_ip": "10.0.0.100",
      "prism_element_ip": "10.0.0.101",
      "username": "admin",
      "password": "your_password",
      "port": 9440,
      "verify_ssl": false
    }
  }
}
```

### 2. Test de connectivité
```bash
python -c "
from hypervisor_manager import HypervisorManager
manager = HypervisorManager()
connected = manager.connect_provider('nutanix')
print('Nutanix connection:', 'SUCCESS' if connected else 'FAILED')
"
```

### 3. Configuration via PowerShell
```powershell
.\New-NutanixVM.ps1 -VMName "test-vm" -CPU 2 -RAM 2048 -DiskSize 20 -ClusterName "your-cluster" -NetworkName "your-network" -PrismCentralIP "10.0.0.100" -Username "admin" -Password "password"
```

## 💻 Utilisation CLI

### Commandes de base

```bash
# Lister les providers disponibles
python vm_manager_new.py status

# Créer une VM sur VMware
python vm_manager_new.py create "MyVM" --provider vmware --cpu 4 --ram 4096 --ssd 40

# Créer une VM sur Nutanix
python vm_manager_new.py create "MyNutanixVM" --provider nutanix --cpu 4 --ram 4096 --ssd 40 --cluster "MyCluster" --network "VM Network"

# Cloner une VM
python vm_manager_new.py clone "ClonedVM" --source-vm "SourceVM" --provider vmware

# Lister toutes les VMs
python vm_manager_new.py list --detailed

# Contrôler les VMs
python vm_manager_new.py start "MyVM" --provider vmware
python vm_manager_new.py stop "MyVM" --provider vmware
python vm_manager_new.py restart "MyVM" --provider vmware

# Snapshots
python vm_manager_new.py snapshot create "MyVM" "snapshot1" --provider vmware
python vm_manager_new.py snapshot restore "MyVM" "snapshot1" --provider vmware
python vm_manager_new.py snapshot delete "MyVM" "snapshot1" --provider vmware

# Obtenir des informations
python vm_manager_new.py templates --provider nutanix
python vm_manager_new.py clusters --provider nutanix
python vm_manager_new.py networks --provider nutanix
```

### Exemples avancés

```bash
# Créer une VM Nutanix à partir d'un template
python vm_manager_new.py create "UbuntuVM" \
  --provider nutanix \
  --template "Ubuntu-20.04-Template" \
  --cluster "Production-Cluster" \
  --network "VM-Network" \
  --cpu 4 --ram 8192 --ssd 100

# Créer plusieurs VMs en batch
for i in {1..5}; do
  python vm_manager_new.py create "WebServer-$i" \
    --provider nutanix \
    --cpu 2 --ram 4096 --ssd 50 \
    --cluster "Web-Cluster" \
    --network "Web-Network"
done
```

## 🌐 Utilisation Web

### 1. Démarrer l'application web
```bash
python app_new.py
```

### 2. Accéder à l'interface
Ouvrez votre navigateur et allez à : `http://localhost:5000`

### 3. Fonctionnalités disponibles

#### Dashboard
- Statut des hyperviseurs
- Statistiques des VMs
- Activité récente

#### Création de VM
- Sélection de l'hyperviseur (VMware/Nutanix)
- Configuration des ressources (CPU, RAM, Disque)
- Options spécifiques Nutanix (Cluster, Réseau, Template)

#### Clonage de VM
- Sélection de la VM source
- Configuration de la nouvelle VM
- Support multi-hyperviseur

#### Liste des VMs
- Vue d'ensemble de toutes les VMs
- Filtrage par hyperviseur
- Actions de contrôle (Start/Stop/Restart/Delete)

#### Paramètres
- Configuration VMware
- Configuration Nutanix
- Paramètres généraux

## 🧪 Tests

### Test complet du système
```bash
python test_multi_hypervisor.py
```

### Tests spécifiques

```bash
# Test VMware uniquement
python -c "
from hypervisor_manager import HypervisorManager
manager = HypervisorManager()
print('VMware VMs:', len(manager.list_vms('vmware')))
"

# Test Nutanix uniquement
python -c "
from hypervisor_manager import HypervisorManager
manager = HypervisorManager()
print('Nutanix VMs:', len(manager.list_vms('nutanix')))
"

# Test de création de VM (dry run)
python -c "
from hypervisor_providers import VMConfig
config = VMConfig('test', 2, 2048, 20, 'linux')
print('VM Config created:', config.name)
"
```

## 🔧 Dépannage

### Problèmes VMware

**Erreur : vmrun not found**
```bash
# Vérifier l'installation VMware
"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" list

# Ou mettre à jour le chemin dans hypervisor_config.json
```

**Erreur : VM not found**
```bash
# Vérifier les répertoires de VMs
python vm_manager_new.py templates --provider vmware
```

### Problèmes Nutanix

**Erreur : Connection refused**
```bash
# Tester la connectivité
ping 10.0.0.100
telnet 10.0.0.100 9440
```

**Erreur : Authentication failed**
```bash
# Vérifier les credentials
curl -k -u admin:password https://10.0.0.100:9440/api/nutanix/v3/clusters/list
```

**Erreur : SSL Certificate**
```json
{
  "providers": {
    "nutanix": {
      "verify_ssl": false
    }
  }
}
```

### Problèmes généraux

**Erreur : Module not found**
```bash
pip install -r requirements.txt
```

**Erreur : Permission denied**
```bash
# Exécuter en tant qu'administrateur
# Ou vérifier les permissions sur les répertoires
```

### Logs et debugging

```bash
# Activer le mode debug
export DEBUG=1
python vm_manager_new.py list --detailed

# Vérifier les logs
tail -f logs/vm_manager.log
```

## 📚 Documentation API

### REST API Endpoints

```
GET  /api/providers/status     - Statut des hyperviseurs
GET  /api/vms                  - Liste des VMs
POST /api/vms                  - Créer une VM
POST /api/vms/clone            - Cloner une VM
GET  /api/vms/{name}           - Info VM
POST /api/vms/{name}/start     - Démarrer VM
POST /api/vms/{name}/stop      - Arrêter VM
POST /api/vms/{name}/restart   - Redémarrer VM
DELETE /api/vms/{name}         - Supprimer VM
GET  /api/templates            - Templates disponibles
GET  /api/clusters             - Clusters disponibles
GET  /api/networks             - Réseaux disponibles
```

### Configuration programmatique

```python
from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig

# Initialiser le manager
manager = HypervisorManager()

# Créer une VM
vm_config = VMConfig(
    name="my-vm",
    cpu=4,
    ram=4096,
    disk=50,
    os_type="linux",
    cluster="my-cluster",  # Pour Nutanix
    network="my-network"   # Pour Nutanix
)

result = manager.create_vm(vm_config, "nutanix")
print(result)
```

## 🎯 Bonnes pratiques

1. **Sécurité**
   - Utilisez des mots de passe forts
   - Activez SSL/TLS en production
   - Limitez l'accès réseau

2. **Performance**
   - Surveillez l'utilisation des ressources
   - Utilisez des templates pour accélérer le déploiement
   - Planifiez les snapshots

3. **Maintenance**
   - Sauvegardez régulièrement la configuration
   - Surveillez les logs
   - Testez les restaurations

4. **Monitoring**
   - Utilisez le dashboard pour surveiller l'état
   - Configurez des alertes
   - Documentez les changements

## 📞 Support

Pour obtenir de l'aide :

1. Consultez les logs : `logs/vm_manager.log`
2. Exécutez les tests : `python test_multi_hypervisor.py`
3. Vérifiez la configuration : `hypervisor_config.json`
4. Consultez la documentation API

---

**Note** : Ce système supporte actuellement VMware Workstation et Nutanix AHV. D'autres hyperviseurs peuvent être ajoutés en créant de nouveaux providers dans le dossier `hypervisor_providers/`.