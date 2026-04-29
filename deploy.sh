#!/bin/bash

# QNN Deployment Script
# This script sets up and deploys the QNN application

set -e

echo "=================================="
echo "QNN Volatility Prediction"
echo "Deployment Script"
echo "=================================="
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found!${NC}"
    exit 1
fi
python_version=$(python3 --version)
echo -e "${GREEN}✓ Found: $python_version${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[2/5]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[3/5]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[4/5]${NC} Installing dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Verify model files
echo -e "${YELLOW}[5/5]${NC} Verifying model files..."
if [ ! -f "model/model_volatility.h5" ]; then
    echo -e "${RED}Model file not found: model/model_volatility.h5${NC}"
    exit 1
fi
if [ ! -f "model/scaler.pkl" ]; then
    echo -e "${RED}Scaler file not found: model/scaler.pkl${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Model files verified${NC}"
echo ""

# Create log directory
mkdir -p logs
echo -e "${GREEN}✓ Log directory created${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run tests: pytest"
echo "2. Start API: cd app/api && python flask_api.py"
echo "3. Test endpoint: curl http://localhost:5000/api/v1/health"
echo ""
