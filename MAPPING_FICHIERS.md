# 🗂️ Mapping Complet des Fichiers - Auto-Creation-VM

## 📋 **Index des Fichiers par Catégorie**

### 🌟 **FICHIERS PRINCIPAUX (À CONNAÎTRE ABSOLUMENT)**

| **Fichier** | **Rôle** | **Utilisation** | **Importance** |
|-------------|----------|-----------------|----------------|
| `app.py` | 🌐 **Application web Flask** | `python app.py` → Interface web | ⭐⭐⭐⭐⭐ |
| `vm_manager.py` | 🖥️ **CLI principal** | `python vm_manager.py --list` | ⭐⭐⭐⭐⭐ |
| `hypervisor_manager.py` | 🎯 **Orchestrateur central** | Utilisé par autres composants | ⭐⭐⭐⭐⭐ |
| `hypervisor_config.json` | ⚙️ **Configuration système** | Éditer pour configurer | ⭐⭐⭐⭐⭐ |

---

## 📁 **STRUCTURE DÉTAILLÉE PAR DOSSIER**

### 🏠 **RACINE DU PROJET**

#### 🌐 **Applications Principales**
```
app.py                          # 🌐 Serveur web Flask + API REST
├─ Authentification JWT         # 🔐 Login/Register sécurisé
├─ Base MySQL                   # 🗄️ Gestion utilisateurs
├─ API REST (14+ endpoints)     # 🔌 Interface programmable
├─ Mock Nutanix intégré         # 🎭 Simulation automatique
└─ Logging avancé               # 📊 flask_app.log
```

```
vm_manager.py                   # 🖥️ Interface ligne de commande
├─ Support multi-hyperviseur    # 🔌 VMware + Nutanix
├─ Création/Clonage VMs         # ✨ Opérations principales
├─ Organisation automatique     # 📁 Structure pérenne
├─ Gestion cycle de vie         # ⚡ Start/Stop/Restart
└─ Intégration avec organizer   # 🔄 Workflow complet
```

#### 🎯 **Gestionnaires Core**
```
hypervisor_manager.py           # 🎯 Orchestrateur central
├─ Chargement configuration     # ⚙️ hypervisor_config.json
├─ Initialisation providers     # 🔌 VMware + Nutanix
├─ Interface unifiée            # 🎚️ API commune
├─ Sélection automatique        # ⚡ Provider par défaut
└─ Gestion d'erreurs            # 🛡️ Validation + fallback
```

```
vm_organizer.py                 # 📁 Organisation automatique
├─ Structure standardisée       # 🏗️ permanent_vms/date_nom/
├─ Génération métadonnées       # 📄 metadata.json
├─ Scripts automatiques         # 📜 backup/snapshot.bat
├─ Documentation VM             # 📚 README.md généré
└─ Persistance données          # 🔒 Évite perte VMs
```

```
ip_manager.py                   # 🌐 Gestionnaire IP
├─ Pool d'adresses              # 🎯 Plage configurable
├─ Système de verrous           # 🔒 Évite conflits
├─ Allocation automatique       # ⚡ IP libre assignée
├─ Libération automatique       # 🔄 Retour au pool
└─ Suivi utilisation            # 📊 Historique
```

---

### 📦 **DOSSIER hypervisor_providers/**

