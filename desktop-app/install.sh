#!/bin/bash

# Desktop App Installation Script
# Automates the setup process for the Land Document Scanner Desktop App

set -e  # Exit on error

echo "======================================"
echo "  Desktop App Installation Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"

# Check Yarn
echo "Checking Yarn..."
if ! command -v yarn &> /dev/null; then
    echo -e "${YELLOW}⚠️  Yarn not found. Installing...${NC}"
    npm install -g yarn
fi
YARN_VERSION=$(yarn --version)
echo -e "${GREEN}✅ Yarn $YARN_VERSION${NC}"

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found${NC}"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi
PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

# Check pip
echo "Checking pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip not found${NC}"
    echo "Please install pip for Python"
    exit 1
fi
PIP_VERSION=$($PYTHON_CMD -m pip --version)
echo -e "${GREEN}✅ $PIP_VERSION${NC}"

echo ""
echo "======================================"
echo "  Installing Dependencies"
echo "======================================"
echo ""

# Navigate to desktop-app directory
cd "$(dirname "$0")"

# Install JavaScript dependencies
echo -e "${YELLOW}📦 Installing JavaScript dependencies...${NC}"
yarn install
echo -e "${GREEN}✅ JavaScript dependencies installed${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
echo "   (This may take 5-10 minutes for PaddleOCR)"
cd python
$PYTHON_CMD -m pip install -r requirements.txt
cd ..
echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo ""

echo "======================================"
echo "  ✅ Installation Complete!"
echo "======================================"
echo ""
echo "🚀 To run the app in development mode:"
echo "   cd $(pwd)"
echo "   yarn electron-dev"
echo ""
echo "📦 To build for production:"
echo "   yarn build"
echo "   yarn electron-build"
echo ""
echo "📖 For more info, see:"
echo "   - README.md"
echo "   - QUICK_START_VI.md"
echo ""
