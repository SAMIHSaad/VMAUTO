# Guide d'Utilisation : Auto-Creation-VM

## 1. Introduction

Bienvenue sur Auto-Creation-VM ! 

Ce guide est votre point de départ pour maîtriser notre plateforme de gestion de machines virtuelles (VMs). L'objectif d'Auto-Creation-VM est simple : vous permettre de créer, gérer et automatiser vos VMs sur nos différentes infrastructures (VMware et Nutanix) à partir d'une interface unique, simple et puissante.

Que vous soyez développeur, testeur ou administrateur système, ce guide vous montrera comment gagner un temps précieux et vous concentrer sur vos tâches les plus importantes.

---

## 2. Démarrage Rapide : Créez votre première VM en 5 minutes

Suivez ces quelques étapes pour voir la magie opérer.

### Étape 1 : Lancez l'application

Le système est conçu pour être simple. Il vous suffit de lancer le script de démarrage principal :
```bash
# Ouvrez un terminal et exécutez :
python app.py
```
Cela démarre le serveur web et l'API. Vous devriez voir des informations de démarrage dans la console.

### Étape 2 : Accédez à l'interface web

Ouvrez votre navigateur web préféré et rendez-vous à l'adresse suivante :
[http://localhost:5000](http://localhost:5000)

### Étape 3 : Créez un compte et connectez-vous

- Sur la page d'accueil, cliquez sur **"S'inscrire"**.
- Remplissez le formulaire avec votre nom d'utilisateur, email et mot de passe, puis validez.
- Vous serez redirigé vers la page de connexion. Entrez vos nouveaux identifiants pour accéder au tableau de bord.

### Étape 4 : Créez votre Machine Virtuelle

- Une fois connecté, naviguez vers l'onglet **"Créer VM"**.
- Le formulaire de création apparaît. Remplissez les champs :
  - **Nom de la VM** : Donnez un nom simple et descriptif (ex: `mon-serveur-dev`).
  - **Provider** : Choisissez l'hyperviseur sur lequel créer la VM (ex: `vmware`).
  - **Template** : Sélectionnez un modèle de base pour votre VM (ex: `ubuntu-template`).
  - **Mémoire / CPU** : Ajustez les ressources selon vos besoins.
- Cliquez sur le bouton **"Créer la VM"**.

### Étape 5 : Admirez le résultat !

La création peut prendre quelques minutes. Une fois terminée, votre nouvelle machine virtuelle apparaîtra automatiquement sur le **Tableau de Bord** principal. Vous y verrez son statut (en cours d'exécution) et les actions rapides disponibles.

**Félicitations !** Vous venez de déployer votre première VM avec Auto-Creation-VM.

---

## 3. Explorer l'Interface Web

L'interface web est conçue pour être intuitive. Voici ses sections principales.

### Le Tableau de Bord

C'est votre page d'accueil. Elle vous donne une vue d'ensemble de toutes vos machines virtuelles, quel que soit l'hyperviseur. Pour chaque VM, vous pouvez :
- **Voir son statut** (Allumée, Éteinte, etc.).
- **Démarrer, Arrêter ou Redémarrer** la VM en un clic.
- **Supprimer** une VM dont vous n'avez plus besoin.

### La Création de VM

L'onglet **"Créer VM"** vous permet de provisionner de nouvelles machines. Les options disponibles (templates, réseaux, etc.) sont chargées dynamiquement en fonction du "provider" (VMware ou Nutanix) que vous choisissez, vous garantissant de ne voir que les configurations valides.

### Les Paramètres

L'onglet **"Paramètres"** vous permet de voir le statut de connexion aux différents hyperviseurs. Un indicateur vert vous confirme que le système est prêt à recevoir vos demandes.

---

## 4. Pour les Experts : La Ligne de Commande (CLI)

Pour ceux qui préfèrent le terminal, le script `vm_manager.py` offre toute la puissance de la plateforme.

- **Lister toutes les VMs** :
  ```bash
  python vm_manager.py --list
  ```

- **Créer une nouvelle VM** :
  ```bash
  python vm_manager.py --create --name "vm-depuis-cli" --template "ubuntu-template" --provider vmware
  ```

- **Démarrer ou arrêter une VM** :
  ```bash
  python vm_manager.py --start --name "vm-depuis-cli"
  python vm_manager.py --stop --name "vm-depuis-cli"
  ```

- **Obtenir de l'aide** :
  ```bash
  python vm_manager.py --help
  ```

---

## 5. Pour les Utilisateurs Windows : Scripts PowerShell

Nous fournissons également des scripts PowerShell pour une intégration parfaite dans un environnement Windows.

- **Cloner rapidement une VM VMware** :
  ```powershell
  .\New-VMFromClone.ps1 -TemplateName "ubuntu-template" -NewVMName "ma-vm-clonee"
  ```

- **Créer une VM sur Nutanix** :
  ```powershell
  .\New-NutanixVM.ps1 -VMName "mon-serveur-nutanix" -ClusterName "cluster-prod"
  ```

Ces scripts sont des raccourcis pratiques pour les tâches les plus courantes.

---

## 6. Exemples de Scénarios (Workflows)

Voici comment Auto-Creation-VM peut accélérer votre travail au quotidien.

### Scénario 1 : Isoler un bug dans un environnement propre

Vous devez tester un bug sur une version spécifique d'une application. Au lieu de polluer votre machine, vous pouvez créer une VM dédiée en 2 minutes.

1.  Allez sur **"Créer VM"**.
2.  Nommez-la `test-bug-123`.
3.  Choisissez le template `windows-10-dev`.
4.  Cliquez sur **Créer**.
5.  Une fois la VM prête, connectez-vous, reproduisez le bug, puis supprimez la VM depuis le tableau de bord. Votre système reste propre.

### Scénario 2 : Déployer un environnement de développement complet

Vous démarrez un nouveau projet qui nécessite un serveur web et une base de données.

1.  Créez une première VM `mon-projet-frontend` à partir d'un template `ubuntu-web`.
2.  Créez une seconde VM `mon-projet-db` à partir d'un template `ubuntu-database`.
3.  En quelques minutes, votre architecture de base est prête à être configurée, sans aucune installation manuelle d'OS.

---

## 7. Conclusion

Ce guide vous a montré les bases pour bien démarrer avec Auto-Creation-VM. La force de cet outil est sa capacité à standardiser et accélérer des tâches qui étaient auparavant complexes et longues.

N'hésitez pas à explorer les différentes options. Bonne création de VMs !
