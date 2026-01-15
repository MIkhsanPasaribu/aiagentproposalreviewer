# 📋 Panduan Copilot untuk AI Proposal Reviewer Agent

## 🎯 Deskripsi Proyek

Proyek ini adalah aplikasi web full-stack untuk menilai proposal akademik (PDF/DOCX) menggunakan AI Agent berbasis LangChain. Aplikasi memberikan review, skor, dan rekomendasi perbaikan secara otomatis.

---

## 🇮🇩 Aturan Bahasa Indonesia dalam Kode

### Penamaan Variabel & Fungsi

```python
# ✅ BENAR - Gunakan Bahasa Indonesia
teks_proposal = ""
skor_total = 0
daftar_kekuatan = []
daftar_kelemahan = []

def muat_dokumen(jalur_berkas: str):
    pass

def proses_proposal(teks: str, jenis: str):
    pass

def hitung_skor(hasil_evaluasi: dict):
    pass

# ❌ SALAH - Jangan gunakan Bahasa Inggris
proposal_text = ""
total_score = 0
strengths_list = []
```

### Penamaan Kelas

```python
# ✅ BENAR
class AgenPeninjauProposal:
    pass

class PemuatDokumen:
    pass

class PemformatKeluaran:
    pass

# ❌ SALAH
class ProposalReviewerAgent:
    pass
```

### Penamaan Konstanta

```python
# ✅ BENAR
SKOR_MAKSIMAL = 100
JENIS_PROPOSAL_PKM = "pkm"
JENIS_PROPOSAL_SKRIPSI = "skripsi"
JENIS_PROPOSAL_HIBAH = "hibah"
UKURAN_POTONGAN_TEKS = 2000

# ❌ SALAH
MAX_SCORE = 100
PROPOSAL_TYPE_PKM = "pkm"
```

### Komentar & Docstring

```python
def proses_proposal(teks_proposal: str, jenis_proposal: str) -> dict:
    """
    Memproses dan mengevaluasi proposal menggunakan AI Agent.

    Parameter:
        teks_proposal (str): Teks lengkap dari proposal yang akan dievaluasi
        jenis_proposal (str): Jenis proposal (pkm/skripsi/hibah)

    Mengembalikan:
        dict: Hasil evaluasi berisi skor, kekuatan, kelemahan, dan saran

    Pengecualian:
        ValueError: Jika jenis_proposal tidak valid
        FileNotFoundError: Jika berkas tidak ditemukan
    """
    pass
```

---

## 🏗️ Struktur Proyek

```
proposal-reviewer/
├── app/
│   ├── __init__.py
│   ├── utama.py                    # Entry point FastAPI
│   ├── konfigurasi.py              # Pengaturan aplikasi
│   ├── agen/
│   │   ├── __init__.py
│   │   └── agen_peninjau.py        # LangChain Agent utama
│   ├── layanan/
│   │   ├── __init__.py
│   │   ├── pemuat_dokumen.py       # Pemuat PDF/DOCX
│   │   └── pemformat_keluaran.py   # Formatter hasil
│   ├── skema/
│   │   ├── __init__.py
│   │   └── model.py                # Pydantic models
│   ├── templat/
│   │   └── indeks.html             # Halaman utama
│   └── statis/
│       ├── css/
│       └── js/
├── pengujian/
│   ├── __init__.py
│   └── uji_agen.py
├── persyaratan.txt
├── .env.contoh
└── README.md
```

---

## 🔧 Standar Kode & Best Practices

### 1. Import & Dependencies

```python
# Urutan import:
# 1. Pustaka standar Python
# 2. Pustaka pihak ketiga
# 3. Modul lokal

# ✅ BENAR
from typing import Optional, List
from pathlib import Path
import logging

from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from app.agen.agen_peninjau import AgenPeninjauProposal
from app.layanan.pemuat_dokumen import PemuatDokumen
```

### 2. Konfigurasi & Environment Variables

```python
# app/konfigurasi.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Pengaturan(BaseSettings):
    """Konfigurasi aplikasi dari environment variables."""

    # Pengaturan Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str
    azure_openai_api_version: str = "2024-02-15-preview"

    # Pengaturan Aplikasi
    ukuran_maks_berkas_mb: int = 10
    mode_debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def dapatkan_pengaturan() -> Pengaturan:
    """Mendapatkan instance pengaturan (cached)."""
    return Pengaturan()
```

