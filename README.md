# 🤖 AI Proposal Reviewer

Aplikasi web untuk meninjau dan mengevaluasi proposal akademik (PDF/DOCX) menggunakan AI (Groq/Llama 3.3 70B).

## ✨ Fitur

- 📄 **Upload Proposal**: Mendukung format PDF dan DOCX
- 🤖 **Evaluasi AI**: Analisis otomatis menggunakan Groq API (Llama 3.3 70B) - **GRATIS!**
- 📊 **Skor Terperinci**: Evaluasi 5 aspek proposal (Latar Belakang, Formulasi Masalah, Tujuan, Metodologi, Luaran)
- 💡 **Rekomendasi**: Daftar kekuatan, kelemahan, dan saran perbaikan
- 🎨 **UI Modern**: Desain akademis dengan glassmorphism dan dark mode

## 🛠️ Teknologi

- **Backend**: Python 3.10+, FastAPI
- **AI**: Groq API (Llama 3.3 70B Versatile)
- **Frontend**: HTML5, CSS3, JavaScript
- **Document Processing**: PyPDF, docx2txt

## 📦 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/username/ai-proposal-reviewer.git
cd ai-proposal-reviewer
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

Copy `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Edit `.env` (API key sudah tersedia di example):

```ini
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
GROQ_API_ENDPOINT=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
```

## 🚀 Menjalankan Aplikasi

### Mode Development

```bash
uvicorn app.utama:aplikasi --reload --port 8000
```

Aplikasi akan berjalan di `http://localhost:8000`

### Mode Production

```bash
uvicorn app.utama:aplikasi --workers 4 --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Type Checking dengan Pyright

```bash
python -m pyright
```

### Unit Tests

```bash
pytest pengujian/ -v
```

## 📁 Struktur Proyek

```
ai-proposal-reviewer/
├── app/
│   ├── __init__.py
│   ├── utama.py              # Entry point FastAPI
│   ├── konfigurasi.py        # Pengaturan aplikasi
│   ├── pengecualian.py       # Custom exceptions
│   ├── agen/
│   │   └── agen_peninjau.py  # Groq AI Agent
│   ├── layanan/
│   │   ├── pemuat_dokumen.py # PDF/DOCX loader
│   │   └── pemformat_keluaran.py
│   ├── skema/
│   │   └── model.py          # Pydantic models
│   ├── statis/
│   │   ├── css/
│   │   └── js/
│   └── templat/
│       └── indeks.html
├── pengujian/
│   └── uji_agen.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## 📝 API Endpoints

| Method | Endpoint         | Deskripsi       |
| ------ | ---------------- | --------------- |
| GET    | `/`              | Halaman utama   |
| POST   | `/api/review`    | Review proposal |
| GET    | `/api/kesehatan` | Health check    |

## 🎨 Panduan Warna

| Komponen        | Warna                                                        | Hex       |
| --------------- | ------------------------------------------------------------ | --------- |
| Primer (Navy)   | ![#1A365D](https://via.placeholder.com/15/1A365D/1A365D.png) | `#1A365D` |
| Sekunder (Emas) | ![#B7791F](https://via.placeholder.com/15/B7791F/B7791F.png) | `#B7791F` |
| Aksen (Biru)    | ![#3B82F6](https://via.placeholder.com/15/3B82F6/3B82F6.png) | `#3B82F6` |
| Sukses          | ![#38A169](https://via.placeholder.com/15/38A169/38A169.png) | `#38A169` |
| Error           | ![#E53E3E](https://via.placeholder.com/15/E53E3E/E53E3E.png) | `#E53E3E` |

## 📄 Lisensi

MIT License

## 👥 Kontributor

- AI Proposal Reviewer Team
