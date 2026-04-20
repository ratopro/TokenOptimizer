@echo off
echo 🚀 Compiling TokenOptimizer for Windows...

:: Check if PyInstaller is installed
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ PyInstaller not found. Installing...
    pip install pyinstaller
)

:: Install dependencies
echo 🐍 Installing dependencies...
pip install customtkinter ollama pyautogui pyperclip pygetwindow darkdetect

:: Compile
echo 📦 Running PyInstaller...
pyinstaller TokenOptimizer_win.spec --noconfirm

echo ✅ Compilation complete! Check the 'dist' folder for TokenOptimizer.exe
pause
