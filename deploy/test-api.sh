#!/bin/bash

##############################################
# Script Test Endpoint - AI Proposal Reviewer
# Usage: ./test-api.sh
##############################################

# Warna
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Cek parameter
if [ -z "$1" ]; then
    HOST="localhost:8000"
else
    HOST="$1"
fi

echo "Testing API at: $HOST"
echo "========================================"

# Test 1: Health Check
print_info "Testing health check endpoint..."
response=$(curl -s -w "\n%{http_code}" "http://${HOST}/api/kesehatan")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    print_success "Health check OK: $body"
else
    print_error "Health check failed: HTTP $http_code"
fi

# Test 2: Homepage
print_info "Testing homepage..."
response=$(curl -s -w "\n%{http_code}" "http://${HOST}/")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    print_success "Homepage OK"
else
    print_error "Homepage failed: HTTP $http_code"
fi

# Test 3: Static Files
print_info "Testing static CSS..."
response=$(curl -s -w "\n%{http_code}" "http://${HOST}/statis/css/gaya_utama.css")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    print_success "Static CSS OK"
else
    print_error "Static CSS failed: HTTP $http_code"
fi

echo ""
echo "========================================"
echo "Test selesai!"