### 3. Model Pydantic (Skema)

```python
# app/skema/model.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class JenisProposal(str, Enum):
    """Enum untuk jenis-jenis proposal yang didukung."""
    PKM = "pkm"
    SKRIPSI = "skripsi"
    HIBAH = "hibah"

class PermintaanReview(BaseModel):
    """Model untuk permintaan review proposal."""
    jenis_proposal: JenisProposal = Field(
        ...,
        description="Jenis proposal yang akan direview"
    )

class HasilEvaluasi(BaseModel):
    """Model untuk hasil evaluasi proposal."""
    skor: int = Field(..., ge=0, le=100, description="Skor total (0-100)")
    daftar_kekuatan: List[str] = Field(default_factory=list)
    daftar_kelemahan: List[str] = Field(default_factory=list)
    daftar_saran: List[str] = Field(default_factory=list)
    ringkasan: str = Field(..., description="Ringkasan evaluasi")

class ResponReview(BaseModel):
    """Model respons API untuk hasil review."""
    berhasil: bool
    pesan: str
    data: Optional[HasilEvaluasi] = None
```

### 4. LangChain Agent Implementation

```python
# app/agen/agen_peninjau.py
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from typing import Dict, Any
import logging

# Konfigurasi logging
pencatat = logging.getLogger(__name__)

class AgenPeninjauProposal:
    """
    Agent LangChain untuk meninjau dan mengevaluasi proposal akademik.

    Agent ini menggunakan structured reasoning untuk menilai:
    - Kejelasan latar belakang
    - Formulasi masalah
    - Tujuan penelitian
    - Metodologi
    - Luaran yang diharapkan
    """

    TEMPLAT_PROMPT = """
Anda adalah peninjau proposal akademik profesional.

Tinjau proposal {jenis_proposal} berikut ini.

Evaluasi aspek-aspek berikut:
1. Kejelasan latar belakang (0-20 poin)
2. Formulasi masalah (0-20 poin)
3. Tujuan penelitian (0-20 poin)
4. Metodologi (0-20 poin)
5. Luaran yang diharapkan (0-20 poin)

Berikan output dalam format JSON:
{{
    "skor": <total_skor>,
    "detail_skor": {{
        "latar_belakang": <skor>,
        "formulasi_masalah": <skor>,
        "tujuan": <skor>,
        "metodologi": <skor>,
        "luaran": <skor>
    }},
    "daftar_kekuatan": ["kekuatan 1", "kekuatan 2", ...],
    "daftar_kelemahan": ["kelemahan 1", "kelemahan 2", ...],
    "daftar_saran": ["saran 1", "saran 2", ...],
    "ringkasan": "ringkasan evaluasi secara keseluruhan"
}}

Proposal:
{teks_proposal}
"""

    def __init__(self, llm: AzureChatOpenAI):
        """
        Inisialisasi agent peninjau proposal.

        Parameter:
            llm: Instance Azure OpenAI LLM
        """
        self._llm = llm
        self._prompt = PromptTemplate(
            input_variables=["teks_proposal", "jenis_proposal"],
            template=self.TEMPLAT_PROMPT
        )
        self._rantai = LLMChain(llm=self._llm, prompt=self._prompt)
        pencatat.info("AgenPeninjauProposal berhasil diinisialisasi")

    async def tinjau(
        self,
        teks_proposal: str,
        jenis_proposal: str
    ) -> Dict[str, Any]:
        """
        Meninjau proposal dan menghasilkan evaluasi terstruktur.

        Parameter:
            teks_proposal: Teks lengkap proposal
            jenis_proposal: Jenis proposal (pkm/skripsi/hibah)

        Mengembalikan:
            Dict berisi hasil evaluasi
        """
        pencatat.info(f"Memulai review proposal jenis: {jenis_proposal}")

        try:
            hasil = await self._rantai.arun({
                "teks_proposal": teks_proposal,
                "jenis_proposal": jenis_proposal
            })
            pencatat.info("Review proposal selesai")
            return self._parse_hasil(hasil)
        except Exception as e:
            pencatat.error(f"Gagal melakukan review: {str(e)}")
            raise

    def _parse_hasil(self, hasil_mentah: str) -> Dict[str, Any]:
        """Mengurai hasil mentah dari LLM menjadi dictionary."""
        import json
        try:
            return json.loads(hasil_mentah)
        except json.JSONDecodeError as e:
            pencatat.warning(f"Gagal parse JSON, mencoba ekstraksi manual: {e}")
            # Implementasi fallback parsing jika diperlukan
            raise ValueError("Format respons tidak valid")
```

