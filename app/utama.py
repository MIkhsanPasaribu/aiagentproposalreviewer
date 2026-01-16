"""
Entry point aplikasi FastAPI.

Modul utama yang menangani routing dan
endpoint API untuk review proposal.
"""

import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.konfigurasi import dapatkan_pengaturan
from app.layanan.pemuat_dokumen import PemuatDokumen
from app.layanan.database_riwayat import DatabaseRiwayat
from app.pengecualian import (
    BatasUkuranTerlampaui,
    DokumenTidakValid,
    FormatTidakDidukung,
    GagalMemproses,
)
from app.skema.model import HasilEvaluasi, JenisProposal, ResponReview

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
pencatat = logging.getLogger(__name__)

# Inisialisasi aplikasi
aplikasi = FastAPI(
    title="AI Proposal Reviewer",
    description="API untuk meninjau proposal akademik menggunakan AI (Groq/Llama 3.3)",
    version="1.0.0"
)

# Dapatkan direktori aplikasi
DIREKTORI_APP = Path(__file__).parent

# Setup static files & templates
aplikasi.mount(
    "/statis",
    StaticFiles(directory=str(DIREKTORI_APP / "statis")),
    name="statis"
)
templat = Jinja2Templates(directory=str(DIREKTORI_APP / "templat"))

# Inisialisasi layanan
pengaturan = dapatkan_pengaturan()

# Validasi konfigurasi saat startup
@aplikasi.on_event("startup")
async def validasi_konfigurasi():
    """Validasi konfigurasi saat aplikasi startup."""
    pencatat.info("Memulai validasi konfigurasi...")
    
    if not pengaturan.groq_api_key:
        pencatat.error("GROQ_API_KEY tidak ditemukan di environment variables!")
        raise RuntimeError("GROQ_API_KEY harus diset di file .env")
    
    if not pengaturan.groq_api_key.startswith("gsk_"):
        pencatat.warning("GROQ_API_KEY tidak memiliki format yang benar")
    
    pencatat.info(f"API Endpoint: {pengaturan.groq_api_endpoint}")
    pencatat.info(f"Model: {pengaturan.groq_model}")
    pencatat.info(f"Max file size: {pengaturan.ukuran_maks_berkas_mb} MB")
    pencatat.info("Konfigurasi valid ✓")

pemuat_dokumen = PemuatDokumen(ukuran_maks_mb=pengaturan.ukuran_maks_berkas_mb)
database_riwayat = DatabaseRiwayat()


@aplikasi.get("/", response_class=HTMLResponse)
async def halaman_utama(request: Request) -> HTMLResponse:
    """
    Menampilkan halaman utama aplikasi.

    Parameter:
        request: Objek Request FastAPI

    Mengembalikan:
        HTMLResponse berisi halaman utama
    """
    return templat.TemplateResponse(
        request=request,
        name="indeks.html",
        context={"request": request}
    )


@aplikasi.post("/api/review", response_model=ResponReview)
async def review_proposal(
    berkas: UploadFile = File(..., description="File proposal (PDF/DOCX)"),
    jenis_proposal: JenisProposal = Form(..., description="Jenis proposal")
) -> ResponReview:
    """
    Endpoint untuk melakukan review proposal.

    Parameter:
        berkas: File proposal yang akan direview
        jenis_proposal: Jenis proposal (pkm/skripsi/hibah)

    Mengembalikan:
        ResponReview berisi hasil evaluasi
    """
    pencatat.info(f"Menerima permintaan review: {berkas.filename}")

    # Validasi filename
    if not berkas.filename:
        raise HTTPException(
            status_code=400,
            detail="Nama file tidak valid"
        )

    # Validasi tipe file
    ekstensi = Path(berkas.filename).suffix.lower()
    if ekstensi not in PemuatDokumen.EKSTENSI_DIDUKUNG:
        raise HTTPException(
            status_code=400,
            detail=f"Format file tidak didukung: {ekstensi}"
        )

    jalur_sementara: str | None = None

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

        # Cek apakah Groq API dikonfigurasi
        if not pengaturan.groq_api_key:
            # Mode demo tanpa AI
            pencatat.warning("Groq API tidak dikonfigurasi, menggunakan mode demo")
            hasil_demo = HasilEvaluasi(
                skor=75,
                daftar_kekuatan=[
                    "Latar belakang dijelaskan dengan baik",
                    "Tujuan penelitian jelas dan terukur"
                ],
                daftar_kelemahan=[
                    "Metodologi perlu diperjelas",
                    "Luaran belum spesifik"
                ],
                daftar_saran=[
                    "Tambahkan detail metodologi penelitian",
                    "Jelaskan target luaran secara kuantitatif"
                ],
                ringkasan="Proposal memiliki fundasi yang baik, namun "
                          "perlu penguatan pada aspek metodologi dan luaran."
            )
            return ResponReview(
                berhasil=True,
                pesan="Review berhasil (mode demo)",
                data=hasil_demo
            )

        # Inisialisasi agent dan lakukan review
        from app.agen.agen_peninjau import AgenPeninjauProposal

        agen = AgenPeninjauProposal(
            api_key=pengaturan.groq_api_key,
            api_endpoint=pengaturan.groq_api_endpoint,
            model=pengaturan.groq_model
        )
        hasil = await agen.tinjau(teks_proposal, jenis_proposal.value)

        # Format respons
        hasil_evaluasi = HasilEvaluasi(**hasil)
        
        # Simpan ke database riwayat
        try:
            ukuran_berkas = len(konten) if 'konten' in locals() else None
            review_id = database_riwayat.simpan_review(
                nama_berkas=berkas.filename,
                jenis_proposal=jenis_proposal.value,
                hasil=hasil_evaluasi,
                ukuran_berkas=ukuran_berkas
            )
            pencatat.info(f"Review disimpan dengan ID: {review_id}")
        except Exception as e:
            pencatat.warning(f"Gagal menyimpan riwayat: {str(e)}")
        
        return ResponReview(
            berhasil=True,
            pesan="Review berhasil dilakukan",
            data=hasil_evaluasi
        )

    except (FormatTidakDidukung, BatasUkuranTerlampaui, DokumenTidakValid) as e:
        pencatat.error(f"Kesalahan validasi: {e.pesan}")
        raise HTTPException(status_code=400, detail=e.pesan)
    except GagalMemproses as e:
        pencatat.error(f"Kesalahan pemrosesan: {e.pesan}")
        raise HTTPException(status_code=500, detail=e.pesan)
    except Exception as e:
        pencatat.error(f"Kesalahan internal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses proposal"
        )
    finally:
        # Bersihkan file sementara
        if jalur_sementara and os.path.exists(jalur_sementara):
            os.unlink(jalur_sementara)


