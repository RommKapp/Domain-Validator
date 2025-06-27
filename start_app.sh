#!/bin/bash

echo "🚀 Starting Email Domain Validator..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed"
        echo "Please install Python from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Set environment variables for SQLite
export DATABASE_URL="sqlite:///./edv_database.db"
export REDIS_URL="redis://localhost:6379"

echo "📋 Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "🎯 EMAIL DOMAIN VALIDATOR"
echo "============================================================"
echo "🌐 Web Interface: http://localhost:8002"
echo "📚 API Docs: http://localhost:8002/docs"
echo "🛠️ Admin Panel: http://localhost:8002/admin"
echo "============================================================"
echo "💡 Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the application
$PYTHON_CMD start_app.py