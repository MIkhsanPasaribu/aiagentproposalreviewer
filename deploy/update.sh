#!/bin/bash

##############################################
# Script Update Aplikasi - AI Proposal Reviewer
# Usage: sudo ./update.sh
##############################################

set -e  # Exit on error

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Konfigurasi
APP_NAME="proposal-reviewer"
APP_DIR="/opt/${APP_NAME}"
APP_USER="viona"

# Fungsi helper
print_step() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Cek apakah script dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then 
    print_error "Script ini harus dijalankan sebagai root (gunakan sudo)"
    exit 1
fi

# Cek apakah aplikasi sudah terinstall
if [ ! -d "$APP_DIR" ]; then
    print_error "Aplikasi belum terinstall. Jalankan deploy.sh terlebih dahulu."
    exit 1
fi

print_step "🔄 Update AI Proposal Reviewer"

# Step 1: Stop service
print_info "Menghentikan aplikasi..."
systemctl stop ${APP_NAME}
print_success "Aplikasi dihentikan"

# Step 2: Backup .env
print_info "Backup file .env..."
sudo -u ${APP_USER} cp ${APP_DIR}/.env ${APP_DIR}/.env.backup
print_success "File .env di-backup"

# Step 3: Pull latest code
print_step "Mengambil kode terbaru dari repository..."
cd ${APP_DIR}
sudo -u ${APP_USER} git fetch --all
sudo -u ${APP_USER} git reset --hard origin/main
sudo -u ${APP_USER} git pull origin main
print_success "Kode terbaru berhasil diambil"

# Step 4: Restore .env
print_info "Restore file .env..."
sudo -u ${APP_USER} cp ${APP_DIR}/.env.backup ${APP_DIR}/.env
print_success "File .env di-restore"

# Step 5: Update dependencies
print_info "Update dependencies..."
sudo -u ${APP_USER} bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
print_success "Dependencies updated"

# Step 6: Reload systemd jika ada perubahan
if [ -f "deploy/proposal-reviewer.service" ]; then
    print_info "Update systemd service..."
    cp deploy/proposal-reviewer.service /etc/systemd/system/
    systemctl daemon-reload
    print_success "Systemd service updated"
fi

# Step 7: Reload nginx jika ada perubahan
if [ -f "deploy/nginx.conf" ]; then
    print_info "Checking nginx config..."
    nginx -t && systemctl reload nginx
    print_success "Nginx reloaded"
fi

# Step 8: Start service
print_info "Menjalankan aplikasi..."
systemctl start ${APP_NAME}
sleep 3

# Check status
if systemctl is-active --quiet ${APP_NAME}; then
    print_success "Aplikasi berhasil dijalankan!"
else
    print_error "Aplikasi gagal dijalankan. Check logs:"
    echo "sudo journalctl -u ${APP_NAME} -n 50"
    exit 1
fi

# Final Summary
print_step "✅ Update Selesai!"

echo -e "${GREEN}===================================================${NC}"
echo -e "${GREEN}Update Summary${NC}"
echo -e "${GREEN}===================================================${NC}"
echo -e "Status: ${GREEN}Running${NC}"
echo -e "Cek status: ${YELLOW}sudo systemctl status ${APP_NAME}${NC}"
echo -e "Lihat logs: ${YELLOW}sudo journalctl -u ${APP_NAME} -f${NC}"
echo -e "${GREEN}===================================================${NC}"
