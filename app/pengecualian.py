"""
Modul pengecualian kustom untuk aplikasi.

Berisi kelas-kelas exception yang digunakan
untuk menangani berbagai jenis kesalahan.
"""


class PengecualianDasar(Exception):
    """Kelas dasar untuk semua pengecualian kustom."""

    def __init__(self, pesan: str, kode: str | None = None):
        """
        Inisialisasi pengecualian dasar.

        Parameter:
            pesan: Pesan kesalahan
            kode: Kode kesalahan (opsional)
        """
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
