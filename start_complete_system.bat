@echo off
echo.
echo ========================================
echo   SYSTEME VM MULTI-HYPERVISOR COMPLET
echo ========================================
echo.

echo 🚀 Demarrage des serveurs...

echo 📱 1. Demarrage serveur Flask...
start /B python app.py

echo 🔧 2. Demarrage serveur mock Nutanix...
start /B python nutanix_mock_final.py

echo ⏳ 3. Attente du demarrage (8 secondes)...
timeout /t 8 /nobreak >nul

echo 🔧 4. Configuration finale Nutanix...
python final_nutanix_setup.py

echo.
echo 🌐 5. Ouverture de l'interface web...
start http://127.0.0.1:5000

echo.
echo ========================================
echo   ✅ SYSTEME COMPLET PRET!
echo ========================================
echo.
echo 📊 PROVIDERS DISPONIBLES:
echo    ⚙️ VMware: 6 VMs reelles
echo    🔧 Nutanix: 6 VMs simulees
echo.
echo 🌐 INTERFACE WEB: http://127.0.0.1:5000
echo 👤 Utilisateur: testuser
echo 🔐 Mot de passe: test123
echo.
echo 💻 COMMANDES CLI:
echo    python vm_manager_new.py status
echo    python vm_manager_new.py --provider vmware list
echo    python vm_manager_new.py --provider nutanix list
echo.
echo 🎯 VOUS POUVEZ MAINTENANT:
echo    - Voir les VMs des DEUX providers
echo    - Creer des VMs sur VMware OU Nutanix
echo    - Gerer les VMs des deux cotes
echo.
echo Appuyez sur une touche pour continuer...
pause >nul