### 5. Service Layer (Pemuat Dokumen)

```python
# app/layanan/pemuat_dokumen.py
from pathlib import Path
from typing import Union
import logging

from langchain_community.document_loaders import PyPDFLoader
from docx2txt import process as proses_docx

pencatat = logging.getLogger(__name__)

class PemuatDokumen:
    """
    Layanan untuk memuat dan mengekstrak teks dari dokumen.

    Mendukung format:
    - PDF (.pdf)
    - Microsoft Word (.docx)
    """

    EKSTENSI_DIDUKUNG = {".pdf", ".docx"}

    def __init__(self, ukuran_maks_mb: int = 10):
        """
        Inisialisasi pemuat dokumen.

        Parameter:
            ukuran_maks_mb: Ukuran maksimal file dalam MB
        """
        self._ukuran_maks_byte = ukuran_maks_mb * 1024 * 1024

    async def muat(self, jalur_berkas: Union[str, Path]) -> str:
        """
        Memuat dokumen dan mengekstrak teksnya.

        Parameter:
            jalur_berkas: Path ke file dokumen

        Mengembalikan:
            String berisi teks yang diekstrak

        Pengecualian:
            ValueError: Jika format file tidak didukung
            FileNotFoundError: Jika file tidak ditemukan
        """
        jalur = Path(jalur_berkas)

        # Validasi keberadaan file
        if not jalur.exists():
            raise FileNotFoundError(f"Berkas tidak ditemukan: {jalur}")

        # Validasi ekstensi
        if jalur.suffix.lower() not in self.EKSTENSI_DIDUKUNG:
            raise ValueError(
                f"Format tidak didukung: {jalur.suffix}. "
                f"Format yang didukung: {self.EKSTENSI_DIDUKUNG}"
            )

        # Validasi ukuran
        ukuran_berkas = jalur.stat().st_size
        if ukuran_berkas > self._ukuran_maks_byte:
            raise ValueError(
                f"Ukuran berkas ({ukuran_berkas / 1024 / 1024:.2f} MB) "
                f"melebihi batas maksimal ({self._ukuran_maks_byte / 1024 / 1024} MB)"
            )

        pencatat.info(f"Memuat dokumen: {jalur.name}")

        if jalur.suffix.lower() == ".pdf":
            return await self._muat_pdf(jalur)
        else:
            return await self._muat_docx(jalur)

    async def _muat_pdf(self, jalur: Path) -> str:
        """Mengekstrak teks dari file PDF."""
        pemuat = PyPDFLoader(str(jalur))
        dokumen = pemuat.load()
        teks_gabungan = "\n\n".join([dok.page_content for dok in dokumen])
        pencatat.info(f"Berhasil memuat PDF: {len(teks_gabungan)} karakter")
        return teks_gabungan

    async def _muat_docx(self, jalur: Path) -> str:
        """Mengekstrak teks dari file DOCX."""
        teks = proses_docx(str(jalur))
        pencatat.info(f"Berhasil memuat DOCX: {len(teks)} karakter")
        return teks
```

### 6. FastAPI Endpoints

