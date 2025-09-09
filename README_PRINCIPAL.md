# 🚀 Auto-Creation-VM - Système de Gestion Multi-Hyperviseur

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.2+-green.svg)](https://flask.palletsprojects.com)
[![VMware](https://img.shields.io/badge/VMware-Workstation-orange.svg)](https://vmware.com)
[![Nutanix](https://img.shields.io/badge/Nutanix-AHV-purple.svg)](https://nutanix.com)

## 🎯 **Qu'est-ce que Auto-Creation-VM ?**

**Auto-Creation-VM** est une solution complète et moderne qui unifie la gestion de machines virtuelles sur différents hyperviseurs (VMware Workstation et Nutanix AHV) via une interface unique et intuitive.

### ✨ **Fonctionnalités Principales**
- 🌐 **Interface Web moderne** avec dashboard temps réel
- 🖥️ **CLI Python complet** pour automatisation
- 🪟 **Scripts PowerShell natifs** pour Windows
- 🔌 **Architecture modulaire** extensible
- 🧪 **Tests automatisés** avec serveur mock intégré
- 📁 **Organisation automatique** des VMs
- 🔐 **Authentification JWT** sécurisée

---

## 📚 **Documentation Disponible**

### 🎯 **Pour Commencer Rapidement**
- **[📋 REFERENCE_RAPIDE.md](REFERENCE_RAPIDE.md)** - Démarrage en 30 secondes, commandes essentielles
- **[🚀 Guide de Démarrage Rapide](#-démarrage-rapide)** - Installation et première utilisation

### 🏗️ **Pour Comprendre l'Architecture**
- **[📖 GUIDE_ARCHITECTURE_PROJET.md](GUIDE_ARCHITECTURE_PROJET.md)** - Explication détaillée de chaque fichier et composant
- **[🔧 Architecture Technique](#-architecture-technique)** - Vue d'ensemble du système

### 📖 **Documentation Technique Complète**
- **[📄 DOCUMENTATION_TECHNIQUE.tex](DOCUMENTATION_TECHNIQUE.tex)** - Documentation LaTeX complète
- **[📋 README_DOCUMENTATION.md](README_DOCUMENTATION.md)** - Guide de compilation de la documentation
- **[🔨 compile_documentation.bat](compile_documentation.bat)** - Script de génération PDF

---

## 🚀 **Démarrage Rapide**

### 1️⃣ **Installation**
```bash
# Cloner le projet
git clone <repository-url>
cd Auto-Creation-VM

# Installer les dépendances Python
pip install -r requirements.txt
```

### 2️⃣ **Configuration**
```bash
# Copier et éditer la configuration
cp hypervisor_config.json.example hypervisor_config.json
# Éditer avec vos paramètres VMware/Nutanix
```

### 3️⃣ **Démarrage**
```bash
# Démarrer l'application web
python app.py

# Accéder à l'interface : http://localhost:5000
```

### 4️⃣ **Première VM**
- Via **Interface Web** : Onglet "Créer VM"
- Via **CLI** : `python vm_manager.py --create --name "test-vm"`
- Via **PowerShell** : `.\vm_manager.ps1 -Action create -Name "test-vm"`

---

## 🏗️ **Architecture Technique**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACES UTILISATEUR                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Interface Web │   CLI Python    │   Scripts PowerShell   │
│   (Flask + JS)  │   (vm_manager)  │   (Windows natif)      │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE ORCHESTRATION                      │
├─────────────────────────────────────────────────────────────┤
│  HypervisorManager + VM Organizer + IP Manager             │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                 PROVIDERS HYPERVISEURS                     │
├─────────────────────────────────────────────────────────────┤
│  VMware Provider          │  Nutanix Provider              │
│  (vmrun + VMX)           │  (REST API v3)                 │
└─────────────────────────────────────────────────────────────┘
```

### 🔑 **Composants Clés**
- **`app.py`** - Application web Flask avec API REST
- **`hypervisor_manager.py`** - Orchestrateur central multi-hyperviseur
- **`vm_manager.py`** - Interface CLI principale
- **`hypervisor_providers/`** - Providers modulaires (VMware, Nutanix)
- **`frontend/`** - Interface web moderne
- **`nutanix_mock_server.py`** - Serveur de simulation pour tests

---

## 🎛️ **Interfaces Utilisateur**

### 🌐 **Interface Web**
- **Dashboard** temps réel avec statut VMs
- **Création VM** via formulaire intuitif
- **Gestion complète** : Start/Stop/Clone/Delete
- **Multi-hyperviseur** : Sélection VMware ou Nutanix
- **Authentification** JWT sécurisée

### 🖥️ **CLI Python**
```bash
# Exemples d'utilisation
python vm_manager.py --list                    # Lister VMs
python vm_manager.py --create --name "test"    # Créer VM
python vm_manager.py --clone --source "template" --name "new-vm"
python vm_manager.py --start --name "test"     # Démarrer VM
```

### 🪟 **Scripts PowerShell**
```powershell
# Interface native Windows
.\vm_manager.ps1 -Action list
.\New-VMFromClone.ps1 -TemplateName "ubuntu-template"
.\New-NutanixVM.ps1 -VMName "nutanix-vm"
```

### 🌐 **API REST**
- **14+ endpoints** pour intégration
- **Documentation** automatique via Flask
- **Authentification** JWT
- **Support** multi-hyperviseur

---

## 🔧 **Configuration**

### 📝 **hypervisor_config.json**
```json
{
  "vmware": {
    "vmrun_path": "C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe",
    "templates_directory": "C:/VM_Templates",
    "default_vm_directory": "C:/VMs"
  },
  "nutanix": {
    "prism_central_ip": "10.0.0.100",
    "username": "admin",
    "password": "password",
    "default_cluster": "cluster01"
  }
}
```

### 🗄️ **Base de Données**
- **MySQL** pour utilisateurs et sessions
- **Configuration automatique** au premier démarrage
- **Hachage bcrypt** pour mots de passe

---

## 🧪 **Tests et Validation**

### 🔬 **Suite de Tests Complète**
```bash
# Tests système complets
python test_multi_hypervisor.py

# Tests spécifiques
python test_vm_creation.py
python test_nutanix_config.py
```

### 🎭 **Serveur Mock Nutanix**
- **Simulation complète** de l'API Prism Central
- **Tests sans infrastructure** Nutanix réelle
- **Démarrage automatique** avec l'application
- **Données réalistes** pour validation

---

## 📁 **Organisation Automatique**

Le système organise automatiquement vos VMs dans une structure pérenne :

```
permanent_vms/
├── 2024-01-15_ma-vm/
│   ├── vm_files/              # Fichiers VM (.vmx, .vmdk)
│   ├── metadata.json          # Informations VM
│   ├── backup_script.bat      # Script de sauvegarde
│   ├── snapshot_script.bat    # Script de snapshot
│   └── README.md              # Documentation VM
```

---

## 🛠️ **Prérequis**

### 🐍 **Python**
- Python 3.8+ avec pip
- Packages : Flask, requests, bcrypt, PyJWT, etc.

### 🖥️ **VMware Workstation**
- Version 15.0+ avec vmrun.exe
- Templates VM configurés

### ☁️ **Nutanix (Optionnel)**
- Accès Prism Central
- Credentials administrateur
- Ou utilisation du serveur mock

### 🗄️ **MySQL**
- Serveur MySQL 5.7+
- Base de données `autocreationvm`

---

## 🚨 **Dépannage**

### ❌ **Problèmes Courants**

| **Problème** | **Solution** |
|--------------|--------------|
| `vmrun not found` | Vérifier chemin dans `hypervisor_config.json` |
| `Connection refused` | Vérifier IP/credentials Nutanix |
| `Module not found` | `pip install -r requirements.txt` |
| `Port already in use` | Changer port ou arrêter processus |

### 🔍 **Diagnostic**
```bash
# Test système complet
python test_multi_hypervisor.py

# Vérification API
curl http://localhost:5000/api/providers/status

# Logs détaillés
tail -f flask_app.log
```

---

## 🔄 **Extensibilité**

### ➕ **Ajouter un Nouvel Hyperviseur**
1. Créer provider héritant de `BaseHypervisorProvider`
2. Implémenter méthodes obligatoires
3. Ajouter configuration JSON
4. Intégrer dans `HypervisorManager`
5. Ajouter tests spécifiques

### 🔌 **Intégrations Possibles**
- **Terraform** pour Infrastructure as Code
- **Ansible** pour configuration automatique
- **Prometheus/Grafana** pour monitoring
- **CI/CD** pipelines pour déploiement

---

## 📊 **Statistiques du Projet**

- **🐍 Python** : ~3000 lignes de code
- **🌐 JavaScript** : Interface web responsive
- **🪟 PowerShell** : Scripts natifs Windows
- **📖 Documentation** : LaTeX professionnel
- **🧪 Tests** : 15+ fichiers de validation
- **🔌 API** : 14+ endpoints REST

---

## 🤝 **Contribution**

### 📋 **Structure pour Développeurs**
1. **Lire** `GUIDE_ARCHITECTURE_PROJET.md` pour comprendre l'architecture
2. **Consulter** `REFERENCE_RAPIDE.md` pour les commandes essentielles
3. **Tester** avec `python test_multi_hypervisor.py`
4. **Documenter** les changements dans LaTeX

### 🔧 **Développement**
```bash
# Setup développement
git clone <repo>
pip install -r requirements.txt
python test_multi_hypervisor.py  # Validation

# Tests avant commit
python test_multi_hypervisor.py
python test_vm_creation.py
```

---

## 📄 **Licence**

Ce projet est sous licence [MIT](LICENSE) - voir le fichier LICENSE pour détails.

---

## 🎉 **Remerciements**

- **VMware** pour l'API vmrun
- **Nutanix** pour l'API REST v3
- **Flask** pour le framework web
- **Communauté Python** pour les outils

---

## 📞 **Support**

- **📖 Documentation** : Voir guides dans le projet
- **🧪 Tests** : `python test_multi_hypervisor.py`
- **🔍 Logs** : `flask_app.log`, `vm_organizer.log`
- **🌐 API** : `http://localhost:5000/api/providers/status`

---

**Auto-Creation-VM** - *Unifiez votre gestion de machines virtuelles !* 🚀