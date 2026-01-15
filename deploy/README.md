# 📦 Deploy Folder - AI Proposal Reviewer

Folder ini berisi file konfigurasi untuk deploy aplikasi ke Azure VM.

## 📁 Struktur File

```
deploy/
├── README.md               # Dokumentasi ini
├── deploy.sh               # Script deployment otomatis
├── proposal-reviewer.service  # Systemd service configuration
├── nginx.conf              # Nginx reverse proxy config
├── nginx-docker.conf       # Nginx config untuk Docker
├── Dockerfile              # Docker image configuration
└── docker-compose.yml      # Docker Compose configuration
```

## 🚀 Cara Deploy

### Opsi 1: Deploy Manual ke VM

```bash
# 1. SSH ke Azure VM
ssh -i "your-key.pem" azureuser@<PUBLIC_IP>

# 2. Clone repository
git clone <YOUR_REPO> /opt/proposal-reviewer
cd /opt/proposal-reviewer

# 3. Jalankan script deploy
chmod +x deploy/deploy.sh
./deploy/deploy.sh

# 4. Edit konfigurasi
nano /opt/proposal-reviewer/.env

# 5. Restart service
sudo systemctl restart proposal-reviewer
```

### Opsi 2: Deploy dengan Docker

```bash
# 1. SSH ke VM
ssh -i "your-key.pem" azureuser@<PUBLIC_IP>

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Clone dan deploy
git clone <YOUR_REPO> /opt/proposal-reviewer
cd /opt/proposal-reviewer

# 4. Setup environment
cp .env.example .env
nano .env

# 5. Build dan jalankan
cd deploy
docker-compose up -d --build
```

## 🔧 Konfigurasi

### Systemd Service

- File: `proposal-reviewer.service`
- Lokasi target: `/etc/systemd/system/`
- Perintah:
  ```bash
  sudo systemctl enable proposal-reviewer
  sudo systemctl start proposal-reviewer
  ```

### Nginx

- File: `nginx.conf`
- Lokasi target: `/etc/nginx/sites-available/`
- Ganti `proposal-reviewer.southeastasia.cloudapp.azure.com` dengan domain Anda

## 📋 Checklist Deploy

- [ ] Azure OpenAI credentials di `.env`
- [ ] Domain/DNS configured
- [ ] Firewall ports 80/443 dibuka
- [ ] SSL certificate installed
- [ ] Service running (`systemctl status proposal-reviewer`)

## 📖 Tutorial Lengkap

Lihat [docs/TUTORIAL_AZURE.md](../docs/TUTORIAL_AZURE.md) untuk panduan lengkap setup Azure.