```python
# app/utama.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from pathlib import Path
import tempfile
import logging

from app.konfigurasi import dapatkan_pengaturan
from app.agen.agen_peninjau import AgenPeninjauProposal
from app.layanan.pemuat_dokumen import PemuatDokumen
from app.skema.model import JenisProposal, ResponReview, HasilEvaluasi

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
pencatat = logging.getLogger(__name__)

# Inisialisasi aplikasi
aplikasi = FastAPI(
    title="AI Proposal Reviewer",
    description="API untuk meninjau proposal akademik menggunakan AI",
    version="1.0.0"
)

# Setup static files & templates
aplikasi.mount(
    "/statis",
    StaticFiles(directory="app/statis"),
    name="statis"
)
templat = Jinja2Templates(directory="app/templat")

# Inisialisasi layanan
pengaturan = dapatkan_pengaturan()
pemuat_dokumen = PemuatDokumen(ukuran_maks_mb=pengaturan.ukuran_maks_berkas_mb)

@aplikasi.get("/")
async def halaman_utama(request: Request):
    """Menampilkan halaman utama aplikasi."""
    return templat.TemplateResponse(
        "indeks.html",
        {"request": request}
    )

@aplikasi.post("/api/review", response_model=ResponReview)
async def review_proposal(
    berkas: UploadFile = File(..., description="File proposal (PDF/DOCX)"),
    jenis_proposal: JenisProposal = Form(..., description="Jenis proposal")
):
    """
    Endpoint untuk melakukan review proposal.

    Parameter:
        berkas: File proposal yang akan direview
        jenis_proposal: Jenis proposal (pkm/skripsi/hibah)

    Mengembalikan:
        ResponReview berisi hasil evaluasi
    """
    pencatat.info(f"Menerima permintaan review: {berkas.filename}")

    # Validasi tipe file
    ekstensi = Path(berkas.filename).suffix.lower()
    if ekstensi not in PemuatDokumen.EKSTENSI_DIDUKUNG:
        raise HTTPException(
            status_code=400,
            detail=f"Format file tidak didukung: {ekstensi}"
        )

    try:
        # Simpan file sementara
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=ekstensi
        ) as berkas_sementara:
            konten = await berkas.read()
            berkas_sementara.write(konten)
            jalur_sementara = berkas_sementara.name

        # Muat dan proses dokumen
        teks_proposal = await pemuat_dokumen.muat(jalur_sementara)

        # Inisialisasi agent dan lakukan review
        from langchain_openai import AzureChatOpenAI

        llm = AzureChatOpenAI(
            azure_endpoint=pengaturan.azure_openai_endpoint,
            api_key=pengaturan.azure_openai_api_key,
            azure_deployment=pengaturan.azure_openai_deployment,
            api_version=pengaturan.azure_openai_api_version
        )

        agen = AgenPeninjauProposal(llm)
        hasil = await agen.tinjau(teks_proposal, jenis_proposal.value)

        # Format respons
        return ResponReview(
            berhasil=True,
            pesan="Review berhasil dilakukan",
            data=HasilEvaluasi(**hasil)
        )

    except ValueError as e:
        pencatat.error(f"Kesalahan validasi: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        pencatat.error(f"Kesalahan internal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses proposal"
        )
    finally:
        # Bersihkan file sementara
        import os
        if 'jalur_sementara' in locals():
            os.unlink(jalur_sementara)

@aplikasi.get("/api/kesehatan")
async def cek_kesehatan():
    """Endpoint untuk health check."""
    return {"status": "sehat", "versi": "1.0.0"}
```

---

## 🧪 Standar Pengujian

```python
# pengujian/uji_agen.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.agen.agen_peninjau import AgenPeninjauProposal
from app.layanan.pemuat_dokumen import PemuatDokumen

class TestAgenPeninjauProposal:
    """Kelas pengujian untuk AgenPeninjauProposal."""

    @pytest.fixture
    def mock_llm(self):
        """Fixture untuk mock LLM."""
        return Mock()

    @pytest.fixture
    def agen(self, mock_llm):
        """Fixture untuk instance agent."""
        return AgenPeninjauProposal(mock_llm)

    @pytest.mark.asyncio
    async def test_tinjau_proposal_pkm_berhasil(self, agen):
        """Menguji review proposal PKM berhasil."""
        # Arrange
        teks_contoh = "Ini adalah proposal PKM..."
        jenis = "pkm"

        # Act & Assert
        # Implementasi pengujian
        pass

    @pytest.mark.asyncio
    async def test_tinjau_proposal_gagal_teks_kosong(self, agen):
        """Menguji error handling untuk teks kosong."""
        with pytest.raises(ValueError):
            await agen.tinjau("", "pkm")


class TestPemuatDokumen:
    """Kelas pengujian untuk PemuatDokumen."""

    @pytest.fixture
    def pemuat(self):
        """Fixture untuk instance pemuat."""
        return PemuatDokumen()

    @pytest.mark.asyncio
    async def test_muat_pdf_berhasil(self, pemuat, tmp_path):
        """Menguji pemuatan file PDF berhasil."""
        pass

    @pytest.mark.asyncio
    async def test_muat_ekstensi_tidak_didukung(self, pemuat, tmp_path):
        """Menguji error untuk ekstensi tidak didukung."""
        berkas_uji = tmp_path / "dokumen.txt"
        berkas_uji.write_text("konten")

        with pytest.raises(ValueError, match="Format tidak didukung"):
            await pemuat.muat(berkas_uji)
```

