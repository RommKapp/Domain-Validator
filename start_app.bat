@echo off
echo 🚀 Starting Email Domain Validator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Set environment variables for SQLite
set DATABASE_URL=sqlite:///./edv_database.db
set REDIS_URL=redis://localhost:6379

echo 📋 Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🎯 EMAIL DOMAIN VALIDATOR
echo ============================================================
echo 🌐 Web Interface: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🛠️ Admin Panel: http://localhost:8000/admin
echo ============================================================
echo 💡 Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the application
python start_app.py

pause