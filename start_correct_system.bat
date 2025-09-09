@echo off
echo.
echo ========================================
echo   SYSTEME VM AVEC NUTANIX VISIBLE
echo ========================================
echo.

echo 🛑 Arret des anciens serveurs...
taskkill /f /im python.exe >nul 2>&1

echo ⏳ Attente (3 secondes)...
timeout /t 3 /nobreak >nul

echo 🚀 Demarrage des serveurs corrects...

echo 📱 1. Demarrage serveur Flask NOUVEAU...
start /B python app_new.py

echo 🔧 2. Demarrage serveur mock Nutanix...
start /B python nutanix_mock_final.py

echo ⏳ 3. Attente du demarrage (8 secondes)...
timeout /t 8 /nobreak >nul

echo 🔧 4. Configuration finale Nutanix...
python final_nutanix_setup.py

echo.
echo 🌐 5. Ouverture de l'interface web NOUVELLE...
start http://127.0.0.1:5000

echo.
echo ========================================
echo   ✅ SYSTEME CORRECT PRET!
echo ========================================
echo.
echo 📊 MAINTENANT VOUS VERREZ:
echo    ⚙️ VMware: 6 VMs reelles
echo    🔧 Nutanix: 6 VMs simulees (VISIBLES!)
echo.
echo 🌐 INTERFACE WEB NOUVELLE: http://127.0.0.1:5000
echo 👤 Utilisateur: testuser
echo 🔐 Mot de passe: test123
echo.
echo 🎯 DANS L'INTERFACE VOUS POUVEZ:
echo    - Voir les VMs des DEUX providers
echo    - Creer des VMs sur Nutanix (plus de "Not Implemented")
echo    - Gerer toutes les VMs
echo.
echo Appuyez sur une touche pour continuer...
pause >nul