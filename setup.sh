#!/bin/bash

echo "🚀 Setting up TokenOptimizer for Linux..."

# Update and install system dependencies
echo "📦 Installing system dependencies (xdotool, xclip, python3-tk)..."
sudo apt update
sudo apt install -y xdotool xclip python3-tk

# Install python dependencies
echo "🐍 Installing Python libraries..."
pip install --break-system-packages customtkinter darkdetect ollama requests spacy pyautogui pyperclip pynput psutil

echo "✅ Setup complete! You can now run the app with 'python3 main.py' or use the compiled binary in 'dist/TokenOptimizer'."
