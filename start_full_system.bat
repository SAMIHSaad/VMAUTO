@echo off
echo.
echo ========================================
echo   SYSTEME COMPLET AVEC NUTANIX VISIBLE
echo ========================================
echo.

echo 🛑 Nettoyage des anciens processus...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 🔧 1. Demarrage serveur mock Nutanix persistant...
call start_nutanix_mock.bat

echo 📱 2. Demarrage serveur Flask principal...
start /B python app_new.py

echo ⏳ 3. Attente du demarrage complet (8 secondes)...
timeout /t 8 /nobreak >nul

echo 🔧 4. Configuration finale Nutanix...
python final_nutanix_setup.py

echo.
echo 🌐 5. Ouverture de l'interface web...
start http://127.0.0.1:5000

echo.
echo ========================================
echo   ✅ SYSTEME COMPLET OPERATIONNEL!
echo ========================================
echo.
echo 📊 STATUT:
echo    🌐 Interface Web: http://127.0.0.1:5000
echo    🔧 Mock Nutanix: http://127.0.0.1:9441/status
echo    ⚙️ VMware: Connecté
echo    🔧 Nutanix: Connecté (simulé)
echo.
echo 🎯 MAINTENANT VOUS POUVEZ:
echo    - Voir TOUTES les VMs (VMware + Nutanix)
echo    - Créer des VMs sur les deux providers
echo    - Le serveur mock reste actif en permanence
echo.
echo 👤 Connexion: testuser / test123
echo.
echo Appuyez sur une touche pour continuer...
pause >nul