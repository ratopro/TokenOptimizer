#!/bin/bash

export VERSION="1.1.1"
APP_NAME="TokenOptimizer"

echo "💎 Building AppImage for ${APP_NAME} v${VERSION}..."

# 1. Download tools if not present
if [ ! -f "linuxdeploy-x86_64.AppImage" ]; then
    echo "📥 Downloading linuxdeploy..."
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

# 2. Prepare AppDir
rm -rf AppDir
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications

# Copy binary
if [ ! -f "dist/TokenOptimizer" ]; then
    echo "❌ Error: Binary 'dist/TokenOptimizer' not found. Run compilation first."
    exit 1
fi
cp dist/TokenOptimizer AppDir/usr/bin/tokenoptimizer

# 3. Create Desktop Entry
cat <<EOT > AppDir/usr/share/applications/tokenoptimizer.desktop
[Desktop Entry]
Name=TokenOptimizer
Exec=tokenoptimizer
Icon=tokenoptimizer
Type=Application
Categories=Development;Utility;
EOT

# 4. Generate AppImage
echo "📦 Running linuxdeploy..."
cp assets/icon.png assets/tokenoptimizer.png
./linuxdeploy-x86_64.AppImage --appdir AppDir --icon-file assets/tokenoptimizer.png --output appimage
rm assets/tokenoptimizer.png

echo "✅ Done! AppImage created in current directory."
ls -lh *.AppImage
