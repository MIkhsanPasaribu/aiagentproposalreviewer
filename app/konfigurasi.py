"""
Modul konfigurasi aplikasi.

Memuat pengaturan dari environment variables menggunakan Pydantic.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Pengaturan(BaseSettings):
    """Konfigurasi aplikasi dari environment variables."""

    # Pengaturan Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"

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
