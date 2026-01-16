#!/bin/bash

##############################################
# Script Setup SSL - AI Proposal Reviewer
# Usage: sudo ./setup-ssl.sh <domain>
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

# Cek parameter
if [ -z "$1" ]; then
    print_error "Usage: sudo ./setup-ssl.sh <domain>"
    print_error "Example: sudo ./setup-ssl.sh proposal-reviewer.southeastasia.cloudapp.azure.com"
    exit 1
fi

DOMAIN=$1

print_step "🔒 Setup SSL Certificate untuk ${DOMAIN}"

# Step 1: Install Certbot
print_info "Installing Certbot..."
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
    print_success "Certbot installed"
else
    print_info "Certbot already installed"
fi

# Step 2: Get Email
read -p "Masukkan email untuk Certbot: " certbot_email

if [ -z "$certbot_email" ]; then
    print_error "Email tidak boleh kosong"
    exit 1
fi

# Step 3: Get SSL Certificate
print_info "Mendapatkan SSL certificate..."
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${certbot_email}

print_success "SSL certificate installed!"

# Step 4: Test auto-renewal
print_info "Testing auto-renewal..."
certbot renew --dry-run

print_success "Auto-renewal configured!"

# Final Summary
print_step "✅ SSL Setup Selesai!"

echo -e "${GREEN}===================================================${NC}"
echo -e "${GREEN}SSL Certificate Summary${NC}"
echo -e "${GREEN}===================================================${NC}"
echo -e "Domain: ${DOMAIN}"
echo -e "Status: ${GREEN}Active${NC}"
echo -e ""
echo -e "Akses aplikasi di: ${GREEN}https://${DOMAIN}${NC}"
echo -e ""
echo -e "${GREEN}Certificate Commands:${NC}"
echo -e "  Cek certificate: ${YELLOW}sudo certbot certificates${NC}"
echo -e "  Renew manual: ${YELLOW}sudo certbot renew${NC}"
echo -e "  Revoke certificate: ${YELLOW}sudo certbot revoke --cert-name ${DOMAIN}${NC}"
echo -e "${GREEN}===================================================${NC}"
