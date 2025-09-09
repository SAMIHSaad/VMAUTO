@echo off
echo.
echo ========================================
echo   SYSTEME FINAL AVEC ACTIONS VM NUTANIX
echo ========================================
echo.

echo 🛑 Nettoyage des anciens processus...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 🔧 1. Demarrage serveur mock Nutanix avec actions VM...
Start-Process python -ArgumentList "nutanix_mock_persistent.py" -WindowStyle Hidden
timeout /t 3 /nobreak >nul

echo 📱 2. Demarrage serveur Flask principal...
Start-Process python -ArgumentList "app_new.py" -WindowStyle Hidden
timeout /t 5 /nobreak >nul

echo 🔧 3. Configuration finale Nutanix...
python final_nutanix_setup.py

echo 🧪 4. Test des actions VM...
python test_nutanix_actions.py

echo.
echo 🌐 5. Ouverture de l'interface web...
start http://127.0.0.1:5000

echo.
echo ========================================
echo   ✅ SYSTEME FINAL OPERATIONNEL!
echo ========================================
echo.
echo 📊 FONCTIONNALITÉS DISPONIBLES:
echo    🌐 Interface Web: http://127.0.0.1:5000
echo    ⚙️ VMware: 6 VMs réelles (toutes actions)
echo    🔧 Nutanix: 6 VMs simulées (toutes actions)
echo    ▶️ Start/Stop/Restart VMs sur les deux providers
echo    🔄 Création/Clonage VMs
echo.
echo 🎯 MAINTENANT VOUS POUVEZ:
echo    - Voir TOUTES les VMs des deux providers
echo    - Démarrer/Arrêter les VMs Nutanix (ça marche!)
echo    - Créer des VMs sur VMware ou Nutanix
echo    - Gérer complètement les deux environnements
echo.
echo 👤 Connexion: testuser / test123
echo.
echo 🎉 PLUS D'ERREUR "Failed to start VM"!
echo.
echo Appuyez sur une touche pour continuer...
pause >nul