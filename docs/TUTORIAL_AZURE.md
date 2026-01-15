# 🚀 Tutorial Lengkap Deploy AI Proposal Reviewer ke Azure

Tutorial ini menjelaskan langkah-langkah setup Azure OpenAI, Azure Virtual Machine, dan konfigurasi domain untuk aplikasi AI Proposal Reviewer.

---

## 📑 Daftar Isi

1. [Setup Azure OpenAI](#1-setup-azure-openai)
2. [Setup Azure Virtual Machine](#2-setup-azure-virtual-machine)
3. [Setup Domain Azure](#3-setup-domain-azure)
4. [Deploy Aplikasi](#4-deploy-aplikasi)
5. [Konfigurasi SSL/HTTPS](#5-konfigurasi-sslhttps)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Setup Azure OpenAI

### 1.1 Buat Resource Azure OpenAI

1. **Login ke Azure Portal**

   - Buka [https://portal.azure.com](https://portal.azure.com)
   - Login dengan akun Microsoft Anda

2. **Buat Resource Group** (jika belum ada)

   ```
   Menu > Resource Groups > + Create
   - Subscription: <pilih subscription Anda>
   - Resource group name: rg-proposal-reviewer
   - Region: Southeast Asia (atau region terdekat)
   - Klik "Review + create" > "Create"
   ```

3. **Buat Azure OpenAI Resource**

   ```
   Menu > Create a resource > Search "Azure OpenAI"
   - Klik "Azure OpenAI" > "Create"

   Basics:
   - Subscription: <subscription Anda>
   - Resource group: rg-proposal-reviewer
   - Region: East US (atau region dengan ketersediaan)
   - Name: openai-proposal-reviewer (harus unik global)
   - Pricing tier: Standard S0

   - Klik "Next" > "Next" > "Review + create" > "Create"
   ```

   > ⚠️ **Catatan**: Azure OpenAI memerlukan approval. Jika belum disetujui, apply di [https://aka.ms/oai/access](https://aka.ms/oai/access)

4. **Deploy Model GPT**

   ```
   Buka resource Azure OpenAI > Go to Azure OpenAI Studio

   Di Azure OpenAI Studio:
   - Menu Deployments > + Create new deployment
   - Model: gpt-4 atau gpt-35-turbo
   - Deployment name: gpt-proposal-reviewer
   - Klik "Create"
   ```

5. **Catat Kredensial**

   ```
   Di Azure Portal > Resource Azure OpenAI > Keys and Endpoint

   Catat:
   - Endpoint: https://openai-proposal-reviewer.openai.azure.com/
   - KEY 1: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   - Deployment Name: gpt-proposal-reviewer
   ```

---

## 2. Setup Azure Virtual Machine

### 2.1 Buat Virtual Machine

1. **Buat VM Linux**

   ```
   Menu > Virtual machines > + Create > Azure virtual machine

   Basics:
   - Subscription: <subscription Anda>
   - Resource group: rg-proposal-reviewer
   - Virtual machine name: vm-proposal-reviewer
   - Region: Southeast Asia
   - Availability options: No infrastructure redundancy required
   - Image: Ubuntu Server 22.04 LTS - x64 Gen2
   - Size: Standard_B2s (2 vCPUs, 4 GB RAM) *untuk development
         atau Standard_D2s_v3 (2 vCPUs, 8 GB RAM) *untuk production

   Administrator account:
   - Authentication type: SSH public key
   - Username: azureuser
   - SSH public key source: Generate new key pair
   - Key pair name: vm-proposal-reviewer-key

   Inbound port rules:
   - Public inbound ports: Allow selected ports
   - Select inbound ports: SSH (22), HTTP (80), HTTPS (443)
   ```

2. **Konfigurasi Disk**

   ```
   Tab "Disks":
   - OS disk type: Standard SSD (untuk hemat biaya)
   - Size: 30 GB (default cukup)
   ```

3. **Konfigurasi Networking**

   ```
   Tab "Networking":
   - Virtual network: (create new) vnet-proposal-reviewer
   - Subnet: default (10.0.0.0/24)
   - Public IP: (create new) pip-proposal-reviewer
   - NIC network security group: Basic
   - Public inbound ports: SSH, HTTP, HTTPS (seperti di Basics)
   ```

4. **Review dan Create**

   ```
   Klik "Review + create" > "Create"

   ⚠️ PENTING: Download SSH private key saat diminta!
   Simpan file .pem dengan aman.
   ```

### 2.2 Connect ke VM

```bash
# Di Windows PowerShell atau Terminal

# Set permission untuk key file
icacls "vm-proposal-reviewer-key.pem" /inheritance:r /grant:r "$($env:USERNAME):(R)"

# Connect via SSH
ssh -i "vm-proposal-reviewer-key.pem" azureuser@<PUBLIC_IP_ADDRESS>
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
sudo chown azureuser:azureuser /opt/proposal-reviewer
```

---

## 3. Setup Domain Azure

### 3.1 Opsi A: Gunakan Azure DNS Zone (Custom Domain)

1. **Buat DNS Zone**

   ```
   Menu > DNS zones > + Create

   - Subscription: <subscription Anda>
   - Resource group: rg-proposal-reviewer
   - Name: proposalreviewer.com (domain Anda)
   - Klik "Review + create" > "Create"
   ```

2. **Tambah A Record**

   ```
   Buka DNS Zone > + Record set

   - Name: @ (untuk root domain) atau www
   - Type: A
   - TTL: 3600
   - IP address: <PUBLIC_IP VM Anda>
   - Klik "OK"
   ```

3. **Update Nameservers di Domain Registrar**

   ```
   Catat nameservers dari Azure DNS Zone:
   - ns1-XX.azure-dns.com
   - ns2-XX.azure-dns.net
   - ns3-XX.azure-dns.org
   - ns4-XX.azure-dns.info

   Masuk ke domain registrar Anda dan update nameservers.
   ```

### 3.2 Opsi B: Gunakan Azure DNS Label (Subdomain Gratis)

1. **Konfigurasi DNS Label untuk Public IP**

   ```
   Menu > Public IP addresses > pip-proposal-reviewer

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

---

## 4. Deploy Aplikasi

### 4.1 Clone dan Setup Aplikasi

```bash
# SSH ke VM
ssh -i "vm-proposal-reviewer-key.pem" azureuser@<PUBLIC_IP>

# Clone repository
cd /opt/proposal-reviewer
git clone <YOUR_REPOSITORY_URL> .

# Atau upload file manual
# scp -i "vm-proposal-reviewer-key.pem" -r ./* azureuser@<PUBLIC_IP>:/opt/proposal-reviewer/

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cp .env.example .env
nano .env
```

### 4.2 Konfigurasi Environment Variables

```bash
# Edit .env dengan kredensial Azure OpenAI
nano /opt/proposal-reviewer/.env
```

```ini
# Isi dengan kredensial Azure OpenAI Anda
AZURE_OPENAI_ENDPOINT=https://openai-proposal-reviewer.openai.azure.com/
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_DEPLOYMENT=gpt-proposal-reviewer
AZURE_OPENAI_API_VERSION=2024-02-15-preview

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

# Enable site
sudo ln -s /etc/nginx/sites-available/proposal-reviewer /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 5. Konfigurasi SSL/HTTPS

### 5.1 Install Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y
```

### 5.2 Dapatkan SSL Certificate

**Untuk Custom Domain:**

```bash
sudo certbot --nginx -d proposalreviewer.com -d www.proposalreviewer.com
```

**Untuk Azure DNS Label:**

```bash
sudo certbot --nginx -d proposal-reviewer.southeastasia.cloudapp.azure.com
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
sudo tail -f /var/log/nginx/access.log
```

### 6.2 Restart Services

```bash
# Restart aplikasi
sudo systemctl restart proposal-reviewer

# Restart nginx
sudo systemctl restart nginx
```

### 6.3 Common Issues

| Issue              | Solusi                                                                 |
| ------------------ | ---------------------------------------------------------------------- |
| 502 Bad Gateway    | Cek apakah service berjalan: `sudo systemctl status proposal-reviewer` |
| Connection refused | Cek firewall: `sudo ufw status` dan pastikan port 80/443 terbuka       |
| SSL Error          | Cek certificate: `sudo certbot certificates`                           |
| Azure OpenAI Error | Verifikasi endpoint dan API key di `.env`                              |

### 6.4 Firewall Configuration

```bash
# Jika menggunakan UFW
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 📊 Estimasi Biaya Azure (per bulan)

| Resource        | Spesifikasi          | Estimasi Biaya    |
| --------------- | -------------------- | ----------------- |
| Azure OpenAI    | GPT-4 ~1000 requests | ~$30-50           |
| Virtual Machine | Standard_B2s         | ~$30              |
| Public IP       | Static               | ~$4               |
| Storage         | 30 GB SSD            | ~$3               |
| **Total**       |                      | **~$70-90/bulan** |

> 💡 **Tips Hemat**: Gunakan B1s VM untuk development (~$10/bulan) dan scale up untuk production.

---

## ✅ Checklist Deploy

- [ ] Azure OpenAI resource created
- [ ] GPT model deployed
- [ ] VM created dan running
- [ ] SSH connection berhasil
- [ ] Python dan dependencies installed
- [ ] .env configured dengan kredensial
- [ ] Systemd service running
- [ ] Nginx configured
- [ ] Domain/DNS configured
- [ ] SSL certificate installed
- [ ] Aplikasi accessible via HTTPS

---

## 🔗 Referensi

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Azure VM Documentation](https://learn.microsoft.com/azure/virtual-machines/)
- [Azure DNS Documentation](https://learn.microsoft.com/azure/dns/)
- [Certbot Documentation](https://certbot.eff.org/)
