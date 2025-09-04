#!/bin/bash

# Chat+ Voice System Startup Script

echo "=================================================="
echo "   Chat+ Voice System - Starting All Servers"
echo "=================================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3.12 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Function to cleanup on exit
cleanup() {
    echo
    echo "Shutting down all servers..."
    pkill -P $$
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup INT TERM

# Start TTS Server
echo "🚀 Starting TTS Server (Kokoro) on port 5001..."
./venv/bin/python tts_server.py &
TTS_PID=$!
sleep 5

# Start STT Server
echo "🚀 Starting STT Server (Whisper) on port 5002..."
./venv/bin/python stt_server.py &
STT_PID=$!
sleep 5

# Start Main App
echo "🚀 Starting Main Application on port 5003..."
./venv/bin/python app.py &
APP_PID=$!
sleep 2

echo
echo "=================================================="
echo "✅ All servers started successfully!"
echo
echo "🌐 Access the application at:"
echo "   Regular chat: http://localhost:5003"
echo "   Voice chat:   http://localhost:5003?voice=true"
echo
echo "📝 Process IDs:"
echo "   Main app: $APP_PID"
echo "   TTS:      $TTS_PID"
echo "   STT:      $STT_PID"
echo
echo "Press Ctrl+C to stop all servers"
echo "=================================================="

# Wait for any process to exit
wait