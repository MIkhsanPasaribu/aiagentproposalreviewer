"""
Paket skema untuk model data aplikasi.

Berisi definisi model Pydantic untuk validasi
data input dan output API.
"""

from app.skema.model import (
    HasilEvaluasi,
    JenisProposal,
    PermintaanReview,
    ResponReview,
)

__all__ = [
    "JenisProposal",
    "PermintaanReview",
    "HasilEvaluasi",
    "ResponReview",
]
