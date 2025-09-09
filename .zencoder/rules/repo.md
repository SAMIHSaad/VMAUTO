# Auto-Creation-VM — Inventaire du dépôt

Dernière mise à jour: 2025-09-02
Racine: c:\\Users\\saads\\OneDrive\\Documents\\Coding\\Auto-Creation-VM

## Résumé
- **But**: Création, clonage, organisation et gestion de VMs VMware (Windows/Ubuntu) via Web (Flask), CLI (Python) et PowerShell.
- **Points clés**:
  - Organisation des VM en structure pérenne avec métadonnées, scripts de backup/snapshot
  - Intégration VMware (vmrun), post-traitements et corrections de persistance VMX
  - Pool IP simple via `ips.txt`

## Dossiers
- frontend/: UI HTML/CSS/JS
- http/: cloud-init, Kickstart, Unattend
- ansible/: provisioning Ansible
- cloned-vms/: VMs clonées
- permanent_vms/: VMs finales permanentes
- output-*, output-clone, output-save/: sorties de build/clone
- save_Output/: exemple de structure organisée
- logs/: journalisation
- packer_cache/: cache Packer
- .zencoder/rules/: ce fichier

## Fichiers principaux
- app.py — Flask (API/UI/Auth)
- vm_manager.py — CLI (create/clone/organize/list/backup)
- vm_organizer.py — Organisation fichiers + scripts + metadata
- organize_existing_vm.py — Organisation VM existante
- audit_and_fix_vms.py — Audit/correctifs VMX + scripts power
- system_status.py — Diagnostic système
- setup_system.py — Préparation env.
- test_vm_creation.py — Tests intégration
- ip_manager.py — Gestion IP (ips.txt)
- vm_manager.ps1 — Interface PowerShell
- New-VMFromClone.ps1 — Clonage VMware
- register_vm.ps1 — Aide registration/ouverture VMware
- register_permanent_vm.ps1 — Copie/registration VM permanente
- test_vm_build.ps1, test-ubuntu-build.ps1 — Tests Packer/persistance
- copy_vm.bat, take_snapshot.bat — scripts batch
- DOCUMENTATION_TECHNIQUE.tex — Doc LaTeX consolidée

## Documentation
- VM_AUTOMATION_GUIDE.md — Guide complet (Web/CLI/PS)
- PERMANENT_VM_CREATION_GUIDE.md — Pipeline VM permanente
- PERSISTENCE_FIX_GUIDE.md — Correctifs persistance/cloud-init/Ansible
- SOLUTION_SUMMARY.md — Résumé correctifs
- UBUNTU_AUTOMATION_README.md — Spécifique Ubuntu

## Variables / Secrets
- app.py: JWT_SECRET_KEY et identifiants MySQL codés en dur (à externaliser)

## Manquants/à vérifier
- build.pkr.hcl absent (référencé par plusieurs scripts)

## Commandes rapides
- Démarrer web: `python app.py`
- Créer VM: `python vm_manager.py create "MyVM" --cpu 4 --ram 4096 --ssd 40 --os-type linux`
- Cloner VM: `python vm_manager.py clone "NewVM" --source-vmx "C:\\Path\\Template.vmx"`
- Organiser: `python vm_manager.py organize "ExistingVM"`
- Audit: `python audit_and_fix_vms.py`
- Liste: `python vm_manager.py list --detailed`
- Backup: `python vm_manager.py backup "MyVM"`