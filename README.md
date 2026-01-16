# 🤖 AI Proposal Reviewer

Aplikasi web full-stack untuk meninjau dan mengevaluasi proposal akademik (PDF/DOCX) menggunakan AI (Groq/Llama 3.3 70B) dengan fitur riwayat review dan statistik.

## ✨ Fitur Utama

### 📝 Review Proposal

- 📄 **Upload Proposal**: Mendukung format PDF dan DOCX (maks 10 MB)
- 🤖 **Evaluasi AI**: Analisis otomatis menggunakan Groq API (Llama 3.3 70B) - **GRATIS!**
- 📊 **Skor Terperinci**: Evaluasi 5 aspek proposal:
  - 🎯 Latar Belakang (0-20 poin)
  - ❓ Formulasi Masalah (0-20 poin)
  - 🎓 Tujuan Penelitian (0-20 poin)
  - 🔬 Metodologi (0-20 poin)
  - 🏆 Luaran yang Diharapkan (0-20 poin)
- 💡 **Rekomendasi**: Daftar kekuatan, kelemahan, dan saran perbaikan detail
- 💾 **Auto-save**: Setiap review otomatis tersimpan ke database

### 📚 Riwayat Review

- 📋 **List Review**: Tampilan semua review dengan filter dan pencarian
- 📊 **Statistik**: Total review, rata-rata skor, skor tertinggi/terendah
- 👁️ **Detail View**: Lihat kembali hasil review sebelumnya
- 🗑️ **Delete**: Hapus review yang tidak diperlukan
- 💾 **Database**: SQLite untuk penyimpanan lokal

### ⚙️ Pengaturan

- 📡 **Informasi Sistem**: Model AI, endpoint, status API key
- 🎨 **Preferensi Tema**: Light/Dark mode dengan localStorage
- ℹ️ **Info Aplikasi**: Versi, teknologi stack, credits

### 🎨 UI/UX Modern

- 🖥️ **Responsive Design**: Desktop, tablet, dan mobile friendly
- 🌓 **Dark Mode**: Toggle tema terang/gelap dengan preferensi tersimpan
- 🎯 **Glassmorphism**: Desain akademis dengan backdrop blur
- ⚡ **Fast Loading**: Optimized assets dan lazy loading
- 🔔 **Toast Notifications**: Feedback real-time untuk user actions
- 📱 **Mobile Navigation**: Hamburger menu untuk layar kecil

## 🛠️ Teknologi Stack

### Backend

- **Framework**: FastAPI 0.109.0+
- **ASGI Server**: Uvicorn with Gunicorn workers
- **AI Model**: Groq API - Llama 3.3 70B Versatile
- **Database**: SQLite3 (dengan migration path ke PostgreSQL)
- **Document Parser**:
  - pypdf 3.17.0+ untuk PDF
  - docx2txt 0.8+ untuk DOCX
- **Validation**: Pydantic 2.5.0+ models

### Frontend

- **Core**: HTML5, CSS3 (dengan CSS Variables), Vanilla JavaScript
- **Icons**: SVG inline icons
- **Styling**: Custom CSS dengan glassmorphism effects
- **State Management**: LocalStorage untuk preferences

### DevOps

- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: Systemd service
- **SSL**: Let's Encrypt (Certbot)
- **Deployment**: Automated bash scripts

## 📦 Quick Start

### Instalasi Lokal (Development)

```bash
# 1. Clone repository
git clone https://github.com/username/ai-proposal-reviewer.git
cd ai-proposal-reviewer

# 2. Buat virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.contoh .env
# Edit .env dan isi GROQ_API_KEY

# 5. Buat direktori data
mkdir data

# 6. Run aplikasi
uvicorn app.utama:aplikasi --reload --port 8000
```

Buka browser: `http://localhost:8000`

### Deployment ke Azure VM (Production)

