#!/bin/bash

# Configuration
PKG_NAME="tokenoptimizer"
VERSION="1.1.0"
BUILD_DIR="${PKG_NAME}_${VERSION}"

echo "🔨 Building .deb package for ${PKG_NAME} v${VERSION}..."

# 1. Cleanup and Structure
rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}/DEBIAN
mkdir -p ${BUILD_DIR}/usr/bin
mkdir -p ${BUILD_DIR}/usr/share/applications
mkdir -p ${BUILD_DIR}/usr/share/icons/hicolor/512x512/apps

# 2. Control File
cat <<EOT > ${BUILD_DIR}/DEBIAN/control
Package: ${PKG_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Depends: xdotool, xclip, python3-tk
Maintainer: Antigravity <antigravity@example.com>
Description: Desktop app for prompt optimization via Ollama.
 TokenOptimizer uses a symbolic pre-encoder and AI models to reduce 
 prompt length while maintaining core meaning.
EOT

# 3. Icon
cp assets/icon.png ${BUILD_DIR}/usr/share/icons/hicolor/512x512/apps/${PKG_NAME}.png

# 3. Binary
if [ ! -f "dist/TokenOptimizer" ]; then
    echo "❌ Error: Binary 'dist/TokenOptimizer' not found. Run compilation first."
    exit 1
fi
cp dist/TokenOptimizer ${BUILD_DIR}/usr/bin/${PKG_NAME}
chmod +x ${BUILD_DIR}/usr/bin/${PKG_NAME}

# 4. Desktop Entry
cat <<EOT > ${BUILD_DIR}/usr/share/applications/${PKG_NAME}.desktop
[Desktop Entry]
Name=TokenOptimizer
Exec=/usr/bin/${PKG_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Development;Utility;
Comment=AI Prompt Optimizer
Terminal=false
EOT

# 5. Build
dpkg-deb --build ${BUILD_DIR}

echo "✅ Done! Package created: ${BUILD_DIR}.deb"
