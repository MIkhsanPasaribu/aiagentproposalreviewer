#!/bin/bash
# ============================================
# Script Deploy AI Proposal Reviewer
# ============================================
# Jalankan: chmod +x deploy.sh && ./deploy.sh

set -e

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI Proposal Reviewer - Deploy Script  ${NC}"
echo -e "${GREEN}========================================${NC}"

# Variables
APP_DIR="/opt/proposal-reviewer"
LOG_DIR="/var/log/proposal-reviewer"
USER="azureuser"

# Create directories
echo -e "${YELLOW}[1/7] Creating directories...${NC}"
sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R $USER:$USER $LOG_DIR

# Copy application files
echo -e "${YELLOW}[2/7] Copying application files...${NC}"
if [ -d "./app" ]; then
    cp -r ./app $APP_DIR/
    cp -r ./pengujian $APP_DIR/ 2>/dev/null || true
    cp requirements.txt $APP_DIR/
    cp .env.example $APP_DIR/
    [ -f .env ] && cp .env $APP_DIR/
else
    echo -e "${RED}Error: ./app directory not found. Run from project root.${NC}"
    exit 1
fi

# Setup virtual environment
echo -e "${YELLOW}[3/7] Setting up Python virtual environment...${NC}"
cd $APP_DIR
python3.11 -m venv venv || python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Check .env file
echo -e "${YELLOW}[4/7] Checking .env configuration...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from example...${NC}"
    cp $APP_DIR/.env.example $APP_DIR/.env
    echo -e "${RED}Please edit $APP_DIR/.env with your Azure OpenAI credentials${NC}"
fi

# Setup systemd service
echo -e "${YELLOW}[5/7] Setting up systemd service...${NC}"
sudo cp deploy/proposal-reviewer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable proposal-reviewer
sudo systemctl restart proposal-reviewer

# Setup Nginx
echo -e "${YELLOW}[6/7] Setting up Nginx...${NC}"
sudo cp deploy/nginx.conf /etc/nginx/sites-available/proposal-reviewer
sudo ln -sf /etc/nginx/sites-available/proposal-reviewer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Verify deployment
echo -e "${YELLOW}[7/7] Verifying deployment...${NC}"
sleep 3

if systemctl is-active --quiet proposal-reviewer; then
    echo -e "${GREEN}✓ Application service is running${NC}"
else
    echo -e "${RED}✗ Application service failed to start${NC}"
    sudo journalctl -u proposal-reviewer -n 20
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!                  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Application URL: http://$PUBLIC_IP"
echo -e "Health Check: http://$PUBLIC_IP/api/kesehatan"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit .env file: nano $APP_DIR/.env"
echo -e "2. Restart service: sudo systemctl restart proposal-reviewer"
echo -e "3. Setup SSL: sudo certbot --nginx -d YOUR_DOMAIN"
echo ""
