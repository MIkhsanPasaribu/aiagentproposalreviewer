"""
Modul model data untuk API.

Berisi definisi model Pydantic untuk validasi
dan serialisasi data request/response.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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


class DetailSkor(BaseModel):
    """Model untuk detail skor per aspek evaluasi."""

    latar_belakang: int = Field(
        ...,
        ge=0,
        le=20,
        description="Skor kejelasan latar belakang (0-20)"
    )
    formulasi_masalah: int = Field(
        ...,
        ge=0,
        le=20,
        description="Skor formulasi masalah (0-20)"
    )
    tujuan: int = Field(
        ...,
        ge=0,
        le=20,
        description="Skor tujuan penelitian (0-20)"
    )
    metodologi: int = Field(
        ...,
        ge=0,
        le=20,
        description="Skor metodologi (0-20)"
    )
    luaran: int = Field(
        ...,
        ge=0,
        le=20,
        description="Skor luaran yang diharapkan (0-20)"
    )


class HasilEvaluasi(BaseModel):
    """Model untuk hasil evaluasi proposal."""

    skor: int = Field(
        ...,
        ge=0,
        le=100,
        description="Skor total (0-100)"
    )
    detail_skor: Optional[DetailSkor] = Field(
        default=None,
        description="Detail skor per aspek"
    )
    daftar_kekuatan: list[str] = Field(
        default_factory=list,
        description="Daftar kekuatan proposal"
    )
    daftar_kelemahan: list[str] = Field(
        default_factory=list,
        description="Daftar kelemahan proposal"
    )
    daftar_saran: list[str] = Field(
        default_factory=list,
        description="Daftar saran perbaikan"
    )
    ringkasan: str = Field(
        ...,
        description="Ringkasan evaluasi"
    )


class ResponReview(BaseModel):
    """Model respons API untuk hasil review."""

    berhasil: bool = Field(
        ...,
        description="Status keberhasilan review"
    )
    pesan: str = Field(
        ...,
        description="Pesan hasil review"
    )
    data: Optional[HasilEvaluasi] = Field(
        default=None,
        description="Data hasil evaluasi"
    )
