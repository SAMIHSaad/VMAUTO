@echo off
echo 🚀 Demarrage serveur mock Nutanix persistant...

REM Tuer les anciens processus Python sur le port 9441
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :9441') do taskkill /f /pid %%a >nul 2>&1

REM Démarrer le serveur mock en arrière-plan
start /B /MIN python nutanix_mock_persistent.py

REM Attendre que le serveur démarre
timeout /t 3 /nobreak >nul

REM Tester si le serveur répond
python -c "import requests; r=requests.get('http://127.0.0.1:9441/status'); print('✅ Serveur mock Nutanix démarré:', r.json()['server'])" 2>nul

if %errorlevel% equ 0 (
    echo ✅ Serveur mock Nutanix opérationnel sur le port 9441
) else (
    echo ❌ Problème avec le serveur mock
)

echo 🎯 Le serveur mock reste actif en arrière-plan
echo 📊 URL de test: http://127.0.0.1:9441/status