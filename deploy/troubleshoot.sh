#!/bin/bash

##############################################
# Script Troubleshooting - AI Proposal Reviewer
# Usage: sudo ./troubleshoot.sh
##############################################

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Konfigurasi
APP_NAME="proposal-reviewer"
APP_DIR="/opt/${APP_NAME}"

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

print_step "🔍 Troubleshooting AI Proposal Reviewer"

# 1. Cek Service Status
print_step "1. Service Status"
systemctl status ${APP_NAME} --no-pager | tail -20

# 2. Cek Logs Terakhir
print_step "2. Application Logs (50 baris terakhir)"
journalctl -u ${APP_NAME} -n 50 --no-pager

# 3. Cek Environment Variables
print_step "3. Environment Variables"
if [ -f "${APP_DIR}/.env" ]; then
    print_info "File .env exists"
    echo "Content (API key disembunyikan):"
    grep -v "API_KEY" ${APP_DIR}/.env || echo "No non-sensitive vars found"
    
    # Cek apakah API key ada
    if grep -q "GROQ_API_KEY=gsk_" ${APP_DIR}/.env; then
        print_success "GROQ_API_KEY is set"
    else
        print_error "GROQ_API_KEY is NOT set or invalid!"
    fi
else
    print_error "File .env NOT found!"
fi

# 4. Test Groq API Connection
print_step "4. Test Groq API Connection"
API_KEY=$(grep "GROQ_API_KEY=" ${APP_DIR}/.env | cut -d'=' -f2)

if [ -n "$API_KEY" ]; then
    print_info "Testing Groq API..."
    response=$(curl -s -w "\n%{http_code}" -X POST https://api.groq.com/openai/v1/chat/completions \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
      }')
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Groq API connection successful!"
    else
        print_error "Groq API connection failed! HTTP code: $http_code"
        echo "$response" | head -n-1
    fi
else
    print_error "Cannot test API - API key not found"
fi

# 5. Cek Port 8000
print_step "5. Port 8000 Status"
if netstat -tuln | grep -q ":8000 "; then
    print_success "Port 8000 is listening"
    netstat -tuln | grep ":8000"
else
    print_error "Port 8000 is NOT listening!"
fi

# 6. Cek Nginx Status
print_step "6. Nginx Status"
systemctl status nginx --no-pager | head -10

# 7. Cek Nginx Error Logs
print_step "7. Nginx Error Logs (20 baris terakhir)"
if [ -f "/var/log/nginx/${APP_NAME}_error.log" ]; then
    tail -20 /var/log/nginx/${APP_NAME}_error.log
else
    print_info "No nginx error logs found"
fi

# 8. Cek Disk Space
print_step "8. Disk Space"
df -h | grep -E "Filesystem|/dev/"

# 9. Cek Memory
print_step "9. Memory Usage"
free -h

# 10. Cek Process
print_step "10. Gunicorn Processes"
ps aux | grep -E "gunicorn|uvicorn" | grep -v grep

# Summary
print_step "📋 Quick Fix Commands"
echo -e "${YELLOW}Restart application:${NC} sudo systemctl restart ${APP_NAME}"
echo -e "${YELLOW}View live logs:${NC} sudo journalctl -u ${APP_NAME} -f"
echo -e "${YELLOW}Edit .env:${NC} sudo nano ${APP_DIR}/.env"
echo -e "${YELLOW}Test endpoint:${NC} curl http://localhost:8000/api/kesehatan"
echo ""
