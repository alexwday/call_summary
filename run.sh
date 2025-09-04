#!/bin/bash

# Unified Chat+ Voice Application Launcher with SSL Support

echo "=================================================="
echo "   Starting Chat+ Voice Application"
echo "=================================================="
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check and configure SSL certificate
SSL_CERT_FILE="rbc-ca-bundle.cer"
if [ -f "$SSL_CERT_FILE" ]; then
    echo -e "${GREEN}✓ Found corporate SSL certificate: $SSL_CERT_FILE${NC}"
    
    # Export SSL environment variables for Python requests
    export REQUESTS_CA_BUNDLE="$(pwd)/$SSL_CERT_FILE"
    export SSL_CERT_FILE="$(pwd)/$SSL_CERT_FILE"
    export CURL_CA_BUNDLE="$(pwd)/$SSL_CERT_FILE"
    
    # For pip installations
    export PIP_CERT="$(pwd)/$SSL_CERT_FILE"
    
    # For urllib (used by some ML libraries)
    export SSL_CERT_DIR="$(pwd)"
    export SSL_VERIFY="true"
    
    echo -e "${BLUE}SSL verification enabled with corporate certificate${NC}"
else
    echo -e "${YELLOW}⚠ No SSL certificate found (rbc-ca-bundle.cer)${NC}"
    echo -e "${YELLOW}Running without SSL verification (development mode)${NC}"
    
    # Disable SSL verification for development
    export PYTHONWARNINGS="ignore:Unverified HTTPS request"
    export REQUESTS_CA_BUNDLE=""
    export SSL_VERIFY="false"
    
    # For HuggingFace downloads
    export HF_HUB_DISABLE_SSL_VERIFY="1"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    
    # Install with appropriate SSL settings
    if [ -f "$SSL_CERT_FILE" ]; then
        ./venv/bin/pip install -r requirements.txt --cert="$SSL_CERT_FILE"
    else
        ./venv/bin/pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
    fi
fi

# Display SSL status
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " SSL Configuration:"
if [ -f "$SSL_CERT_FILE" ]; then
    echo " • Mode: Corporate SSL Verification"
    echo " • Certificate: $SSL_CERT_FILE"
else
    echo " • Mode: Development (No SSL Verification)"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Start the unified server
echo "🚀 Starting unified server on port 5003..."
./venv/bin/python app.py