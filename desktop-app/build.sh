#!/bin/bash
# Build script for 90dayChonThanh Desktop App
# Tự động build installer cho tất cả platforms

set -e  # Exit on error

echo "🚀 Starting build process for 90dayChonThanh..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Node.js
echo "📋 Checking requirements..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

# Check Yarn
if ! command -v yarn &> /dev/null; then
    echo -e "${RED}❌ Yarn not found. Installing...${NC}"
    npm install -g yarn
fi
echo -e "${GREEN}✅ Yarn: $(yarn --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}⚠️  Python3 not found. Users will need to install Python.${NC}"
else
    echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"
fi

echo ""
echo "📦 Installing dependencies..."
yarn install

echo ""
echo "🏗️  Building React app..."
yarn build

echo ""
echo "📊 Current package.json version:"
VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}Version: $VERSION${NC}"

echo ""
echo "🎯 Select build target:"
echo "1) Current platform only (fast)"
echo "2) Windows"
echo "3) macOS"
echo "4) Linux"
echo "5) All platforms (slow)"
echo "6) Portable version (no installer)"
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "🔨 Building for current platform..."
        yarn electron-build
        ;;
    2)
        echo ""
        echo "🪟 Building for Windows..."
        yarn electron-build --win
        ;;
    3)
        echo ""
        echo "🍎 Building for macOS..."
        yarn electron-build --mac
        ;;
    4)
        echo ""
        echo "🐧 Building for Linux..."
        yarn electron-build --linux
        ;;
    5)
        echo ""
        echo "🌍 Building for all platforms..."
        yarn electron-build --win --mac --linux
        ;;
    6)
        echo ""
        echo "📁 Building portable version..."
        yarn electron-pack
        echo ""
        echo "Creating ZIP archive..."
        cd dist
        if [ -d "win-unpacked" ]; then
            zip -r "90dayChonThanh-Portable-Win-$VERSION.zip" win-unpacked/
            echo -e "${GREEN}✅ Created: 90dayChonThanh-Portable-Win-$VERSION.zip${NC}"
        fi
        if [ -d "mac" ]; then
            zip -r "90dayChonThanh-Portable-Mac-$VERSION.zip" mac/
            echo -e "${GREEN}✅ Created: 90dayChonThanh-Portable-Mac-$VERSION.zip${NC}"
        fi
        if [ -d "linux-unpacked" ]; then
            zip -r "90dayChonThanh-Portable-Linux-$VERSION.zip" linux-unpacked/
            echo -e "${GREEN}✅ Created: 90dayChonThanh-Portable-Linux-$VERSION.zip${NC}"
        fi
        cd ..
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "✨ Build complete!"
echo ""
echo "📁 Output files are in: ./dist/"
ls -lh dist/ | grep -E '\.(exe|dmg|AppImage|zip)$' || echo "No installer files found"

echo ""
echo "📝 Next steps:"
echo "1. Test the installer on a clean machine"
echo "2. Verify Tesseract OCR integration works"
echo "3. Upload to distribution channel (GitHub Releases, Drive, etc.)"
echo ""
echo -e "${GREEN}🎉 Done!${NC}"
