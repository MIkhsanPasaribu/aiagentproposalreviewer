# Changelog

Semua perubahan penting pada proyek ini akan didokumentasikan di file ini.

## [1.1.0] - 2024-01-XX

### ✨ Fitur Baru

#### 1. **Riwayat Review**

- Implementasi database SQLite untuk menyimpan riwayat review
- Halaman Riwayat Review dengan tampilan list dan statistik
- Statistik: Total Review, Rata-rata Skor, Skor Tertinggi, Skor Terendah
- Detail view untuk setiap review
- Fitur hapus review dengan konfirmasi
- Otomatis menyimpan setiap review ke database

#### 2. **Halaman Pengaturan**

- Informasi sistem (Model AI, API Endpoint, Status API Key)
- Preferensi tema (Terang/Gelap)
- Informasi aplikasi (Versi, Teknologi)

#### 3. **Navigasi Multi-halaman**

- Sidebar navigation dengan 4 menu: Beranda, Review Proposal, Riwayat Review, Pengaturan
- Support URL hash untuk deep linking (e.g., `#riwayat`, `#pengaturan`)
- Active state indicator pada menu
- Responsive untuk mobile (hamburger menu)

### 🔧 Perbaikan

#### API & Backend

- **app/layanan/database_riwayat.py**: Class `DatabaseRiwayat` untuk manajemen database
- **app/utama.py**:
  - Endpoint `/api/riwayat` - GET list semua review
  - Endpoint `/api/riwayat/{id}` - GET detail review
  - Endpoint `/api/riwayat/{id}` - DELETE review
  - Endpoint `/api/statistik` - GET statistik review
  - Endpoint `/api/pengaturan` - GET konfigurasi aplikasi
  - Auto-save review ke database setelah berhasil
- **app/skema/model.py**: Model baru untuk response riwayat dan statistik

#### Frontend

- **app/templat/indeks.html**: Struktur 3 section (beranda, riwayat, pengaturan)
- **app/statis/css/gaya_utama.css**:
  - Styling untuk `.riwayat-item`, `.stats-grid`, `.settings-grid`
  - Badge variants untuk jenis proposal
  - Empty state styling
  - Responsive breakpoints
- **app/statis/js/skrip_utama.js**:
  - `navigasiKe()` - Handle navigation antar halaman
  - `muatRiwayat()` - Load dan display riwayat review
  - `muatStatistik()` - Load statistik
  - `tampilkanDetailRiwayat()` - Show detail review
  - `hapusRiwayat()` - Delete review dengan konfirmasi
  - `muatPengaturan()` - Load pengaturan aplikasi
  - `formatTanggal()` - Format tanggal Indonesia
  - `escapeHtml()` - Security XSS prevention

#### Deployment & DevOps

- **deploy/deploy.sh**: Full automated deployment script
- **deploy/update.sh**: Automated update script
- **deploy/setup-ssl.sh**: SSL certificate setup
- **deploy/quickfix.sh**: Emergency dependency fix
- **deploy/troubleshoot.sh**: Comprehensive diagnostic tool
- **deploy/test-api.sh**: API endpoint testing
- **DEPLOYMENT_GUIDE.md**: Panduan deployment lengkap

### 🐛 Bug Fixes

- Fix "No module named 'langchain_community'" error
- Ganti `langchain_community.document_loaders.PyPDFLoader` dengan `pypdf.PdfReader`
- Tambah error handling untuk PDF loading yang gagal
- Fix theme toggle persistence dengan localStorage

### 📚 Dokumentasi

- **README.md**: Update dengan fitur-fitur baru
- **DEPLOYMENT_GUIDE.md**: Panduan deployment lengkap
- **deploy/README.md**: Dokumentasi deployment scripts
- **deploy/TROUBLESHOOTING.md**: Troubleshooting guide
- **deploy/QUICKFIX.md**: Quick fix guide
- **CHANGELOG.md**: File ini

### 🔒 Security

- Escape HTML output untuk prevent XSS
- Validasi input file upload
- API key tidak pernah di-expose ke frontend
- Database file tidak di-commit ke git (.gitignore)
- Environment variables untuk sensitive data

### 📦 Dependencies

Tetap menggunakan dependencies yang sama dengan penambahan:

- `pypdf>=3.17.0` (menggantikan langchain_community)

### 🎨 UI/UX Improvements

- Loading spinner saat fetching data
- Empty state untuk list kosong
- Confirmation dialog sebelum delete
- Toast notification untuk feedback user
- Badge untuk jenis proposal (PKM, Skripsi, Hibah)
- Responsive design untuk mobile
- Smooth transitions antar halaman

## [1.0.0] - 2024-01-XX

### ✨ Initial Release

- Upload dan review proposal (PDF/DOCX)
- AI-powered evaluation menggunakan Groq API (Llama 3.3 70B)
- Skor per aspek: Latar Belakang, Masalah, Tujuan, Metodologi, Luaran
- Display kekuatan, kelemahan, dan saran
- Export hasil review ke JSON
- Dark/Light theme
- Responsive design

---

**Format**: [Major.Minor.Patch]

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes
