#!/bin/bash
# ============================================
# Script Deploy AI Proposal Reviewer
# ============================================
# Jalankan script ini SETELAH login SSH ke VM:
# chmod +x deploy.sh && ./deploy.sh

set -e

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Proposal Reviewer - Deploy Script  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Variables
APP_DIR="/opt/proposal-reviewer"
LOG_DIR="/var/log/proposal-reviewer"
CURRENT_DIR=$(pwd)

# [1] Create directories
echo -e "${YELLOW}[1/7] Membuat direktori...${NC}"
sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo chown -R $USER:$USER $APP_DIR
sudo chown -R $USER:$USER $LOG_DIR
echo -e "${GREEN}✓ Direktori berhasil dibuat${NC}"

# [2] Copy application files
echo -e "${YELLOW}[2/7] Menyalin file aplikasi ke $APP_DIR...${NC}"
if [ -d "$CURRENT_DIR/app" ]; then
    cp -r $CURRENT_DIR/app $APP_DIR/
    cp -r $CURRENT_DIR/pengujian $APP_DIR/ 2>/dev/null || true
    cp -r $CURRENT_DIR/deploy $APP_DIR/
    cp $CURRENT_DIR/requirements.txt $APP_DIR/
    cp $CURRENT_DIR/.env.example $APP_DIR/
    [ -f "$CURRENT_DIR/.env" ] && cp $CURRENT_DIR/.env $APP_DIR/
    echo -e "${GREEN}✓ File aplikasi berhasil disalin${NC}"
else
    echo -e "${RED}Error: Folder 'app' tidak ditemukan.${NC}"
    echo -e "${RED}Pastikan menjalankan script dari root folder project.${NC}"
    exit 1
fi

# [3] Setup Python virtual environment
echo -e "${YELLOW}[3/7] Setup Python virtual environment...${NC}"
cd $APP_DIR
python3.11 -m venv venv 2>/dev/null || python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q
echo -e "${GREEN}✓ Virtual environment berhasil dibuat${NC}"

# [4] Setup .env file
echo -e "${YELLOW}[4/7] Mengecek konfigurasi .env...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env
    echo -e "${YELLOW}⚠ File .env dibuat dari .env.example${NC}"
    echo -e "${YELLOW}  API key Groq sudah tersedia di file tersebut.${NC}"
else
    echo -e "${GREEN}✓ File .env sudah ada${NC}"
fi

# [5] Setup systemd service
echo -e "${YELLOW}[5/7] Setup systemd service...${NC}"
sudo cp $APP_DIR/deploy/proposal-reviewer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable proposal-reviewer
sudo systemctl restart proposal-reviewer
echo -e "${GREEN}✓ Systemd service berhasil disetup${NC}"

# [6] Setup Nginx
echo -e "${YELLOW}[6/7] Setup Nginx reverse proxy...${NC}"
sudo cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/proposal-reviewer
sudo ln -sf /etc/nginx/sites-available/proposal-reviewer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

if sudo nginx -t 2>/dev/null; then
    sudo systemctl restart nginx
    echo -e "${GREEN}✓ Nginx berhasil dikonfigurasi${NC}"
else
    echo -e "${RED}✗ Konfigurasi Nginx error, cek nginx.conf${NC}"
fi

# [7] Verify deployment
echo -e "${YELLOW}[7/7] Verifikasi deployment...${NC}"
sleep 3

if systemctl is-active --quiet proposal-reviewer; then
    echo -e "${GREEN}✓ Service proposal-reviewer berjalan${NC}"
else
    echo -e "${RED}✗ Service gagal start. Cek log:${NC}"
    echo -e "  sudo journalctl -u proposal-reviewer -n 20"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx berjalan${NC}"
else
    echo -e "${RED}✗ Nginx gagal start${NC}"
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "<IP_ANDA>")

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ✅ Deployment Selesai!                ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "🌐 Akses aplikasi: ${GREEN}http://$PUBLIC_IP${NC}"
echo -e "🔍 Health check:   ${GREEN}http://$PUBLIC_IP/api/kesehatan${NC}"
echo ""
echo -e "${YELLOW}Langkah selanjutnya:${NC}"
echo -e "1. Setup SSL: sudo certbot --nginx -d YOUR_DOMAIN"
echo -e "2. Cek logs:  sudo journalctl -u proposal-reviewer -f"
echo ""
