@echo off
echo.
echo ========================================
echo   DEMARRAGE RAPIDE - SYSTEME VM
echo ========================================
echo.

echo 🚀 Demarrage du serveur web...
start /B python app.py

echo ⏳ Attente du demarrage (5 secondes)...
timeout /t 5 /nobreak >nul

echo 🌐 Ouverture de l'interface web...
start http://127.0.0.1:5000

echo.
echo ✅ SYSTEME PRET!
echo.
echo 📋 Informations d'acces:
echo    URL: http://127.0.0.1:5000
echo    Utilisateur: testuser
echo    Mot de passe: test123
echo.
echo 🔧 Commandes utiles:
echo    python vm_manager_new.py status
echo    python nutanix_simulator.py
echo.
echo Appuyez sur une touche pour continuer...
pause >nul