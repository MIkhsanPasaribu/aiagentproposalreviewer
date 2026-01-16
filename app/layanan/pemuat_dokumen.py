"""
Modul pemuat dokumen untuk mengekstrak teks dari file.

Mendukung format PDF dan DOCX.
"""

import logging
from pathlib import Path
from typing import Union

from app.pengecualian import (
    BatasUkuranTerlampaui,
    DokumenTidakValid,
    FormatTidakDidukung,
)

pencatat = logging.getLogger(__name__)


class PemuatDokumen:
    """
    Layanan untuk memuat dan mengekstrak teks dari dokumen.

    Mendukung format:
    - PDF (.pdf)
    - Microsoft Word (.docx)
    """

    EKSTENSI_DIDUKUNG: set[str] = {".pdf", ".docx"}

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
            FormatTidakDidukung: Jika format file tidak didukung
            DokumenTidakValid: Jika file tidak ditemukan
            BatasUkuranTerlampaui: Jika ukuran file melebihi batas
        """
        jalur = Path(jalur_berkas)

        # Validasi keberadaan file
        if not jalur.exists():
            raise DokumenTidakValid(
                pesan=f"Berkas tidak ditemukan: {jalur}",
                kode="BERKAS_TIDAK_DITEMUKAN"
            )

        # Validasi ekstensi
        if jalur.suffix.lower() not in self.EKSTENSI_DIDUKUNG:
            raise FormatTidakDidukung(
                pesan=f"Format tidak didukung: {jalur.suffix}. "
                      f"Format yang didukung: {self.EKSTENSI_DIDUKUNG}",
                kode="FORMAT_TIDAK_DIDUKUNG"
            )

        # Validasi ukuran
        ukuran_berkas = jalur.stat().st_size
        if ukuran_berkas > self._ukuran_maks_byte:
            raise BatasUkuranTerlampaui(
                pesan=f"Ukuran berkas ({ukuran_berkas / 1024 / 1024:.2f} MB) "
                      f"melebihi batas maksimal "
                      f"({self._ukuran_maks_byte / 1024 / 1024} MB)",
                kode="UKURAN_TERLAMPAUI"
            )

        pencatat.info(f"Memuat dokumen: {jalur.name}")

        if jalur.suffix.lower() == ".pdf":
            return await self._muat_pdf(jalur)
        else:
            return await self._muat_docx(jalur)

    async def _muat_pdf(self, jalur: Path) -> str:
        """
        Mengekstrak teks dari file PDF.

        Parameter:
            jalur: Path ke file PDF

        Mengembalikan:
            String berisi teks yang diekstrak
        """
        from pypdf import PdfReader

        try:
            pembaca = PdfReader(str(jalur))
            teks_halaman = []
            
            for halaman in pembaca.pages:
                teks = halaman.extract_text()
                if teks:
                    teks_halaman.append(teks)
            
            teks_gabungan = "\n\n".join(teks_halaman)
            pencatat.info(f"Berhasil memuat PDF: {len(teks_gabungan)} karakter dari {len(pembaca.pages)} halaman")
            return teks_gabungan
        except Exception as e:
            pencatat.error(f"Gagal memuat PDF: {str(e)}")
            raise DokumenTidakValid(
                pesan=f"Gagal membaca file PDF: {str(e)}",
                kode="PDF_TIDAK_VALID"
            )

    async def _muat_docx(self, jalur: Path) -> str:
        """
        Mengekstrak teks dari file DOCX.

        Parameter:
            jalur: Path ke file DOCX

        Mengembalikan:
            String berisi teks yang diekstrak
        """
        import docx2txt

        try:
            teks = docx2txt.process(str(jalur))
            pencatat.info(f"Berhasil memuat DOCX: {len(teks)} karakter")
            return teks
        except Exception as e:
            pencatat.error(f"Gagal memuat DOCX: {str(e)}")
            raise DokumenTidakValid(
                pesan=f"Gagal membaca file DOCX: {str(e)}",
                kode="DOCX_TIDAK_VALID"
            )
