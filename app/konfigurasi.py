"""
Modul konfigurasi aplikasi.

Memuat pengaturan dari environment variables menggunakan Pydantic.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Pengaturan(BaseSettings):
    """Konfigurasi aplikasi dari environment variables."""

    # Pengaturan Groq API
    groq_api_key: str = ""
    groq_api_endpoint: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_model: str = "llama-3.3-70b-versatile"

    # Pengaturan Aplikasi
    ukuran_maks_berkas_mb: int = 10
    mode_debug: bool = False

    class Config:
        """Konfigurasi untuk Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def dapatkan_pengaturan() -> Pengaturan:
    """
    Mendapatkan instance pengaturan (cached).

    Mengembalikan:
        Pengaturan: Instance konfigurasi aplikasi
    """
    return Pengaturan()
