@echo off
REM Market Prediction System v2.3.0 Startup Script for Windows

echo Starting Market Prediction System v2.3.0...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Please copy .env.example to .env and add your API keys.
    echo You can still run the system, but it will need API keys from environment variables.
)

REM Start the application
echo Starting Market Prediction System...
python market_predictor.py

pause
