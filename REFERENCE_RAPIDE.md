# 🚀 Référence Rapide - Auto-Creation-VM

## ⚡ Démarrage Ultra-Rapide

### 🎯 **En 30 secondes**
```bash
# 1. Installer dépendances
pip install -r requirements.txt

# 2. Configurer hyperviseurs
cp hypervisor_config.json.example hypervisor_config.json
# Éditer avec vos paramètres

# 3. Démarrer l'application
python app.py
# Aller sur http://localhost:5000
```

---

## 📁 **Fichiers Essentiels à Connaître**

| **Fichier** | **Rôle** | **Quand l'utiliser** |
|-------------|----------|----------------------|
| `app.py` | 🌐 Interface web | Démarrer l'app web |
| `vm_manager.py` | 🖥️ CLI principal | Ligne de commande |
| `hypervisor_manager.py` | 🎯 Orchestrateur | Utilisé par autres composants |
| `hypervisor_config.json` | ⚙️ Configuration | Paramétrer hyperviseurs |
| `test_multi_hypervisor.py` | 🧪 Tests | Valider le système |

---

## 🎛️ **Commandes Essentielles**

### 🌐 **Interface Web**
```bash
python app.py                    # Démarrer serveur web
# Puis aller sur http://localhost:5000
```

### 🖥️ **CLI Python**
```bash
python vm_manager.py --list                           # Lister VMs
python vm_manager.py --create --name "test"           # Créer VM
python vm_manager.py --clone --source "template"      # Cloner VM
python vm_manager.py --start --name "test"            # Démarrer VM
python vm_manager.py --organize --name "test"         # Organiser VM
```

### 🪟 **PowerShell**
```powershell
.\vm_manager.ps1 -Action list                         # Lister VMs
.\New-VMFromClone.ps1 -TemplateName "ubuntu"          # Cloner VMware
.\New-NutanixVM.ps1 -VMName "test"                    # Créer Nutanix
```

### 🧪 **Tests**
```bash
python test_multi_hypervisor.py                       # Tests complets
python test_vm_creation.py                            # Tests création
```

### 📖 **Documentation**
```batch
compile_documentation.bat                             # Générer PDF
```

---

## 🔧 **Configuration Rapide**

### 📝 **hypervisor_config.json**
```json
{
  "vmware": {
    "vmrun_path": "C:/Program Files (x86)/VMware/VMware Workstation/vmrun.exe",
    "templates_directory": "C:/VM_Templates"
  },
  "nutanix": {
    "prism_central_ip": "10.0.0.100",
    "username": "admin",
    "password": "password"
  }
}
```

---

## 🌐 **API REST - Endpoints Clés**

| **Méthode** | **Endpoint** | **Description** |
|-------------|--------------|-----------------|
| GET | `/api/vms` | Liste toutes les VMs |
| POST | `/api/vms` | Créer nouvelle VM |
| POST | `/api/vms/clone` | Cloner VM existante |
| GET | `/api/providers/status` | Statut hyperviseurs |
| POST | `/api/vms/{name}/start` | Démarrer VM |
| POST | `/api/vms/{name}/stop` | Arrêter VM |

---

## 🏗️ **Architecture en 1 Minute**

```
Interface Web/CLI/PowerShell
           ↓
    HypervisorManager (orchestrateur)
           ↓
VMware Provider ←→ Nutanix Provider
           ↓
    VMware Workstation / Nutanix AHV
```

---

## 🚨 **Dépannage Express**

### ❌ **Problèmes Courants**

| **Erreur** | **Solution Rapide** |
|------------|---------------------|
| `vmrun not found` | Vérifier chemin dans config |
| `Connection refused` | Vérifier IP Nutanix dans config |
| `Module not found` | `pip install -r requirements.txt` |
| `Port already in use` | Changer port ou tuer processus |
| `Permission denied` | Lancer en administrateur |

### 🔍 **Diagnostic Rapide**
```bash
python test_multi_hypervisor.py    # Test complet système
curl http://localhost:5000/api/providers/status  # Test API
```

---

## 📊 **Structure Projet Simplifiée**

```
Auto-Creation-VM/
├── 🌐 app.py                     # Interface web
├── 🎯 hypervisor_manager.py      # Orchestrateur
├── 🖥️ vm_manager.py              # CLI principal
├── 📁 vm_organizer.py            # Organisation VMs
├── 🌐 ip_manager.py              # Gestion IPs
├── 📦 hypervisor_providers/      # Providers modulaires
│   ├── base_provider.py          # Interface commune
│   ├── vmware_provider.py        # Provider VMware
│   └── nutanix_provider.py       # Provider Nutanix
├── 🎨 frontend/                  # Interface web
│   ├── index.html                # Page principale
│   ├── script.js                 # Logique JS
│   └── style.css                 # Styles CSS
├── 🪟 *.ps1                      # Scripts PowerShell
├── 🧪 test_*.py                  # Tests système
├── 🎭 nutanix_mock_server.py     # Serveur simulation
├── ⚙️ hypervisor_config.json     # Configuration
├── 📖 DOCUMENTATION_TECHNIQUE.tex # Doc complète
└── 📋 README files               # Guides
```

---

## 🎯 **Cas d'Usage Typiques**

### 👤 **Utilisateur Final**
1. Ouvrir navigateur → `http://localhost:5000`
2. Se connecter/s'inscrire
3. Créer VM via interface graphique
4. Gérer VMs via dashboard

### 👨‍💻 **Administrateur Système**
1. Configurer `hypervisor_config.json`
2. Utiliser CLI : `python vm_manager.py --list`
3. Scripts PowerShell pour automatisation
4. Surveiller logs et statuts

### 🔧 **Développeur**
1. Lancer tests : `python test_multi_hypervisor.py`
2. Utiliser API REST pour intégrations
3. Étendre avec nouveaux providers
4. Modifier interface web

---

## 🔄 **Workflow Typique**

### ✨ **Création VM Standard**
```
1. Configuration → hypervisor_config.json
2. Démarrage → python app.py
3. Interface → http://localhost:5000
4. Création → Formulaire web ou CLI
5. Organisation → Automatique via vm_organizer
6. Gestion → Dashboard ou commandes
```

---

## 📚 **Ressources Utiles**

- **📖 Documentation complète** : `GUIDE_ARCHITECTURE_PROJET.md`
- **🔧 Configuration** : `hypervisor_config.json`
- **🧪 Tests** : `test_multi_hypervisor.py`
- **📋 API** : Endpoints dans `app.py`
- **🎨 Interface** : `frontend/index.html`

---

## 🎉 **Points Clés à Retenir**

1. **🎯 Un seul point d'entrée** : `app.py` pour web, `vm_manager.py` pour CLI
2. **🔌 Architecture modulaire** : Facile d'ajouter nouveaux hyperviseurs
3. **🧪 Tests intégrés** : Validation automatique du système
4. **📁 Organisation automatique** : VMs rangées proprement
5. **🌐 Multi-interface** : Web, CLI, PowerShell selon préférence
6. **🎭 Mock intégré** : Tests sans infrastructure réelle

**En résumé** : Auto-Creation-VM unifie la gestion de VMs sur différents hyperviseurs avec une interface moderne et des outils robustes ! 🚀