Lihat panduan lengkap di [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Quick deploy** (sudah SSH ke VM):

```bash
cd aiagentproposalreviewer
cd deploy
sudo ./deploy.sh
```

## 🔧 Konfigurasi

### Environment Variables (.env)

```ini
# API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Application Settings
UKURAN_MAKS_BERKAS_MB=10
MODE_DEBUG=false
```

### Mendapatkan Groq API Key (GRATIS)

1. Buka [console.groq.com](https://console.groq.com)
2. Sign up dengan GitHub/Google
3. Buat API Key di dashboard
4. Copy key ke `.env`

**Catatan**: Groq memberikan free tier yang sangat generous untuk development!

## 🚀 Menjalankan Aplikasi

### Development Mode

```bash
uvicorn app.utama:aplikasi --reload --host 127.0.0.1 --port 8000
```

### Production Mode (dengan Gunicorn)

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.utama:aplikasi
```

## 🧪 Testing & Quality

### Type Checking

```bash
python -m pyright
```

### Unit Tests

```bash
pytest pengujian/ -v
```

### API Testing

```bash
# Health check
curl http://localhost:8000/api/kesehatan

# Upload dan review (PowerShell)
$response = Invoke-WebRequest -Method POST -Uri "http://localhost:8000/api/review-proposal" `
  -Form @{
    berkas = Get-Item "proposal.pdf"
    jenis_proposal = "pkm"
  }
```

## 📁 Struktur Proyek

```
aiagentproposalreviewer/
├── app/
│   ├── __init__.py
│   ├── utama.py                    # FastAPI main app
│   ├── konfigurasi.py              # Environment config
│   ├── pengecualian.py             # Custom exceptions
│   ├── agen/
│   │   ├── __init__.py
│   │   └── agen_peninjau.py        # Groq AI Agent
│   ├── layanan/
│   │   ├── __init__.py
│   │   ├── pemuat_dokumen.py       # PDF/DOCX loader
│   │   ├── pemformat_keluaran.py   # Output formatter
│   │   └── database_riwayat.py     # SQLite database manager
│   ├── skema/
│   │   ├── __init__.py
│   │   └── model.py                # Pydantic models
│   ├── templat/
│   │   └── indeks.html             # Main HTML template
│   └── statis/
│       ├── css/
│       │   └── gaya_utama.css      # Main stylesheet
│       └── js/
│           └── skrip_utama.js      # Main JavaScript
├── deploy/                          # Deployment scripts
│   ├── deploy.sh                    # Full deployment
│   ├── update.sh                    # Update script
│   ├── setup-ssl.sh                 # SSL setup
│   ├── quickfix.sh                  # Emergency fix
│   ├── troubleshoot.sh              # Diagnostic tool
│   ├── test-api.sh                  # API testing
│   ├── proposal-reviewer.service    # Systemd service
│   ├── nginx.conf                   # Nginx config
│   └── README.md                    # Deploy docs
├── data/                            # Database directory
│   └── riwayat_review.db           # SQLite database
├── pengujian/                       # Tests
│   ├── __init__.py
│   └── uji_agen.py
├── docs/                            # Documentation
├── .env.contoh                      # Example environment
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
├── DEPLOYMENT_GUIDE.md              # Deployment guide
└── CHANGELOG.md                     # Version history
```

## 📝 API Endpoints

### Public Endpoints

| Method | Endpoint               | Deskripsi                    | Body/Params                                   |
| ------ | ---------------------- | ---------------------------- | --------------------------------------------- |
| GET    | `/`                    | Halaman utama                | -                                             |
| GET    | `/api/kesehatan`       | Health check                 | -                                             |
| POST   | `/api/review-proposal` | Review proposal              | `berkas` (file), `jenis_proposal` (form-data) |
| GET    | `/api/riwayat`         | List semua review            | `?limit=50` (optional)                        |
| GET    | `/api/riwayat/{id}`    | Detail review berdasarkan ID | -                                             |
| DELETE | `/api/riwayat/{id}`    | Hapus review                 | -                                             |
| GET    | `/api/statistik`       | Statistik review             | -                                             |
| GET    | `/api/pengaturan`      | Konfigurasi aplikasi         | -                                             |

### Response Examples

**POST /api/review-proposal**

```json
{
  "berhasil": true,
  "pesan": "Review berhasil dilakukan",
  "data": {
    "skor": 85,
    "detail_skor": {
      "latar_belakang": 18,
      "formulasi_masalah": 17,
      "tujuan": 18,
      "metodologi": 16,
      "luaran": 16
    },
    "daftar_kekuatan": ["...", "..."],
    "daftar_kelemahan": ["...", "..."],
    "daftar_saran": ["...", "..."],
    "ringkasan": "..."
  }
}
```

**GET /api/statistik**

```json
{
  "berhasil": true,
  "data": {
    "total_review": 42,
    "rata_rata_skor": 78.5,
    "skor_tertinggi": 95,
    "skor_terendah": 65
  }
}
```

## 🎯 Cara Penggunaan

### 1. Upload Proposal

- Klik "Pilih Berkas" atau drag & drop file
- Pilih jenis proposal (PKM/Skripsi/Hibah)
- Klik "Review Proposal"

### 2. Lihat Hasil

- Skor total dan per aspek
- Kekuatan proposal
- Kelemahan proposal
- Saran perbaikan
- Ringkasan evaluasi

### 3. Kelola Riwayat

- Klik menu "Riwayat Review"
- Lihat statistik review Anda
- Klik review untuk melihat detail
- Hapus review yang tidak diperlukan

### 4. Atur Preferensi

- Klik menu "Pengaturan"
- Ubah tema (Terang/Gelap)
- Lihat informasi sistem
- Cek status API key

## 🎨 Panduan Warna & Desain

### Color Palette

| Komponen        | Light Mode | Dark Mode | Hex       |
| --------------- | ---------- | --------- | --------- |
| Primer (Navy)   | `#1A365D`  | `#2D3748` | Navy/Gray |
| Sekunder (Emas) | `#B7791F`  | `#D69E2E` | Gold      |
| Aksen (Biru)    | `#3B82F6`  | `#4299E1` | Blue      |
| Sukses          | `#38A169`  | `#48BB78` | Green     |
| Bahaya          | `#E53E3E`  | `#F56565` | Red       |
| Peringatan      | `#DD6B20`  | `#ED8936` | Orange    |

### Design Principles

- 🎨 **Glassmorphism**: Backdrop blur dengan transparansi
- 📱 **Mobile-first**: Responsive dari 320px ke 4K
- ♿ **Accessible**: WCAG 2.1 AA compliant
- ⚡ **Fast**: Optimized assets < 500KB total
- 🎯 **Intuitive**: Max 3 clicks untuk semua fitur

## 🐛 Troubleshooting

### Error: "Terjadi kesalahan saat memproses proposal"

**Solusi**:

1. Cek API key di `.env`
2. Pastikan file PDF/DOCX valid
3. Cek logs: `sudo journalctl -u proposal-reviewer -n 50`
4. Run diagnostic: `./deploy/troubleshoot.sh`

### Error: "No module named 'langchain_community'"

**Solusi**: Sudah fixed! Kami menggunakan `pypdf` sebagai gantinya.

```bash
# Quick fix di production
cd ~/aiagentproposalreviewer/deploy
./quickfix.sh
```

### Database Locked

**Solusi**:

```bash
# Stop service
sudo systemctl stop proposal-reviewer

# Reset database (BACKUP FIRST!)
cp data/riwayat_review.db data/riwayat_review.db.backup
rm data/riwayat_review.db

# Restart
sudo systemctl start proposal-reviewer
```

### More Issues?

Lihat [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) atau [deploy/TROUBLESHOOTING.md](deploy/TROUBLESHOOTING.md)

## 🚀 Deployment Options

### Option 1: Azure VM (Recommended)

- Full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Automated scripts available
- Production-ready dengan Nginx + SSL

### Option 2: Docker (Coming Soon)

```bash
docker-compose up -d
```

### Option 3: Vercel/Netlify (Frontend Only)

- Deploy static files
- Point API to separate backend

## 📊 Performance

- **Load Time**: < 2s (first load)
- **Review Time**: 3-10s (tergantung panjang proposal)
- **Database**: SQLite (dapat handle 100K+ reviews)
- **Concurrent Users**: 20+ dengan 4 Gunicorn workers
- **Max File Size**: 10 MB (configurable)

## 🔐 Security

- ✅ No API key exposure (server-side only)
- ✅ XSS prevention (HTML escaping)
- ✅ File type validation
- ✅ File size limits
- ✅ HTTPS ready (SSL setup included)
- ✅ Environment variable configuration
- ✅ Database file in .gitignore

## 🗺️ Roadmap

### v1.2.0 (Q1 2024)

- [ ] Export hasil ke PDF
- [ ] Batch upload multiple files
- [ ] Compare 2 proposals
- [ ] Custom scoring weights
- [ ] User authentication

### v1.3.0 (Q2 2024)

- [ ] PostgreSQL support
- [ ] Real-time collaboration
- [ ] REST API documentation (Swagger)
- [ ] Email notifications
- [ ] Analytics dashboard

### v2.0.0 (Q3 2024)

- [ ] Multi-language support (EN/ID)
- [ ] Custom AI prompts
- [ ] Integration dengan LMS
- [ ] Mobile app (React Native)

## 🤝 Contributing

Contributions welcome! Silakan:

1. Fork repository
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Tambah fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

### Code Style

- Follow PEP 8 untuk Python
- Gunakan Bahasa Indonesia untuk nama variabel/fungsi
- Tulis docstring untuk semua functions
- Add tests untuk fitur baru

## 📄 Lisensi

MIT License - Feel free to use for academic/commercial purposes.

## 👥 Credits

- **Developer**: AI Proposal Reviewer Team
- **AI Model**: Groq (Llama 3.3 70B Versatile)
- **Framework**: FastAPI
- **Design**: Custom CSS with Glassmorphism

## 📞 Support

- 📧 Email: support@aiproposalreviewer.com
- 💬 GitHub Issues: [Create Issue](https://github.com/username/repo/issues)
- 📚 Documentation: [docs/](docs/)
- 🐛 Bug Reports: Use issue template

---

⭐ **Star this repo** jika membantu project Anda!

Made with ❤️ for Indonesian Academic Community
