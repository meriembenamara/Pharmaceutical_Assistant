@echo off
echo ========================================
echo   PHARMA ASSISTANT - LANCEUR WINDOWS
echo ========================================

REM Vérifier l'environnement virtuel
if not exist "venv\Scripts\activate.bat" (
    echo  Environnement virtuel non trouvé
    echo    Création de l'environnement...
    python -m venv venv
)

REM Activer l'environnement
call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
echo Vérification des dépendances...
pip install -r requirements.txt 2>nul || (
    echo Installation des dépendances...
    pip install fastapi uvicorn openai chromadb sentence-transformers requests
)

REM Tester OpenAI
echo Test OpenAI...
python app/test_openai.py
if errorlevel 1 (
    echo  OpenAI test échoué
    pause
    exit /b 1
)

REM Lancer l'application
echo    Lancement de l'API...
echo    Accédez à: http://localhost:8000
echo    Documentation: http://localhost:8000/docs
echo    Ctrl+C pour arrêter
echo ========================================

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000