```
hypervisor_providers/
├─ __init__.py                  # 📦 Initialisation module
├─ base_provider.py             # 🏗️ Interface commune abstraite
│  ├─ BaseHypervisorProvider    # 🎯 Classe abstraite
│  ├─ VMConfig dataclass        # 📋 Structure config VM
│  ├─ VMInfo dataclass          # 📊 Structure info VM
│  └─ Méthodes abstraites       # ✅ create_vm, list_vms, etc.
├─ vmware_provider.py           # 🖥️ Provider VMware Workstation
│  ├─ Utilise vmrun.exe         # 🛠️ Commandes VMware natives
│  ├─ Découverte templates      # 📁 Scan automatique
│  ├─ Clonage VMware            # 🔄 Via vmrun clone
│  ├─ Contrôle VMs              # ⚡ Start/Stop/Reset
│  └─ Gestion VMX               # 📝 Lecture/écriture config
└─ nutanix_provider.py          # ☁️ Provider Nutanix AHV
   ├─ API REST v3               # 🌐 Prism Central
   ├─ Gestion clusters          # 🏢 Liste et sélection
   ├─ Gestion réseaux           # 🔗 Configuration auto
   ├─ Opérations VMs            # 🖥️ CRUD complet
   └─ Authentification          # 🔐 Basic Auth
```

---

### 🎨 **DOSSIER frontend/**

```
frontend/
├─ index.html                   # 🏠 Page principale
│  ├─ Dashboard VMs             # 📊 Vue d'ensemble temps réel
│  ├─ Formulaire création       # ✨ Multi-hyperviseur
│  ├─ Liste VMs                 # 📋 Avec contrôles
│  ├─ Paramètres système        # ⚙️ Configuration providers
│  └─ Navigation onglets        # 🔄 Interface fluide
├─ login.html                   # 🔐 Page connexion
├─ register.html                # 👤 Page inscription
├─ clear-cookies.html           # 🧹 Nettoyage session
├─ script.js                    # ⚡ Logique JavaScript
│  ├─ Appels API REST           # 🔌 Communication backend
│  ├─ Gestion formulaires       # 📝 Validation + soumission
│  ├─ Mise à jour dynamique     # 🔄 Rafraîchissement temps réel
│  ├─ Contrôles VM              # 🎛️ Start/Stop/Restart
│  └─ Affichage données         # 📊 Tableaux dynamiques
├─ style.css                    # 🎨 Styles principaux
├─ login.css                    # 🔐 Styles connexion
├─ register.css                 # 👤 Styles inscription
└─ ACAPS.jpg                    # 🖼️ Logo organisation
```

---

### 🪟 **SCRIPTS POWERSHELL**

#### 🎯 **Scripts Principaux**
```
vm_manager.ps1                  # 🪟 Interface PowerShell → vm_manager.py
├─ Paramètres PowerShell        # 🔧 -Action, -Name, -Provider
├─ Appel Python natif           # 🐍 Exécution vm_manager.py
└─ Gestion erreurs Windows      # 🛡️ Codes retour PowerShell
```

```
New-VMFromClone.ps1             # 🔄 Clonage VMware avancé
├─ Clone depuis template        # 📁 Template local
├─ Ajustement ressources        # ⚙️ RAM, CPU, disque
├─ Configuration réseau         # 🌐 IP automatique
└─ Démarrage automatique        # ▶️ VM prête à l'emploi
```

```
New-NutanixVM.ps1               # ☁️ Création VM Nutanix
├─ Interface PowerShell         # 🪟 Paramètres natifs
├─ Appel API Nutanix            # 🌐 REST v3
├─ Configuration cluster        # 🏢 Sélection automatique
└─ Gestion réseau               # 🔗 VLAN et IP
```

```
nutanix_manager.ps1             # 🎛️ Gestionnaire Nutanix complet
├─ Création VMs                 # ✨ Avec paramètres détaillés
├─ Listing ressources           # 📋 VMs, clusters, réseaux
├─ Contrôle VMs                 # ⚡ Start/Stop/Restart
└─ Monitoring                   # 📊 Statut et métriques
```

#### 🔧 **Scripts Utilitaires**
```
register_vm.ps1                 # 📝 Registration VMware
register_permanent_vm.ps1       # 📁 Copie vers permanent_vms/
create_nutanix_vm.ps1          # ☁️ Création Nutanix détaillée
install_nutanix_ce.ps1         # 🛠️ Installation Nutanix CE
fix_vmware_vnc.ps1             # 🔧 Correctif VNC VMware
monitor_vm_creation.ps1        # 👀 Surveillance création
```

