# 📖 README - Deploy Scripts

Scripts untuk otomasi deployment AI Proposal Reviewer ke Azure VM.

## 📁 File dalam Folder Deploy

```
deploy/
├── deploy.sh                    # Script deployment utama (first time)
├── update.sh                    # Script update aplikasi
├── setup-ssl.sh                 # Script setup SSL certificate
├── proposal-reviewer.service    # Systemd service file
├── nginx.conf                   # Nginx configuration template
└── README.md                    # Dokumentasi ini
```

## 🚀 Quick Start

### 1. First Time Deployment

Setelah SSH ke Azure VM:

```bash
# Clone repository
cd /tmp
git clone https://github.com/MIkhsanPasaribu/aiagentproposalreviewer.git
cd aiagentproposalreviewer/deploy

# Jalankan script deployment
chmod +x deploy.sh
sudo ./deploy.sh
```

Script akan:

- ✅ Install semua dependencies (Python, Nginx, Git, dll)
- ✅ Clone repository ke `/opt/proposal-reviewer`
- ✅ Setup virtual environment
- ✅ Install Python packages
- ✅ Konfigurasi `.env` (input API key)
- ✅ Setup systemd service
- ✅ Konfigurasi Nginx (input domain/IP)
- ✅ Start aplikasi
- ✅ (Optional) Setup SSL certificate

### 2. Update Aplikasi

Untuk update ke versi terbaru:

```bash
cd /opt/proposal-reviewer/deploy
sudo ./update.sh
```

Script akan:

- ✅ Stop aplikasi
- ✅ Backup file `.env`
- ✅ Pull kode terbaru dari Git
- ✅ Restore file `.env`
- ✅ Update dependencies
- ✅ Restart aplikasi

### 3. Setup SSL (Opsional)

Untuk install SSL certificate:

```bash
cd /opt/proposal-reviewer/deploy
sudo ./setup-ssl.sh <domain-anda>
```

Contoh:

```bash
sudo ./setup-ssl.sh proposal-reviewer.southeastasia.cloudapp.azure.com
```

## 📋 Prerequisites

- Azure VM dengan Ubuntu 22.04 LTS
- User dengan sudo access (default: `viona`)
- Port terbuka: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Groq API Key (gratis dari https://console.groq.com)

## 🔧 Konfigurasi

### Environment Variables (.env)

```ini
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GROQ_API_ENDPOINT=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
UKURAN_MAKS_BERKAS_MB=10
MODE_DEBUG=false
```

### Systemd Service

Service akan otomatis running dengan:

- 4 worker processes (Gunicorn)
- Uvicorn worker class (async support)
- Auto-restart on failure
- Logging ke `/var/log/proposal-reviewer/`

### Nginx Configuration

- Reverse proxy ke port 8000
- Max file size: 10MB
- Static files caching
- WebSocket support

## 📝 Useful Commands

```bash
# Status aplikasi
sudo systemctl status proposal-reviewer

# Restart aplikasi
sudo systemctl restart proposal-reviewer

# Stop aplikasi
sudo systemctl stop proposal-reviewer

# Start aplikasi
sudo systemctl start proposal-reviewer

# Lihat logs real-time
sudo journalctl -u proposal-reviewer -f

# Lihat 50 baris terakhir logs
sudo journalctl -u proposal-reviewer -n 50

# Cek nginx status
sudo systemctl status nginx

# Test nginx config
sudo nginx -t

# Reload nginx (tanpa downtime)
sudo systemctl reload nginx

# Cek SSL certificate
sudo certbot certificates
```

## 🔍 Troubleshooting

Jika aplikasi error di production:

```bash
# 1. Jalankan diagnostic script
cd /opt/proposal-reviewer/deploy
chmod +x troubleshoot.sh
sudo ./troubleshoot.sh

# 2. Lihat panduan lengkap
cat TROUBLESHOOTING.md
```

Lihat [TROUBLESHOOTING.md](TROUBLESHOOTING.md) untuk panduan lengkap.

### Common Issues

| Issue                      | Quick Fix                                  |
| -------------------------- | ------------------------------------------ |
| Error saat upload proposal | `sudo journalctl -u proposal-reviewer -f`  |
| 502 Bad Gateway            | `sudo systemctl restart proposal-reviewer` |
| API key error              | Edit `/opt/proposal-reviewer/.env`         |
| Port already used          | `sudo systemctl restart proposal-reviewer` |

## 📚 Referensi

- [Tutorial Lengkap](../docs/TUTORIAL_AZURE.md)
- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
