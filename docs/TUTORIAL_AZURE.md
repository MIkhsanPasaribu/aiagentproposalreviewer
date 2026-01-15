# 🚀 Tutorial Lengkap Deploy AI Proposal Reviewer ke Azure VM

Tutorial ini menjelaskan langkah-langkah setup Groq API dan Azure Virtual Machine untuk aplikasi AI Proposal Reviewer.

> **Note**: Aplikasi ini menggunakan **Groq API** dengan model **Llama 3.3 70B** (gratis!) sebagai pengganti Azure OpenAI.

---

## 📑 Daftar Isi

1. [Setup Groq API](#1-setup-groq-api)
2. [Setup Azure Virtual Machine](#2-setup-azure-virtual-machine)
3. [Setup Domain Azure](#3-setup-domain-azure)
4. [Deploy Aplikasi](#4-deploy-aplikasi)
5. [Konfigurasi SSL/HTTPS](#5-konfigurasi-sslhttps)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Setup Groq API

### 1.1 Daftar Akun Groq (Gratis!)

1. **Buka Groq Console**

   - Kunjungi [https://console.groq.com](https://console.groq.com)
   - Klik "Sign Up" dan daftar dengan Google/GitHub

2. **Dapatkan API Key**

   ```
   Di Groq Console:
   - Klik menu "API Keys" di sidebar
   - Klik "Create API Key"
   - Beri nama: "proposal-reviewer"
   - Copy API key yang dihasilkan
   ```

3. **Informasi API Groq**
   ```
   Endpoint: https://api.groq.com/openai/v1/chat/completions
   Model: llama-3.3-70b-versatile
   API Key: gsk_xxxxxxxxxxxxxxxxxxxxx
   ```

### 1.2 Kelebihan Groq vs Azure OpenAI

| Fitur     | Groq                      | Azure OpenAI              |
| --------- | ------------------------- | ------------------------- |
| Biaya     | **Gratis** (dengan limit) | Berbayar                  |
| Kecepatan | Sangat cepat (LPU)        | Standar                   |
| Model     | Llama 3.3 70B             | GPT-4, GPT-3.5            |
| Setup     | Mudah (1 API key)         | Kompleks (Azure resource) |
| Approval  | Tidak perlu               | Perlu approval            |

---

## 2. Setup Azure Virtual Machine

### 2.1 Buat Virtual Machine

1. **Login ke Azure Portal**

   - Buka [https://portal.azure.com](https://portal.azure.com)
   - Login dengan akun Microsoft Anda

2. **Buat Resource Group** (jika belum ada)

   ```
   Menu > Resource Groups > + Create
   - Subscription: <pilih subscription Anda>
   - Resource group name: rg-proposal-reviewer
   - Region: Southeast Asia
   - Klik "Review + create" > "Create"
   ```

3. **Buat VM Linux**

   ```text
   Menu > Virtual machines > + Create > Azure virtual machine

   Basics:
   - Subscription: <subscription Anda>
   - Resource group: rg-proposal-reviewer
   - Virtual machine name: vm-proposal-reviewer
   - Region: Southeast Asia
   - Image: Ubuntu Server 22.04 LTS - x64 Gen2
   - Size: Standard_B2s (2 vCPUs, 4 GB RAM)

   Administrator account:
   - Authentication type: Password
   - Username: viona
   - Password: <buat password yang kuat>
   - Confirm password: <ulangi password>

   Inbound port rules:
   - Public inbound ports: Allow selected ports
   - Select inbound ports: SSH (22), HTTP (80), HTTPS (443)
   ```

4. **Create VM**

   ```text
   Klik "Review + create" > "Create"
   Tunggu sampai deployment selesai.
   ```

### 2.2 Connect ke VM

```bash
# Di Windows PowerShell atau Terminal
# Connect via SSH dengan password
ssh viona@<PUBLIC_IP_ADDRESS>

# Masukkan password saat diminta
```

### 2.3 Setup Environment di VM

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y

# Create app directory
sudo mkdir -p /opt/proposal-reviewer
sudo chown viona:viona /opt/proposal-reviewer

# Create log directory
sudo mkdir -p /var/log/proposal-reviewer
sudo chown viona:viona /var/log/proposal-reviewer
```

---

## 3. Setup Domain Azure

### 3.1 Gunakan Azure DNS Label (Gratis!)

1. **Konfigurasi DNS Label untuk Public IP**

   ```
   Menu > Public IP addresses > pip-proposal-reviewer (atau nama IP VM Anda)

   Configuration:
   - DNS name label: proposal-reviewer
   - Klik "Save"
   ```

2. **Akses via Azure Domain**

   ```
   Aplikasi akan tersedia di:
   http://proposal-reviewer.southeastasia.cloudapp.azure.com

   Format: <dns-label>.<region>.cloudapp.azure.com
   ```

### 3.2 (Opsional) Custom Domain

Jika punya domain sendiri, bisa setup di Azure DNS Zone atau arahkan A record ke Public IP VM.

---

## 4. Deploy Aplikasi

### 4.1 Clone dan Setup Aplikasi

```bash
# SSH ke VM
ssh viona@<PUBLIC_IP>

# Clone repository
cd /opt/proposal-reviewer
git clone <YOUR_REPOSITORY_URL> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 4.2 Konfigurasi Environment Variables

```bash
# Create .env file
cp .env.example .env
nano .env
```

Edit file `.env`:

```ini
# Groq API Configuration
GROQ_API_KEY=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
GROQ_API_ENDPOINT=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile

# Pengaturan Aplikasi
UKURAN_MAKS_BERKAS_MB=10
MODE_DEBUG=false
```

### 4.3 Setup Systemd Service

```bash
# Copy service file
sudo cp /opt/proposal-reviewer/deploy/proposal-reviewer.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable dan start service
sudo systemctl enable proposal-reviewer
sudo systemctl start proposal-reviewer

# Cek status
sudo systemctl status proposal-reviewer
```

### 4.4 Setup Nginx Reverse Proxy

```bash
# Copy nginx config
sudo cp /opt/proposal-reviewer/deploy/nginx.conf /etc/nginx/sites-available/proposal-reviewer

# Edit domain name jika perlu
sudo nano /etc/nginx/sites-available/proposal-reviewer

# Enable site
sudo ln -s /etc/nginx/sites-available/proposal-reviewer /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 5. Konfigurasi SSL/HTTPS

### 5.1 Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 5.2 Dapatkan SSL Certificate

```bash
# Untuk Azure DNS Label
sudo certbot --nginx -d proposal-reviewer.southeastasia.cloudapp.azure.com

# Ikuti instruksi dan masukkan email
```

### 5.3 Auto-Renewal

```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Certbot sudah otomatis setup cron job untuk renewal
```

---

## 6. Troubleshooting

### 6.1 Cek Log Aplikasi

```bash
# Cek log systemd service
sudo journalctl -u proposal-reviewer -f

# Cek log nginx
sudo tail -f /var/log/nginx/error.log
```

### 6.2 Restart Services

```bash
# Restart aplikasi
sudo systemctl restart proposal-reviewer

# Restart nginx
sudo systemctl restart nginx
```

### 6.3 Common Issues

| Issue              | Solusi                                                 |
| ------------------ | ------------------------------------------------------ |
| 502 Bad Gateway    | Cek service: `sudo systemctl status proposal-reviewer` |
| Groq API Error     | Verifikasi API key di `.env`                           |
| Connection refused | Cek firewall: `sudo ufw status`                        |
| SSL Error          | Cek certificate: `sudo certbot certificates`           |

### 6.4 Test Groq API

```bash
# Test API key
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 📊 Estimasi Biaya Azure (per bulan)

| Resource        | Spesifikasi           | Estimasi Biaya |
| --------------- | --------------------- | -------------- |
| **Groq API**    | Gratis (dengan limit) | **$0**         |
| Virtual Machine | Standard_B2s          | ~$30           |
| Public IP       | Static                | ~$4            |
| Storage         | 30 GB SSD             | ~$3            |
| **Total**       |                       | **~$37/bulan** |

> 💡 **Tips Hemat**: Gunakan B1s VM untuk development (~$10/bulan)

---

## ✅ Checklist Deploy

- [ ] Groq API key sudah didapat
- [ ] VM created dan running
- [ ] SSH connection berhasil
- [ ] Python dan dependencies installed
- [ ] .env configured dengan Groq API key
- [ ] Systemd service running
- [ ] Nginx configured
- [ ] Domain/DNS configured
- [ ] SSL certificate installed
- [ ] Aplikasi accessible via HTTPS

---

## 🔗 Referensi

- [Groq Console](https://console.groq.com)
- [Groq API Documentation](https://console.groq.com/docs)
- [Azure VM Documentation](https://learn.microsoft.com/azure/virtual-machines/)
- [Certbot Documentation](https://certbot.eff.org/)
