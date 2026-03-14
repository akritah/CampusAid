@echo off
REM CampusAid Quick Setup Script for Windows
REM This script sets up both backend and frontend

echo ==================================
echo   CampusAid Setup Script
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8+ first.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

echo √ Python version:
python --version
echo √ Node.js version:
node --version
echo.

REM Backend Setup
echo ==================================
echo   Setting up Backend
echo ==================================
echo.

cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Train ML model
echo Training ML model...
python train_classifier.py

echo √ Backend setup complete!
echo.

cd ..

REM Frontend Setup
echo ==================================
echo   Setting up Frontend
echo ==================================
echo.

cd frontend\campusaid

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

echo √ Frontend setup complete!
echo.

cd ..\..

REM Final instructions
echo ==================================
echo   Setup Complete!
echo ==================================
echo.
echo To start the application:
echo.
echo 1. Start Backend (Terminal 1):
echo    cd backend
echo    .venv\Scripts\activate
echo    python app\main.py
echo.
echo 2. Start Frontend (Terminal 2):
echo    cd frontend\campusaid
echo    npm run dev
echo.
echo 3. Open browser:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Demo Users:
echo   student1 / student123
echo   worker1 / worker123
echo   admin1 / admin123
echo   warden1 / warden123
echo.
echo ==================================

pause
