# 🚀 Guide d'Installation Nutanix Community Edition

## 📋 Prérequis

### Hardware Minimum
- **CPU** : 4 cores (8 recommandés)
- **RAM** : 32 GB (64 GB recommandés) 
- **Stockage** : 200 GB SSD
- **Réseau** : 1 Gbps

### Software
- VMware Workstation Pro
- ISO Nutanix CE (téléchargé depuis le site officiel)

## 🔧 Installation Étape par Étape

### 1. Télécharger Nutanix CE
```
🌐 Site : https://www.nutanix.com/products/community-edition
📧 Inscription gratuite requise
📦 Télécharger l'ISO (4-6 GB)
```

### 2. Créer la VM
```powershell
# Utiliser notre script automatique
.\create_nutanix_vm.ps1 -ISOPath "C:\Path\To\nutanix-ce.iso"
```

### 3. Démarrer l'Installation
1. **Démarrer la VM** dans VMware
2. **Booter sur l'ISO** Nutanix CE
3. **Suivre l'assistant** d'installation

### 4. Configuration Réseau
```
🌐 Type : NAT ou Bridged
📍 IP : Automatique (DHCP) ou statique
🔌 Port : 9440 (HTTPS)
```

### 5. Configuration Initiale
```
👤 Username : admin
🔐 Password : nutanix/4u (par défaut)
🌐 Interface : https://[IP-VM]:9440
```

## 🎯 Configuration Post-Installation

### 1. Accès Web Interface
```
🌐 URL : https://192.168.x.x:9440
👤 Login : admin
🔐 Password : nutanix/4u
```

### 2. Configuration Cluster
1. **Créer un cluster** (single node pour CE)
2. **Configurer le stockage**
3. **Créer des réseaux virtuels**

### 3. Préparer pour notre Système
```json
{
  "prism_central_ip": "192.168.x.x",
  "username": "admin", 
  "password": "nutanix/4u",
  "port": 9440
}
```

## 🔍 Vérification Installation

### Test de Connectivité
```bash
# Test ping
ping 192.168.x.x

# Test port HTTPS
telnet 192.168.x.x 9440
```

### Test API
```bash
curl -k -X POST https://192.168.x.x:9440/api/nutanix/v3/clusters/list \
  -H "Content-Type: application/json" \
  -u admin:nutanix/4u \
  -d '{}'
```

## 🎉 Intégration avec notre Système

### 1. Configuration dans l'Interface Web
```
🌐 Ouvrir : http://localhost:5000
⚙️ Aller : Settings > Nutanix Configuration
✅ Activer : Enable Nutanix Provider
📝 Entrer :
   - Prism Central IP: 192.168.x.x
   - Username: admin
   - Password: nutanix/4u
   - Port: 9440
```

### 2. Test de Fonctionnement
```bash
# Tester la configuration
python test_nutanix_config.py

# Lister les VMs Nutanix
python vm_manager_new.py list --provider nutanix
```

## 🚨 Dépannage

### Problèmes Courants

#### VM ne démarre pas
```
❌ Problème : Pas assez de RAM
✅ Solution : Augmenter RAM à 32GB minimum
```

#### Pas d'accès réseau
```
❌ Problème : Configuration réseau VMware
✅ Solution : Vérifier NAT/Bridged dans VMware
```

#### Interface web inaccessible
```
❌ Problème : Port 9440 bloqué
✅ Solution : Vérifier firewall et configuration réseau
```

### Logs Utiles
```bash
# Dans la VM Nutanix
tail -f /home/nutanix/data/logs/genesis.out
tail -f /home/nutanix/data/logs/prism_gateway.log
```

## 📚 Ressources

- **Documentation** : https://portal.nutanix.com/
- **Community** : https://next.nutanix.com/
- **Support CE** : Forums communautaires
- **APIs** : https://www.nutanix.dev/

## 🎯 Résultat Final

Après installation, vous aurez :
- ✅ Cluster Nutanix CE fonctionnel
- ✅ Interface Prism accessible
- ✅ APIs REST disponibles
- ✅ Intégration avec notre système multi-hypervisor
- ✅ Capacité de créer/gérer des VMs Nutanix

**Temps d'installation estimé : 2-3 heures**