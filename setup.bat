@echo off
echo ========================================
echo JIRA Ticket Generator - Setup Script
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo [2/4] Checking .env file...
if not exist .env (
    echo .env file not found. Creating from .env.example...
    copy .env.example .env
    echo.
    echo ========================================
    echo IMPORTANT: Please edit backend\.env and add your Google API Key!
    echo Get your API key from: https://makersuite.google.com/app/apikey
    echo ========================================
    echo.
    pause
)
cd ..

echo [3/4] Setting up Frontend...
cd frontend
echo Installing Node.js dependencies...
call npm install
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo 1. Run 'start-backend.bat' in one terminal
echo 2. Run 'start-frontend.bat' in another terminal
echo 3. Open http://localhost:5173 in your browser
echo.
pause
