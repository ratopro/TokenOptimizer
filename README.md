# 🚀 TokenOptimizer

**TokenOptimizer** is a professional-grade desktop application designed to optimize and compress AI prompts using local models via **Ollama**. It features a high-density UI, symbolic pre-encoding, dynamic multi-language support, and seamless integration with other applications.

<p align="center">
  <img src="assets/icon.png" width="128" alt="TokenOptimizer Icon">
</p>

## ✨ Key Features

- **🎯 4 Optimization Modes**:
  - **Light**: Refines clarity and grammar while maintaining original length.
  - **Optimized**: The perfect balance between compression and intent (recommended).
  - **Aggressive**: Maximum token savings using compact, Telegram-style phrasing.
  - **Symbolic**: Replaces common logical operators with mathematical symbols (`&`, `->`, `∀`, `∃`).
- **🌐 Global Localization (i18n)**: 
  - Entire application UI translates instantly between **English, Spanish, French, German, Italian, and Portuguese**.
- **🔄 Intelligent Translation**:
  - **Toggle OFF**: Output matches the current UI language.
  - **Toggle ON**: Output is always translated to **English** (ideal for English-optimized LLMs).
- **🔗 Auto-Send Integration**: Automatically focuses and injects optimized prompts into external windows (Browsers, IDEs, Discord, etc.).
- **📜 Smart History**: Persistent history window with search functionality and chronological navigation via `Ctrl + Up/Down`.
- **⚡ Real-time Diagnostics**: Live token counters and compression percentage tracking with high-contrast visual feedback.
- **🔄 Auto-Updates**: Seamless version checking against GitHub releases with a built-in Changelog viewer.
- **🌍 Cross-Platform**: Native look and feel on Linux, Windows, and macOS.

## 🛠️ Installation & Setup

### 🐧 Linux (Recommended)
Use the automated setup script to install system dependencies (`xdotool`, `xclip`, `python3-tk`) and Python requirements:
```bash
chmod +x setup.sh && ./setup.sh
```

### 🪟 Windows / 🍎 macOS
1. Install [Ollama](https://ollama.com/).
2. Ensure Python 3.10+ is installed.
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📦 Build & Distribution

TokenOptimizer includes specialized scripts to generate production-ready binaries:

### 🐧 Linux
- **Debian Package**: `./build_deb.sh` (Generates a `.deb` with automatic dependency management).
- **AppImage**: `./build_appimage.sh` (Generates a portable binary that works on any distribution).
- **Standalone**: `pyinstaller TokenOptimizer.spec`

### 🪟 Windows
Run `compile_windows.bat` on a Windows machine to generate a portable `.exe`.

### 🍎 macOS
Run `./compile_mac.sh` on a Mac to generate a `.app` bundle.

## ⌨️ Controls & Shortcuts

| Action | Shortcut |
|--------|----------|
| **Optimize** | `Enter` (in prompt field) |
| **New Line** | `Ctrl + Enter` |
| **History Prev/Next** | `Ctrl + Up` / `Ctrl + Down` |
| **Zoom In/Out** | `Ctrl + "+"` / `Ctrl + "-"` |
| **Update Check** | Click version label (bottom-right) |
| **Stay on Top** | Toggle 📌 button |

## 📋 Technical Requirements

- **Ollama**: Must be running locally (`ollama serve`).
- **Python 3.10+**: For source execution.
- **System Utilities (Linux)**: `xdotool` and `xclip` are required for the "Inject" and "Copy" features.

## 📄 License

This project is licensed under the MIT License.

---
*Developed with ❤️ for the AI community by Antigravity.*