@aplikasi.get("/api/kesehatan")
async def cek_kesehatan() -> dict[str, str]:
    """
    Endpoint untuk health check.

    Mengembalikan:
        Dict berisi status dan versi aplikasi
    """
    return {"status": "sehat", "versi": "1.0.0"}


# ============================================
# ENDPOINTS RIWAYAT REVIEW
# ============================================

@aplikasi.get("/api/riwayat")
async def ambil_riwayat(
    limit: int = 50,
    offset: int = 0
):
    """
    Endpoint untuk mengambil riwayat review.

    Parameter:
        limit: Jumlah maksimal record (default: 50)
        offset: Offset untuk pagination (default: 0)

    Mengembalikan:
        List riwayat review
    """
    try:
        riwayat = database_riwayat.ambil_semua_riwayat(limit, offset)
        total = database_riwayat.hitung_total_review()
        
        return {
            "berhasil": True,
            "data": riwayat,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        pencatat.error(f"Gagal mengambil riwayat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil riwayat review"
        )


@aplikasi.get("/api/riwayat/{review_id}")
async def ambil_review(review_id: int):
    """
    Endpoint untuk mengambil detail review berdasarkan ID.

    Parameter:
        review_id: ID review

    Mengembalikan:
        Detail review
    """
    try:
        review = database_riwayat.ambil_review_berdasarkan_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review tidak ditemukan"
            )
        
        return {
            "berhasil": True,
            "data": review
        }
    except HTTPException:
        raise
    except Exception as e:
        pencatat.error(f"Gagal mengambil review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil detail review"
        )


@aplikasi.delete("/api/riwayat/{review_id}")
async def hapus_review(review_id: int):
    """
    Endpoint untuk menghapus review berdasarkan ID.

    Parameter:
        review_id: ID review yang akan dihapus

    Mengembalikan:
        Status penghapusan
    """
    try:
        berhasil = database_riwayat.hapus_review(review_id)
        
        if not berhasil:
            raise HTTPException(
                status_code=404,
                detail="Review tidak ditemukan"
            )
        
        return {
            "berhasil": True,
            "pesan": "Review berhasil dihapus"
        }
    except HTTPException:
        raise
    except Exception as e:
        pencatat.error(f"Gagal menghapus review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Gagal menghapus review"
        )


@aplikasi.get("/api/statistik")
async def ambil_statistik():
    """
    Endpoint untuk mengambil statistik review.

    Mengembalikan:
        Statistik review
    """
    try:
        statistik = database_riwayat.ambil_statistik()
        return {
            "berhasil": True,
            "data": statistik
        }
    except Exception as e:
        pencatat.error(f"Gagal mengambil statistik: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil statistik"
        )


# ============================================
# ENDPOINTS PENGATURAN
# ============================================

@aplikasi.get("/api/pengaturan")
async def ambil_pengaturan():
    """
    Endpoint untuk mengambil konfigurasi aplikasi.

    Mengembalikan:
        Konfigurasi aplikasi (tanpa API key)
    """
    return {
        "berhasil": True,
        "data": {
            "model": pengaturan.groq_model,
            "endpoint": pengaturan.groq_api_endpoint,
            "ukuran_maks_mb": pengaturan.ukuran_maks_berkas_mb,
            "mode_debug": pengaturan.mode_debug,
            "api_key_tersedia": bool(pengaturan.groq_api_key)
        }
    }

