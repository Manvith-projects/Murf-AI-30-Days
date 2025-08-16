@echo off
REM 🚀 Voice AI Agent Setup Script for Windows
REM This script helps you get started with the Voice AI Agent project

echo 🎤 Setting up Voice AI Agent...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv flask_env

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call flask_env\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Copy environment template
if not exist .env (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your API keys
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Run: python app.py
echo 3. Open: http://127.0.0.1:5000
echo.
echo 📚 For detailed instructions, see README.md
pause
