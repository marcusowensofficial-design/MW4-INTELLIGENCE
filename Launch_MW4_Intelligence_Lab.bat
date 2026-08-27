@echo off
title MW4 Weapon Intelligence Lab - Launcher
color 0B
cls

echo ===============================================================================
echo         __  ____          _____     _   _ _____ _____ _     _      _    ____  
echo        / / / / /   /\    / ____^|   ^| \ ^| ^|_   _/ ____^| ^|   ^| ^|    / \  ^|  _ \ 
echo       / / / / /   /  \  ^| ^|  __   ^|  \^| ^| ^| ^|^| (___ ^| ^|   ^| ^|   / _ \ ^| ^|_) ^|
echo      / / / / /   / /\ \ ^| ^| ^|_ ^|  ^| . ` ^| ^| ^| \___ \^| ^|   ^| ^|  / ___ \^|  _ ^< 
echo     / / / / /   / ____ \^| ^|__^| ^|  ^| ^|\  ^|_^| ^|_^|____) ^| ^|___^| ^|_/ /   \ \ ^|_) ^|
echo    /_/_/_/_/   /_/    \_\\_____^|  ^|_^| \_^|_____^|_____/^|______^|___/_/     \_^|____/ 
echo ===============================================================================
echo            EVIDENCE-BACKED MODERN WARFARE 4 FPS WEAPON INTELLIGENCE LAB        
echo ===============================================================================
echo.

:: 1. Check Python Availability
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Python was not found in your system PATH.
    echo Please ensure Python 3.10+ is installed and checked in Windows PATH.
    echo.
    pause
    exit /b 1
)

echo [*] Python environment detected:
python --version
echo.

:: 2. Check Database & Auto-Seed if Missing
if not exist "data\mw4_intelligence.duckdb" (
    echo [*] DuckDB database not found. Initializing and seeding baseline intelligence...
    python -c "from src.database.connection import db_manager; db_manager.init_database(); from src.database.seed_data import seed_database; seed_database(); print('[*] Seed complete.')"
    echo.
)

:: 3. Launch Streamlit Application
echo [*] Launching MW4 Weapon Intelligence Lab Command Center...
echo [*] Local URL: http://localhost:8501
echo.
echo Press Ctrl+C in this terminal window to stop the server when finished.
echo ===============================================================================
echo.

python -m streamlit run app.py --server.port=8501 --server.headless=false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server process terminated unexpectedly.
    pause
)
