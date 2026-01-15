"""
Modul pengujian untuk AgenPeninjauProposal dan PemuatDokumen.

Berisi unit tests untuk memastikan fungsionalitas
agent dan layanan pemuat dokumen.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.layanan.pemuat_dokumen import PemuatDokumen
from app.pengecualian import (
    BatasUkuranTerlampaui,
    DokumenTidakValid,
    FormatTidakDidukung,
)


class TestPemuatDokumen:
    """Kelas pengujian untuk PemuatDokumen."""

    @pytest.fixture
    def pemuat(self) -> PemuatDokumen:
        """Fixture untuk instance pemuat."""
        return PemuatDokumen(ukuran_maks_mb=10)

    @pytest.mark.asyncio
    async def test_muat_berkas_tidak_ditemukan(
        self,
        pemuat: PemuatDokumen
    ) -> None:
        """Menguji error untuk file tidak ditemukan."""
        jalur_tidak_ada = Path("/path/yang/tidak/ada.pdf")

        with pytest.raises(DokumenTidakValid) as exc_info:
            await pemuat.muat(jalur_tidak_ada)

        assert "tidak ditemukan" in exc_info.value.pesan.lower()

    @pytest.mark.asyncio
    async def test_muat_format_tidak_didukung(
        self,
        pemuat: PemuatDokumen,
        tmp_path: Path
    ) -> None:
        """Menguji error untuk format file tidak didukung."""
        berkas_txt = tmp_path / "dokumen.txt"
        berkas_txt.write_text("konten teks biasa")

        with pytest.raises(FormatTidakDidukung) as exc_info:
            await pemuat.muat(berkas_txt)

        assert "tidak didukung" in exc_info.value.pesan.lower()

    @pytest.mark.asyncio
    async def test_muat_ukuran_terlampaui(
        self,
        tmp_path: Path
    ) -> None:
        """Menguji error untuk file yang melebihi batas ukuran."""
        pemuat = PemuatDokumen(ukuran_maks_mb=0)  # Batas 0 MB
        berkas_pdf = tmp_path / "dokumen.pdf"
        berkas_pdf.write_bytes(b"konten pdf")

        with pytest.raises(BatasUkuranTerlampaui) as exc_info:
            await pemuat.muat(berkas_pdf)

        assert "melebihi" in exc_info.value.pesan.lower()

    def test_ekstensi_didukung(self, pemuat: PemuatDokumen) -> None:
        """Menguji ekstensi yang didukung."""
        ekstensi_didukung = pemuat.EKSTENSI_DIDUKUNG

        assert ".pdf" in ekstensi_didukung
        assert ".docx" in ekstensi_didukung
        assert len(ekstensi_didukung) == 2


class TestAgenPeninjauProposal:
    """Kelas pengujian untuk AgenPeninjauProposal."""

    @pytest.fixture
    def agen(self) -> "AgenPeninjauProposal":  # type: ignore[name-defined]
        """Fixture untuk instance agent dengan API key dummy."""
        from app.agen.agen_peninjau import AgenPeninjauProposal
        return AgenPeninjauProposal(api_key="dummy-key")

    @pytest.mark.asyncio
    async def test_tinjau_teks_kosong(self) -> None:
        """Menguji error untuk teks proposal kosong."""
        from app.agen.agen_peninjau import AgenPeninjauProposal

        agen = AgenPeninjauProposal(api_key="dummy-key")

        with pytest.raises(ValueError) as exc_info:
            await agen.tinjau("", "pkm")

        assert "kosong" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tinjau_teks_whitespace(self) -> None:
        """Menguji error untuk teks proposal hanya whitespace."""
        from app.agen.agen_peninjau import AgenPeninjauProposal

        agen = AgenPeninjauProposal(api_key="dummy-key")

        with pytest.raises(ValueError):
            await agen.tinjau("   \n\t  ", "pkm")


class TestSkemaModel:
    """Kelas pengujian untuk model skema."""

    def test_jenis_proposal_valid(self) -> None:
        """Menguji enum JenisProposal."""
        from app.skema.model import JenisProposal

        assert JenisProposal.PKM.value == "pkm"
        assert JenisProposal.SKRIPSI.value == "skripsi"
        assert JenisProposal.HIBAH.value == "hibah"

    def test_hasil_evaluasi_skor_valid(self) -> None:
        """Menguji validasi skor HasilEvaluasi."""
        from app.skema.model import HasilEvaluasi

        hasil = HasilEvaluasi(
            skor=75,
            daftar_kekuatan=["Kekuatan 1"],
            daftar_kelemahan=["Kelemahan 1"],
            daftar_saran=["Saran 1"],
            ringkasan="Ringkasan proposal"
        )

        assert hasil.skor == 75
        assert len(hasil.daftar_kekuatan) == 1

    def test_hasil_evaluasi_skor_invalid(self) -> None:
        """Menguji validasi skor yang tidak valid."""
        from pydantic import ValidationError

        from app.skema.model import HasilEvaluasi

        with pytest.raises(ValidationError):
            HasilEvaluasi(
                skor=150,  # Melebihi 100
                daftar_kekuatan=[],
                daftar_kelemahan=[],
                daftar_saran=[],
                ringkasan="Ringkasan"
            )

    def test_respon_review(self) -> None:
        """Menguji model ResponReview."""
        from app.skema.model import HasilEvaluasi, ResponReview

        hasil = HasilEvaluasi(
            skor=80,
            daftar_kekuatan=[],
            daftar_kelemahan=[],
            daftar_saran=[],
            ringkasan="Ringkasan"
        )

        respon = ResponReview(
            berhasil=True,
            pesan="Review berhasil",
            data=hasil
        )

        assert respon.berhasil is True
        assert respon.data is not None
        assert respon.data.skor == 80
