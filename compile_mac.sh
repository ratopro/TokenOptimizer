#!/bin/bash

echo "🍎 Compiling TokenOptimizer for macOS..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Install dependencies
echo "🐍 Installing dependencies..."
pip install customtkinter ollama pyautogui pyperclip pyobjc darkdetect

# Compile
echo "📦 Running PyInstaller..."
pyinstaller TokenOptimizer_mac.spec --noconfirm

echo "✅ Compilation complete! Check the 'dist' folder for TokenOptimizer.app"
