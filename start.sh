#!/bin/bash

echo "==================================================="
echo "    Starting YourDaddy AI Assistant"
echo "==================================================="
echo ""

# Check for node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed. Please install Node.js."
    exit 1
fi

# Check for python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed or not in PATH."
    exit 1
fi

PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "[1/2] Starting Python Backend Server..."
if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
    # Git Bash on Windows
    start cmd /k "$PYTHON_CMD modern_web_backend.py"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && $PYTHON_CMD modern_web_backend.py\""
else
    # Linux
    x-terminal-emulator -e "$PYTHON_CMD modern_web_backend.py" &
fi

echo "[2/2] Starting React Frontend..."
cd src/project

if [ ! -d "node_modules" ]; then
    echo "Installing React dependencies..."
    npm install
fi

if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
    start cmd /k "npm run dev"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && npm run dev\""
else
    x-terminal-emulator -e "npm run dev" &
fi

echo ""
echo "==================================================="
echo "    SUCCESS! The Assistant is starting up."
echo "==================================================="
echo "Backend API will be available at: http://localhost:8000"
echo "Frontend UI will be available at: http://localhost:5173"
echo ""
echo "Two new terminal windows have opened. Keep them running!"
