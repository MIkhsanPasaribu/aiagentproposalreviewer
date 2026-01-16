#!/bin/bash

##############################################
# Quick Fix untuk Error "No module named 'langchain_community'"
# Usage: sudo ./quickfix.sh
##############################################

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_NAME="proposal-reviewer"
APP_DIR="/opt/${APP_NAME}"

echo -e "${YELLOW}🔧 Quick Fix: Installing Missing Dependencies${NC}\n"

# 1. Stop service
echo -e "${YELLOW}[1/4]${NC} Stopping service..."
systemctl stop ${APP_NAME}

# 2. Activate venv and install dependencies
echo -e "${YELLOW}[2/4]${NC} Installing pypdf..."
cd ${APP_DIR}
source venv/bin/activate
pip install pypdf --quiet

# 3. Pull latest code (jika ada perubahan)
echo -e "${YELLOW}[3/4]${NC} Checking for updates..."
git pull

# 4. Restart service
echo -e "${YELLOW}[4/4]${NC} Restarting service..."
systemctl start ${APP_NAME}

sleep 3

# Check status
if systemctl is-active --quiet ${APP_NAME}; then
    echo -e "\n${GREEN}✅ Service running successfully!${NC}\n"
    
    # Test endpoint
    echo -e "${YELLOW}Testing endpoint...${NC}"
    response=$(curl -s http://localhost:8000/api/kesehatan)
    
    if [[ $response == *"sehat"* ]]; then
        echo -e "${GREEN}✅ API responding correctly!${NC}\n"
        echo "Response: $response"
    else
        echo -e "${RED}❌ API not responding correctly${NC}"
    fi
else
    echo -e "\n${RED}❌ Service failed to start!${NC}\n"
    echo "Check logs: sudo journalctl -u ${APP_NAME} -n 50"
fi
