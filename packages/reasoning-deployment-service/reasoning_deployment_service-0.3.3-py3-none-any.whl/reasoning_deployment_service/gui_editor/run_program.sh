#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

# Detect Python executable
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ Python is not installed. Please install Python 3.9+."
    exit 1
fi

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate venv (POSIX)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
# Activate venv (Windows Git Bash or Cygwin)
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo "❌ Could not find venv activation script."
    exit 1
fi

# Install Tkinter if on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🖼  Installing Tkinter for Linux..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update && sudo apt-get install -y python3-tk
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-tkinter
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm tk
    else
        echo "⚠️ Could not determine package manager. Install python3-tk manually."
    fi
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --upgrade pip
# Install the reasoning deployment service with GUI extras
pip3 install "reasoning-deployment-service[gui]"

# Run your app
echo "🚀 Starting app..."
$PYTHON main.py
