"""
Modul database untuk menyimpan riwayat review.

Menggunakan SQLite untuk penyimpanan lokal.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.skema.model import HasilEvaluasi, JenisProposal

pencatat = logging.getLogger(__name__)


class DatabaseRiwayat:
    """Database untuk menyimpan riwayat review proposal."""

    def __init__(self, jalur_db: str = "data/riwayat_review.db"):
        """
        Inisialisasi database.

        Parameter:
            jalur_db: Path ke file database SQLite
        """
        # Pastikan direktori data ada
        Path(jalur_db).parent.mkdir(parents=True, exist_ok=True)
        
        self.jalur_db = jalur_db
        self._buat_tabel()
        pencatat.info(f"Database riwayat diinisialisasi: {jalur_db}")

    def _buat_tabel(self):
        """Membuat tabel jika belum ada."""
        with sqlite3.connect(self.jalur_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS riwayat_review (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_berkas TEXT NOT NULL,
                    jenis_proposal TEXT NOT NULL,
                    skor INTEGER NOT NULL,
                    detail_skor TEXT NOT NULL,
                    daftar_kekuatan TEXT NOT NULL,
                    daftar_kelemahan TEXT NOT NULL,
                    daftar_saran TEXT NOT NULL,
                    ringkasan TEXT NOT NULL,
                    tanggal_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ukuran_berkas INTEGER
                )
            """)
            conn.commit()
            pencatat.info("Tabel riwayat_review siap")

    def simpan_review(
        self,
        nama_berkas: str,
        jenis_proposal: str,
        hasil: HasilEvaluasi,
        ukuran_berkas: Optional[int] = None
    ) -> int:
        """
        Menyimpan hasil review ke database.

        Parameter:
            nama_berkas: Nama file proposal
            jenis_proposal: Jenis proposal (pkm/skripsi/hibah)
            hasil: Hasil evaluasi
            ukuran_berkas: Ukuran file dalam bytes

        Mengembalikan:
            ID review yang baru disimpan
        """
        with sqlite3.connect(self.jalur_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO riwayat_review (
                    nama_berkas,
                    jenis_proposal,
                    skor,
                    detail_skor,
                    daftar_kekuatan,
                    daftar_kelemahan,
                    daftar_saran,
                    ringkasan,
                    ukuran_berkas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nama_berkas,
                jenis_proposal,
                hasil.skor,
                json.dumps(hasil.detail_skor if hasattr(hasil, 'detail_skor') else {}),
                json.dumps(hasil.daftar_kekuatan),
                json.dumps(hasil.daftar_kelemahan),
                json.dumps(hasil.daftar_saran),
                hasil.ringkasan,
                ukuran_berkas
            ))
            conn.commit()
            review_id = cursor.lastrowid
            pencatat.info(f"Review disimpan dengan ID: {review_id}")
            return review_id # pyright: ignore[reportReturnType]

    def ambil_semua_riwayat(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Mengambil semua riwayat review.

        Parameter:
            limit: Jumlah maksimal record
            offset: Offset untuk pagination

        Mengembalikan:
            List dictionary berisi riwayat review
        """
        with sqlite3.connect(self.jalur_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM riwayat_review
                ORDER BY tanggal_review DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            hasil = []
            for row in cursor.fetchall():
                hasil.append({
                    "id": row["id"],
                    "nama_berkas": row["nama_berkas"],
                    "jenis_proposal": row["jenis_proposal"],
                    "skor": row["skor"],
                    "detail_skor": json.loads(row["detail_skor"]),
                    "daftar_kekuatan": json.loads(row["daftar_kekuatan"]),
                    "daftar_kelemahan": json.loads(row["daftar_kelemahan"]),
                    "daftar_saran": json.loads(row["daftar_saran"]),
                    "ringkasan": row["ringkasan"],
                    "tanggal_review": row["tanggal_review"],
                    "ukuran_berkas": row["ukuran_berkas"]
                })
            
            return hasil

    def ambil_review_berdasarkan_id(self, review_id: int) -> Optional[dict]:
        """
        Mengambil review berdasarkan ID.

        Parameter:
            review_id: ID review

        Mengembalikan:
            Dictionary berisi data review atau None
        """
        with sqlite3.connect(self.jalur_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM riwayat_review WHERE id = ?
            """, (review_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "nama_berkas": row["nama_berkas"],
                    "jenis_proposal": row["jenis_proposal"],
                    "skor": row["skor"],
                    "detail_skor": json.loads(row["detail_skor"]),
                    "daftar_kekuatan": json.loads(row["daftar_kekuatan"]),
                    "daftar_kelemahan": json.loads(row["daftar_kelemahan"]),
                    "daftar_saran": json.loads(row["daftar_saran"]),
                    "ringkasan": row["ringkasan"],
                    "tanggal_review": row["tanggal_review"],
                    "ukuran_berkas": row["ukuran_berkas"]
                }
            return None

    def hapus_review(self, review_id: int) -> bool:
        """
        Menghapus review berdasarkan ID.

        Parameter:
            review_id: ID review yang akan dihapus

        Mengembalikan:
            True jika berhasil dihapus
        """
        with sqlite3.connect(self.jalur_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM riwayat_review WHERE id = ?
            """, (review_id,))
            conn.commit()
            berhasil = cursor.rowcount > 0
            if berhasil:
                pencatat.info(f"Review ID {review_id} berhasil dihapus")
            return berhasil

    def hitung_total_review(self) -> int:
        """
        Menghitung total jumlah review.

        Mengembalikan:
            Jumlah total review
        """
        with sqlite3.connect(self.jalur_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM riwayat_review")
            return cursor.fetchone()[0]

    def ambil_statistik(self) -> dict:
        """
        Mengambil statistik review.

        Mengembalikan:
            Dictionary berisi statistik
        """
        with sqlite3.connect(self.jalur_db) as conn:
            cursor = conn.cursor()
            
            # Total review
            cursor.execute("SELECT COUNT(*) FROM riwayat_review")
            total = cursor.fetchone()[0]
            
            # Rata-rata skor
            cursor.execute("SELECT AVG(skor) FROM riwayat_review")
            rata_rata = cursor.fetchone()[0] or 0
            
            # Skor tertinggi
            cursor.execute("SELECT MAX(skor) FROM riwayat_review")
            tertinggi = cursor.fetchone()[0] or 0
            
            # Skor terendah
            cursor.execute("SELECT MIN(skor) FROM riwayat_review")
            terendah = cursor.fetchone()[0] or 0
            
            # Review per jenis
            cursor.execute("""
                SELECT jenis_proposal, COUNT(*) as jumlah
                FROM riwayat_review
                GROUP BY jenis_proposal
            """)
            per_jenis = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_review": total,
                "rata_rata_skor": round(rata_rata, 2),
                "skor_tertinggi": tertinggi,
                "skor_terendah": terendah,
                "review_per_jenis": per_jenis
            }
