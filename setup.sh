#!/bin/bash

# Setup script for Call Summary project with Python 3.12
# This script ensures Python 3.12 is used and sets up the virtual environment

set -e  # Exit on error

echo "=================================================="
echo "Call Summary Project Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare version numbers
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Step 1: Check for Python 3.12
echo -e "\n${YELLOW}Step 1: Checking Python installation...${NC}"

# Try to find Python 3.12 specifically
if command_exists python3.12; then
    PYTHON_CMD="python3.12"
elif command_exists python3; then
    # Check if python3 is version 3.12
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$PYTHON_VERSION" = "3.12" ]; then
        PYTHON_CMD="python3"
    else
        echo -e "${RED}Error: Python 3.12 is required but found Python $PYTHON_VERSION${NC}"
        echo "Please install Python 3.12 first:"
        echo "  - macOS: brew install python@3.12"
        echo "  - Ubuntu/Debian: sudo apt install python3.12 python3.12-venv"
        echo "  - Or download from: https://www.python.org/downloads/"
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.12 first"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Step 2: Check for venv module
echo -e "\n${YELLOW}Step 2: Checking venv module...${NC}"
if ! $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
    echo -e "${RED}Error: venv module not found${NC}"
    echo "Please install python3.12-venv:"
    echo "  - Ubuntu/Debian: sudo apt install python3.12-venv"
    echo "  - macOS: venv should be included with Python"
    exit 1
fi
echo -e "${GREEN}✓ venv module available${NC}"

# Step 3: Create virtual environment
echo -e "\n${YELLOW}Step 3: Setting up virtual environment...${NC}"

# Remove existing venv if it exists and is not Python 3.12
if [ -d "venv" ]; then
    if [ -f "venv/bin/python" ]; then
        VENV_PYTHON_VERSION=$(venv/bin/python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$VENV_PYTHON_VERSION" != "3.12" ]; then
            echo "Existing venv uses Python $VENV_PYTHON_VERSION. Removing and recreating with Python 3.12..."
            rm -rf venv
        else
            echo "Existing venv already uses Python 3.12"
        fi
    else
        echo "Invalid venv detected. Removing..."
        rm -rf venv
    fi
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists with Python 3.12${NC}"
fi

# Step 4: Activate virtual environment and install dependencies
echo -e "\n${YELLOW}Step 4: Installing dependencies...${NC}"

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip >/dev/null 2>&1

# Add PyPI as an additional trusted source alongside any existing artifactory
echo "Adding PyPI as additional package source..."

# Install requirements with PyPI as extra index
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    echo "Using both your artifactory and PyPI as package sources..."
    
    # First, ensure pip, setuptools, and wheel are up to date
    pip install --upgrade pip setuptools wheel --quiet
    
    # Install with PyPI as extra index url and trusted host
    # Use --no-deps first for problematic packages, then resolve deps
    echo "Installing packages (this may take a few minutes)..."
    
    # Try installation with proper index configuration
    pip install -r requirements.txt \
        --extra-index-url https://pypi.org/simple \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        --no-cache-dir \
        2>&1 | tee install.log
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
        rm -f install.log
    else
        echo -e "${YELLOW}⚠ Some packages may have failed to install${NC}"
        echo "Checking for common issues..."
        
        # Check for mistral_common issue
        if grep -q "mistral.*audio" install.log; then
            echo -e "${YELLOW}Note: mistral_common[audio] dependency issue detected${NC}"
            echo "This is expected and won't affect functionality."
            echo "The required audio packages are installed separately."
        fi
        
        echo ""
        echo "You can try installing missing packages individually:"
        echo "  pip install <package-name> --index-url https://pypi.org/simple"
        echo ""
        echo "Or with PyPI as primary:"
        echo "  pip install -r requirements.txt --index-url https://pypi.org/simple"
    fi
else
    echo -e "${RED}Warning: requirements.txt not found${NC}"
fi

# Step 5: Create .env file if it doesn't exist
echo -e "\n${YELLOW}Step 5: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here

# Optional: Custom API endpoint (leave blank for default OpenAI)
# OPENAI_API_BASE=

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Flask configuration
SECRET_KEY=your-secret-key-here
EOF
    echo -e "${GREEN}✓ Created .env file - Please add your API keys${NC}"
    echo -e "${YELLOW}  Edit .env and add your OpenAI API key${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Step 6: Create necessary directories
echo -e "\n${YELLOW}Step 6: Creating necessary directories...${NC}"
mkdir -p uploads
mkdir -p data
echo -e "${GREEN}✓ Directories created${NC}"

# Step 7: Display final instructions
echo -e "\n${GREEN}=================================================="
echo "Setup Complete!"
echo "==================================================${NC}"
echo ""
echo "Python version: $PYTHON_VERSION"
echo "Virtual environment: ./venv"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the application:"
echo "   python app.py"
echo "   OR"
echo "   ./start.sh"
echo ""
echo "The app will be available at:"
echo "  - Regular chat: http://localhost:5003"
echo "  - Voice chat: http://localhost:5003?voice=true"
echo ""