@echo off
echo ======================================================================
echo 🚀 Starting AI Chat API Server on Port 7000
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if in correct directory (should be in Bookies_Website root)
if not exist "LLM_AWS\main.py" (
    echo ❌ Error: Please run this script from Bookies_Website root directory
    echo Current directory: %CD%
    echo Expected: D:\Bookies_Website (or your project root)
    echo.
    echo Usage: 
    echo   cd D:\Bookies_Website
    echo   LLM_AWS\start_server.bat
    pause
    exit /b 1
)

echo 📦 Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencies not installed
    echo Installing dependencies...
    pip install -r LLM_AWS\requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Dependencies OK
echo.
echo 🚀 Starting server...
echo.
echo 📍 Server will be available at:
echo    - http://localhost:7000
echo    - Swagger UI: http://localhost:7000/docs
echo    - ReDoc: http://localhost:7000/redoc
echo.
echo 💡 Press Ctrl+C to stop the server
echo.
echo ======================================================================
echo.

python LLM_AWS\run_server.py

pause
