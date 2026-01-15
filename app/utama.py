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
    description="API untuk meninjau proposal akademik menggunakan AI Agent",
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
pemuat_dokumen = PemuatDokumen(ukuran_maks_mb=pengaturan.ukuran_maks_berkas_mb)


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

        # Cek apakah Azure OpenAI dikonfigurasi
        if not pengaturan.azure_openai_endpoint or not pengaturan.azure_openai_api_key:
            # Mode demo tanpa AI
            pencatat.warning("Azure OpenAI tidak dikonfigurasi, menggunakan mode demo")
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
        from pydantic import SecretStr

        from langchain_openai import AzureChatOpenAI

        from app.agen.agen_peninjau import AgenPeninjauProposal

        llm = AzureChatOpenAI(
            azure_endpoint=pengaturan.azure_openai_endpoint,
            api_key=SecretStr(pengaturan.azure_openai_api_key),
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
