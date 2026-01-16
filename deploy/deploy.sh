#!/bin/bash

##############################################
# Script Deploy Otomatis - AI Proposal Reviewer
# Usage: ./deploy.sh
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
PYTHON_VERSION="python3.11"
REPO_URL="https://github.com/MIkhsanPasaribu/aiagentproposalreviewer.git"

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

# Step 1: Update System
print_step "Step 1: Update System"
apt update && apt upgrade -y
print_success "System updated"

# Step 2: Install Dependencies
print_step "Step 2: Install Dependencies"

# Install Python 3.11
if ! command -v python3.11 &> /dev/null; then
    print_info "Installing Python 3.11..."
    add-apt-repository ppa:deadsnakes/ppa -y
    apt install python3.11 python3.11-venv python3.11-dev -y
    print_success "Python 3.11 installed"
else
    print_info "Python 3.11 already installed"
fi

# Install pip
if ! command -v pip3 &> /dev/null; then
    print_info "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
    print_success "Pip installed"
else
    print_info "Pip already installed"
fi

# Install Nginx
if ! command -v nginx &> /dev/null; then
    print_info "Installing Nginx..."
    apt install nginx -y
    print_success "Nginx installed"
else
    print_info "Nginx already installed"
fi

# Install Git
if ! command -v git &> /dev/null; then
    print_info "Installing Git..."
    apt install git -y
    print_success "Git installed"
else
    print_info "Git already installed"
fi

# Step 3: Setup Application Directory
print_step "Step 3: Setup Application Directory"

if [ ! -d "$APP_DIR" ]; then
    print_info "Creating app directory..."
    mkdir -p "$APP_DIR"
    chown ${APP_USER}:${APP_USER} "$APP_DIR"
    print_success "App directory created"
else
    print_info "App directory already exists"
fi

# Create log directory
if [ ! -d "/var/log/${APP_NAME}" ]; then
    print_info "Creating log directory..."
    mkdir -p "/var/log/${APP_NAME}"
    chown ${APP_USER}:${APP_USER} "/var/log/${APP_NAME}"
    print_success "Log directory created"
else
    print_info "Log directory already exists"
fi

# Step 4: Clone Repository
print_step "Step 4: Clone Repository"

cd "$APP_DIR"
if [ ! -d ".git" ]; then
    print_info "Cloning repository..."
    sudo -u ${APP_USER} git clone "$REPO_URL" .
    print_success "Repository cloned"
else
    print_info "Repository already exists, pulling latest changes..."
    sudo -u ${APP_USER} git pull
    print_success "Repository updated"
fi

# Step 5: Setup Python Environment
print_step "Step 5: Setup Python Virtual Environment"

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    sudo -u ${APP_USER} ${PYTHON_VERSION} -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Install dependencies
print_info "Installing Python dependencies..."
sudo -u ${APP_USER} bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn"
print_success "Dependencies installed"

# Step 6: Configure Environment Variables
print_step "Step 6: Configure Environment Variables"

if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    sudo -u ${APP_USER} cp .env.example .env
    
    echo -e "${YELLOW}===================================================${NC}"
    echo -e "${YELLOW}PENTING: Konfigurasi Environment Variables${NC}"
    echo -e "${YELLOW}===================================================${NC}"
    
    read -p "Masukkan GROQ_API_KEY: " groq_api_key
    
    # Update .env file
    sudo -u ${APP_USER} bash -c "cat > .env << EOF
# Pengaturan Groq API
GROQ_API_KEY=${groq_api_key}
GROQ_API_ENDPOINT=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile

# Pengaturan Aplikasi
UKURAN_MAKS_BERKAS_MB=10
MODE_DEBUG=false
EOF"
    
    print_success ".env file created and configured"
else
    print_info ".env file already exists"
    echo -e "${YELLOW}Jika ingin update API key, edit file: ${APP_DIR}/.env${NC}"
fi

# Step 7: Setup Systemd Service
print_step "Step 7: Setup Systemd Service"

print_info "Installing systemd service..."
cp deploy/proposal-reviewer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ${APP_NAME}
print_success "Systemd service installed and enabled"

# Step 8: Setup Nginx
print_step "Step 8: Setup Nginx Configuration"

print_info "Configuring Nginx..."