---

### 🧪 **FICHIERS DE TEST**

#### 🔬 **Tests Principaux**
```
test_multi_hypervisor.py        # 🧪 Suite tests complète
├─ Tests configuration          # ⚙️ Validation config files
├─ Tests providers              # 🔌 Connectivité hyperviseurs
├─ Tests opérations VM          # 🖥️ Création, listing, contrôle
├─ Tests API REST               # 🌐 Validation endpoints
└─ Tests intégration            # 🔄 Workflow bout en bout
```

```
test_vm_creation.py             # ⚡ Tests création VMs
├─ Validation structure         # 📁 Organisation fichiers
├─ Tests dépendances            # 🔧 Outils requis
├─ Validation configuration     # ⚙️ Paramètres corrects
└─ Tests persistance            # 💾 Sauvegarde données
```

#### 🎯 **Tests Spécialisés**
```
test_nutanix_config.py          # ☁️ Tests config Nutanix
test_nutanix_actions.py         # 🎛️ Tests actions Nutanix
test_post_api.py                # 📤 Tests endpoints POST
test_user_display.py            # 👤 Tests interface utilisateur
demo_multi_hypervisor.py        # 🎭 Démonstration complète
final_test.py                   # ✅ Validation finale système
```

#### 🪟 **Tests PowerShell**
```
test_vm_build.ps1               # 🔨 Tests build Packer
test-ubuntu-build.ps1           # 🐧 Build Ubuntu rapide
test_post_*.ps1                 # 📤 Tests API POST PowerShell
test_simple_creation.ps1        # ⚡ Test création simple
test_vm_creation_location.ps1   # 📍 Test localisation création
```

---

### 🎭 **SERVEURS MOCK ET SIMULATION**

```
nutanix_mock_server.py          # 🎭 Serveur mock principal
├─ API REST v3 complète         # 🌐 Simulation Prism Central
├─ Données réalistes            # 📊 Clusters, VMs, réseaux
├─ Persistance données          # 💾 Maintien entre redémarrages
├─ Tests sans infrastructure    # 🧪 Développement sans Nutanix
└─ Démarrage automatique        # ⚡ Port 9441
```

#### 🎪 **Variantes Mock**
```
nutanix_mock_final.py           # 🏁 Version finale complète
nutanix_mock_persistent.py      # 💾 Avec persistance avancée
simple_nutanix_mock.py          # ⚡ Version simplifiée
start_mock_server.py            # 🚀 Script démarrage
simulate_nutanix_vms.py         # 🖥️ Simulation VMs
nutanix_simulator.py            # 🎭 Simulateur environnement
```

---

### ⚙️ **CONFIGURATION ET DONNÉES**

```
hypervisor_config.json          # ⚙️ Configuration principale
├─ Section VMware               # 🖥️ Chemins vmrun, templates
├─ Section Nutanix              # ☁️ IP, credentials, cluster
├─ Paramètres globaux           # 🌐 Répertoires, options
└─ Configuration réseau         # 🔗 Pools IP, VLANs
```

```
requirements.txt                # 📦 Dépendances Python
├─ Flask + extensions           # 🌐 Framework web
├─ Authentification             # 🔐 JWT, bcrypt
├─ Base de données              # 🗄️ MySQL
├─ Communication réseau         # 🌐 requests, urllib3
└─ Tests                        # 🧪 pytest
```

---

### 📖 **DOCUMENTATION**

```
DOCUMENTATION_TECHNIQUE.tex     # 📖 Documentation LaTeX complète
├─ Architecture détaillée       # 🏗️ Diagrammes + explications
├─ Guide installation           # 🛠️ Étapes complètes
├─ Guides utilisation           # 🎯 Web, CLI, PowerShell
├─ Référence API                # 📋 Documentation endpoints
├─ Dépannage                    # 🔧 Solutions problèmes
└─ Design professionnel         # 🎨 Thème bleu cohérent
```

