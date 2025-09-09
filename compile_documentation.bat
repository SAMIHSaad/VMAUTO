@echo off
echo ========================================
echo Compilation Documentation Technique
echo ========================================
echo.

echo Compilation de la documentation technique...
echo.

REM Compilation principale
pdflatex -interaction=nonstopmode DOCUMENTATION_TECHNIQUE.tex

if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Echec de la premiere compilation
    echo Verifiez les packages LaTeX installes
    pause
    exit /b 1
)

echo.
echo Deuxieme compilation pour les references croisees...
pdflatex -interaction=nonstopmode DOCUMENTATION_TECHNIQUE.tex

if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Echec de la deuxieme compilation
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilation terminee avec succes !
echo ========================================
echo.
echo Fichier genere: DOCUMENTATION_TECHNIQUE.pdf
echo.

REM Nettoyage des fichiers temporaires
echo Nettoyage des fichiers temporaires...
del *.aux *.log *.toc *.out *.fls *.fdb_latexmk 2>nul

echo.
echo Ouverture du PDF...
start DOCUMENTATION_TECHNIQUE.pdf

pause