# Tanya domain/IP
echo -e "${YELLOW}===================================================${NC}"
echo -e "${YELLOW}Konfigurasi Domain/IP${NC}"
echo -e "${YELLOW}===================================================${NC}"
echo "Pilihan:"
echo "1. Gunakan IP Public saja"
echo "2. Gunakan Azure DNS Label (contoh: proposal-reviewer.southeastasia.cloudapp.azure.com)"
echo "3. Gunakan custom domain"
read -p "Pilih opsi (1/2/3): " domain_option

case $domain_option in
    1)
        PUBLIC_IP=$(curl -s ifconfig.me)
        SERVER_NAME="$PUBLIC_IP"
        print_info "Menggunakan IP: $PUBLIC_IP"
        ;;
    2)
        read -p "Masukkan DNS label Azure (contoh: proposal-reviewer): " dns_label
        read -p "Masukkan region Azure (contoh: southeastasia): " azure_region
        SERVER_NAME="${dns_label}.${azure_region}.cloudapp.azure.com"
        print_info "Menggunakan Azure DNS: $SERVER_NAME"
        ;;
    3)
        read -p "Masukkan custom domain: " custom_domain
        SERVER_NAME="$custom_domain"
        print_info "Menggunakan custom domain: $SERVER_NAME"
        ;;
    *)
        print_error "Pilihan tidak valid"
        exit 1
        ;;
esac

# Create nginx config dengan server_name yang tepat
cat > /etc/nginx/sites-available/${APP_NAME} << EOF
server {
    listen 80;
    server_name ${SERVER_NAME};

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /statis {
        alias ${APP_DIR}/app/statis;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log /var/log/nginx/${APP_NAME}_error.log;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t
systemctl restart nginx
print_success "Nginx configured and restarted"

# Step 9: Start Application
print_step "Step 9: Start Application"

print_info "Starting application..."
systemctl start ${APP_NAME}
sleep 3

# Check status
if systemctl is-active --quiet ${APP_NAME}; then
    print_success "Application started successfully!"
else
    print_error "Application failed to start. Check logs:"
    echo "sudo journalctl -u ${APP_NAME} -n 50"
    exit 1
fi

# Step 10: Setup SSL (Optional)
print_step "Step 10: Setup SSL Certificate (Optional)"

if [ "$domain_option" != "1" ]; then
    read -p "Apakah ingin install SSL certificate dengan Certbot? (y/n): " install_ssl
    
    if [ "$install_ssl" = "y" ] || [ "$install_ssl" = "Y" ]; then
        print_info "Installing Certbot..."
        apt install certbot python3-certbot-nginx -y
        
        read -p "Masukkan email untuk Certbot: " certbot_email
        
        print_info "Mendapatkan SSL certificate..."
        certbot --nginx -d ${SERVER_NAME} --non-interactive --agree-tos --email ${certbot_email}
        
        print_success "SSL certificate installed!"
    else
        print_info "Skipping SSL installation"
    fi
else
    print_info "SSL tidak tersedia untuk IP address. Gunakan domain untuk SSL."
fi

# Final Summary
print_step "🎉 Deployment Selesai!"

echo -e "${GREEN}===================================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}===================================================${NC}"
echo -e "App Directory: ${APP_DIR}"
echo -e "Service Name: ${APP_NAME}"
echo -e "Server Name: ${SERVER_NAME}"
echo -e ""
echo -e "${GREEN}Akses aplikasi di:${NC}"
if [ "$install_ssl" = "y" ] || [ "$install_ssl" = "Y" ]; then
    echo -e "  https://${SERVER_NAME}"
else
    echo -e "  http://${SERVER_NAME}"
fi
echo -e ""
echo -e "${GREEN}Useful Commands:${NC}"
echo -e "  Status aplikasi: ${YELLOW}sudo systemctl status ${APP_NAME}${NC}"
echo -e "  Restart aplikasi: ${YELLOW}sudo systemctl restart ${APP_NAME}${NC}"
echo -e "  Lihat logs: ${YELLOW}sudo journalctl -u ${APP_NAME} -f${NC}"
echo -e "  Update aplikasi: ${YELLOW}cd ${APP_DIR}/deploy && sudo ./update.sh${NC}"
echo -e "${GREEN}===================================================${NC}"