```
compile_documentation.bat       # 🔨 Compilation LaTeX → PDF
├─ Double compilation           # 🔄 Références croisées
├─ Nettoyage automatique        # 🧹 Fichiers temporaires
├─ Ouverture PDF                # 📄 Affichage résultat
└─ Gestion erreurs              # 🛡️ Messages explicites
```

#### 📚 **Guides Utilisateur**
```
README_PRINCIPAL.md             # 🏠 Guide principal du projet
GUIDE_ARCHITECTURE_PROJET.md   # 🏗️ Architecture détaillée
REFERENCE_RAPIDE.md             # ⚡ Démarrage 30 secondes
README_DOCUMENTATION.md         # 📖 Guide documentation
MAPPING_FICHIERS.md             # 🗂️ Ce fichier !
```

---

## 🎯 **POINTS D'ENTRÉE PAR USAGE**

### 👤 **Utilisateur Final**
1. **Démarrer** : `python app.py`
2. **Interface** : `http://localhost:5000`
3. **Documentation** : `README_PRINCIPAL.md`

### 👨‍💻 **Administrateur Système**
1. **Configuration** : `hypervisor_config.json`
2. **CLI** : `python vm_manager.py`
3. **PowerShell** : `vm_manager.ps1`
4. **Guide** : `REFERENCE_RAPIDE.md`

### 🔧 **Développeur**
1. **Architecture** : `GUIDE_ARCHITECTURE_PROJET.md`
2. **Tests** : `test_multi_hypervisor.py`
3. **API** : `app.py` (endpoints)
4. **Extension** : `hypervisor_providers/`

### 📖 **Documentation**
1. **Compilation** : `compile_documentation.bat`
2. **Source** : `DOCUMENTATION_TECHNIQUE.tex`
3. **Guide** : `README_DOCUMENTATION.md`

---

## 🔄 **FLUX DE DONNÉES TYPIQUE**

```
1. Configuration → hypervisor_config.json
2. Démarrage → app.py ou vm_manager.py
3. Orchestration → hypervisor_manager.py
4. Providers → vmware_provider.py / nutanix_provider.py
5. Organisation → vm_organizer.py
6. Réseau → ip_manager.py
7. Interface → frontend/ ou CLI
8. Tests → test_multi_hypervisor.py
```

---

## 📊 **STATISTIQUES FICHIERS**

| **Catégorie** | **Nombre** | **Lignes Code** | **Importance** |
|---------------|------------|-----------------|----------------|
| 🌐 **Applications** | 5 | ~1500 | ⭐⭐⭐⭐⭐ |
| 🔌 **Providers** | 3 | ~800 | ⭐⭐⭐⭐⭐ |
| 🎨 **Frontend** | 8 | ~1000 | ⭐⭐⭐⭐ |
| 🪟 **PowerShell** | 15+ | ~2000 | ⭐⭐⭐ |
| 🧪 **Tests** | 20+ | ~1500 | ⭐⭐⭐⭐ |
| 🎭 **Mock** | 6 | ~600 | ⭐⭐⭐ |
| 📖 **Documentation** | 6 | ~500 | ⭐⭐⭐⭐ |

---

## 🎉 **RÉSUMÉ POUR DÉBUTANTS**

**Auto-Creation-VM** c'est comme une **boîte à outils complète** :

- **🏠 Une maison** (`app.py`) avec interface web
- **🧠 Un cerveau** (`hypervisor_manager.py`) qui coordonne tout
- **🔧 Des outils** (`vm_manager.py`) pour ligne de commande
- **🔌 Des adaptateurs** (`providers/`) pour parler aux hyperviseurs
- **📁 Un rangement** (`vm_organizer.py`) pour organiser
- **🧪 Un laboratoire** (`test_*.py`) pour vérifier que tout marche
- **📖 Un manuel** (documentation) pour tout expliquer

**Chaque fichier a un rôle précis** dans cet écosystème unifié ! 🚀