---

## 📝 Penanganan Error

```python
# app/pengecualian.py
class PengecualianDasar(Exception):
    """Kelas dasar untuk semua pengecualian kustom."""

    def __init__(self, pesan: str, kode: str = None):
        self.pesan = pesan
        self.kode = kode
        super().__init__(self.pesan)


class DokumenTidakValid(PengecualianDasar):
    """Pengecualian untuk dokumen yang tidak valid."""
    pass


class FormatTidakDidukung(PengecualianDasar):
    """Pengecualian untuk format file yang tidak didukung."""
    pass


class GagalMemproses(PengecualianDasar):
    """Pengecualian untuk kegagalan pemrosesan."""
    pass


class BatasUkuranTerlampaui(PengecualianDasar):
    """Pengecualian untuk file yang melebihi batas ukuran."""
    pass
```

---

## 🔒 Keamanan & Validasi

### Validasi Input

```python
from pydantic import validator, field_validator

class PermintaanReview(BaseModel):
    jenis_proposal: JenisProposal

    @field_validator("jenis_proposal")
    @classmethod
    def validasi_jenis(cls, nilai):
        """Memvalidasi jenis proposal."""
        if nilai not in JenisProposal:
            raise ValueError(f"Jenis proposal tidak valid: {nilai}")
        return nilai
```

### Sanitasi File Upload

```python
TIPE_MIME_DIIZINKAN = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

async def validasi_berkas(berkas: UploadFile) -> bool:
    """Memvalidasi file yang diupload."""
    # Cek tipe MIME
    if berkas.content_type not in TIPE_MIME_DIIZINKAN:
        raise ValueError(f"Tipe file tidak diizinkan: {berkas.content_type}")

    # Cek ukuran
    konten = await berkas.read()
    await berkas.seek(0)  # Reset posisi baca

    if len(konten) > UKURAN_MAKS_BYTE:
        raise ValueError("Ukuran file melebihi batas")

    return True
```

---

## 📦 Dependencies (persyaratan.txt)

```
# Framework Web
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
jinja2>=3.1.2

# LangChain & AI
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20

# Pemrosesan Dokumen
pypdf>=3.17.0
docx2txt>=0.8

# Validasi & Konfigurasi
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Pengujian
pytest>=7.4.0
pytest-asyncio>=0.23.0

# Utilitas
python-dotenv>=1.0.0
```

---

## 🚀 Perintah Menjalankan

```bash
# Development
uvicorn app.utama:aplikasi --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.utama:aplikasi --workers 4 --host 0.0.0.0 --port 8000
```

---

## ✅ Checklist Code Review

Sebelum commit, pastikan:

- [ ] Semua nama variabel, fungsi, kelas dalam Bahasa Indonesia
- [ ] Semua komentar dan docstring dalam Bahasa Indonesia
- [ ] Tipe data (type hints) lengkap
- [ ] Error handling yang proper
- [ ] Logging yang informatif
- [ ] Unit test untuk fungsi baru
- [ ] Tidak ada hardcoded secrets
- [ ] Validasi input yang ketat

---

## 🎨 Konvensi Penamaan Ringkas

| Jenis     | Konvensi              | Contoh                                  |
| --------- | --------------------- | --------------------------------------- |
| Variabel  | snake_case Indonesia  | `teks_proposal`, `skor_total`           |
| Fungsi    | snake_case Indonesia  | `muat_dokumen()`, `hitung_skor()`       |
| Kelas     | PascalCase Indonesia  | `AgenPeninjau`, `PemuatDokumen`         |
| Konstanta | UPPER_SNAKE Indonesia | `SKOR_MAKSIMAL`, `JENIS_PKM`            |
| File      | snake_case Indonesia  | `agen_peninjau.py`, `pemuat_dokumen.py` |
| Folder    | lowercase Indonesia   | `layanan/`, `templat/`, `pengujian/`    |
