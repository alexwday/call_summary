#!/bin/bash

# Unified Chat+ Voice Application Launcher

echo "=================================================="
echo "   Starting Chat+ Voice Application"
echo "=================================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Start the unified server
echo "🚀 Starting unified server on port 5003..."
./venv/bin/python app.py