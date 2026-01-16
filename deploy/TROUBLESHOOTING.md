# 🔧 Troubleshooting Guide

## Problem: "Terjadi kesalahan saat memproses proposal" di Production

### Langkah Diagnosis

#### 1. SSH ke Server

```bash
ssh viona@<PUBLIC_IP_OR_DOMAIN>
```

#### 2. Jalankan Script Troubleshooting

```bash
cd /opt/proposal-reviewer/deploy
chmod +x troubleshoot.sh
sudo ./troubleshoot.sh
```

Script akan memeriksa:

- ✅ Status service
- ✅ Application logs
- ✅ Environment variables
- ✅ Groq API connection
- ✅ Port 8000 status
- ✅ Nginx status
- ✅ Resource usage

#### 3. Cek Logs Real-time

```bash
# Lihat logs aplikasi secara real-time
sudo journalctl -u proposal-reviewer -f

# Coba upload file dari browser, lalu perhatikan logs
```

### Common Issues & Solutions

#### ❌ Issue 1: API Key Tidak Terbaca

**Gejala:**

```
GROQ_API_KEY is NOT set or invalid!
```

**Solusi:**

```bash
# Edit file .env
sudo nano /opt/proposal-reviewer/.env

# Pastikan formatnya benar:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Restart aplikasi
sudo systemctl restart proposal-reviewer
```

#### ❌ Issue 2: Groq API Connection Failed

**Gejala:**

```
Groq API connection failed! HTTP code: 401
```

**Solusi:**

1. Cek API key valid di https://console.groq.com
2. Generate API key baru jika perlu
3. Update di `/opt/proposal-reviewer/.env`
4. Restart: `sudo systemctl restart proposal-reviewer`

**Gejala:**

```
Groq API connection failed! HTTP code: 429
```

**Solusi:**

- Rate limit tercapai, tunggu beberapa menit
- Atau upgrade akun Groq

#### ❌ Issue 3: Port 8000 Tidak Listening

**Gejala:**

```
Port 8000 is NOT listening!
```

**Solusi:**

```bash
# Cek apakah service running
sudo systemctl status proposal-reviewer

# Jika failed, cek error
sudo journalctl -u proposal-reviewer -n 100

# Cek apakah ada process lain di port 8000
sudo netstat -tulpn | grep 8000

# Kill process jika ada
sudo kill -9 <PID>

# Restart service
sudo systemctl restart proposal-reviewer
```

#### ❌ Issue 4: 502 Bad Gateway

**Gejala:**
Browser menampilkan "502 Bad Gateway"

**Solusi:**

```bash
# Cek status aplikasi
sudo systemctl status proposal-reviewer

# Jika not running, start
sudo systemctl start proposal-reviewer

# Cek apakah port 8000 listening
curl http://localhost:8000/api/kesehatan

# Jika OK, restart nginx
sudo systemctl restart nginx
```

#### ❌ Issue 5: Timeout Error

**Gejala:**

```
Timeout saat memproses proposal
```

**Solusi:**

1. File terlalu besar - coba file lebih kecil (<2MB)
2. Groq API slow - tunggu dan coba lagi
3. Increase timeout di service file:

```bash
sudo nano /etc/systemd/system/proposal-reviewer.service

# Tambahkan di section [Service]:
TimeoutStartSec=300
TimeoutStopSec=300

# Reload dan restart
sudo systemctl daemon-reload
sudo systemctl restart proposal-reviewer
```

#### ❌ Issue 6: Permission Denied

**Gejala:**

```
Permission denied: '/opt/proposal-reviewer/...'
```

**Solusi:**

```bash
# Fix ownership
sudo chown -R viona:viona /opt/proposal-reviewer

# Fix log directory
sudo chown -R viona:viona /var/log/proposal-reviewer

# Restart
sudo systemctl restart proposal-reviewer
```

### Testing Checklist

Setelah fix, test dengan checklist ini:

```bash
# 1. Health check
curl http://localhost:8000/api/kesehatan
# Expected: {"status":"sehat","versi":"1.0.0"}

# 2. Homepage
curl -I http://localhost:8000/
# Expected: HTTP/1.1 200 OK

# 3. Static files
curl -I http://localhost:8000/statis/css/gaya_utama.css
# Expected: HTTP/1.1 200 OK

# 4. Test API (dari browser)
# Upload file proposal kecil (< 1MB)
```

### Monitoring Commands

```bash
# Real-time logs
sudo journalctl -u proposal-reviewer -f

# Last 100 lines
sudo journalctl -u proposal-reviewer -n 100

# Logs since 1 hour ago
sudo journalctl -u proposal-reviewer --since "1 hour ago"

# Nginx error logs
sudo tail -f /var/log/nginx/proposal-reviewer_error.log

# Application error logs
sudo tail -f /var/log/proposal-reviewer/error.log

# Check memory
free -h

# Check disk
df -h

# Check processes
ps aux | grep gunicorn
```

### Quick Restart

```bash
# Restart everything
sudo systemctl restart proposal-reviewer nginx

# Or just app
sudo systemctl restart proposal-reviewer
```

### Force Update & Reset

Jika semua gagal, reset dengan update script:

```bash
cd /opt/proposal-reviewer/deploy
sudo ./update.sh
```

### Get Help

Jika masih error, kumpulkan info ini:

```bash
# Save diagnostic info
cd /opt/proposal-reviewer/deploy
sudo ./troubleshoot.sh > diagnostic.txt 2>&1

# Share diagnostic.txt saat meminta bantuan
```

### Emergency: Start from Scratch

```bash
# Stop service
sudo systemctl stop proposal-reviewer

# Backup .env
sudo cp /opt/proposal-reviewer/.env ~/env-backup

# Remove app
sudo rm -rf /opt/proposal-reviewer

# Re-run deployment
cd /tmp
git clone https://github.com/MIkhsanPasaribu/aiagentproposalreviewer.git
cd aiagentproposalreviewer/deploy
sudo ./deploy.sh

# Restore .env
sudo cp ~/env-backup /opt/proposal-reviewer/.env
sudo systemctl restart proposal-reviewer
```
