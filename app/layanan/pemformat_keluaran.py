"""
Modul pemformat keluaran untuk hasil evaluasi.

Menyediakan utilitas untuk memformat hasil
evaluasi proposal menjadi berbagai format output.
"""

from typing import Any

from app.skema.model import HasilEvaluasi


class PemformatKeluaran:
    """
    Layanan untuk memformat hasil evaluasi proposal.

    Menyediakan berbagai format output seperti
    teks, HTML, dan JSON.
    """

    @staticmethod
    def format_sebagai_teks(hasil: HasilEvaluasi) -> str:
        """
        Memformat hasil evaluasi sebagai teks biasa.

        Parameter:
            hasil: Objek HasilEvaluasi

        Mengembalikan:
            String berisi hasil dalam format teks
        """
        baris: list[str] = []

        # Header
        baris.append("=" * 60)
        baris.append("HASIL EVALUASI PROPOSAL")
        baris.append("=" * 60)
        baris.append("")

        # Skor total
        baris.append(f"📊 SKOR TOTAL: {hasil.skor}/100")
        baris.append("")

        # Detail skor jika ada
        if hasil.detail_skor:
            baris.append("📋 DETAIL SKOR:")
            baris.append(f"   • Latar Belakang: {hasil.detail_skor.latar_belakang}/20")
            baris.append(f"   • Formulasi Masalah: {hasil.detail_skor.formulasi_masalah}/20")
            baris.append(f"   • Tujuan: {hasil.detail_skor.tujuan}/20")
            baris.append(f"   • Metodologi: {hasil.detail_skor.metodologi}/20")
            baris.append(f"   • Luaran: {hasil.detail_skor.luaran}/20")
            baris.append("")

        # Kekuatan
        if hasil.daftar_kekuatan:
            baris.append("✅ KEKUATAN:")
            for kekuatan in hasil.daftar_kekuatan:
                baris.append(f"   • {kekuatan}")
            baris.append("")

        # Kelemahan
        if hasil.daftar_kelemahan:
            baris.append("⚠️ KELEMAHAN:")
            for kelemahan in hasil.daftar_kelemahan:
                baris.append(f"   • {kelemahan}")
            baris.append("")

        # Saran
        if hasil.daftar_saran:
            baris.append("💡 SARAN PERBAIKAN:")
            for saran in hasil.daftar_saran:
                baris.append(f"   • {saran}")
            baris.append("")

        # Ringkasan
        baris.append("📝 RINGKASAN:")
        baris.append(f"   {hasil.ringkasan}")
        baris.append("")
        baris.append("=" * 60)

        return "\n".join(baris)

    @staticmethod
    def format_sebagai_html(hasil: HasilEvaluasi) -> str:
        """
        Memformat hasil evaluasi sebagai HTML.

        Parameter:
            hasil: Objek HasilEvaluasi

        Mengembalikan:
            String berisi hasil dalam format HTML
        """
        html_parts: list[str] = []

        html_parts.append('<div class="hasil-evaluasi">')

        # Skor total
        warna_skor = PemformatKeluaran._dapatkan_warna_skor(hasil.skor)
        html_parts.append(f'''
            <div class="skor-card" style="border-color: {warna_skor}">
                <h2>Skor Total</h2>
                <div class="skor-nilai" style="color: {warna_skor}">{hasil.skor}/100</div>
            </div>
        ''')

        # Kekuatan
        if hasil.daftar_kekuatan:
            html_parts.append('<div class="section kekuatan">')
            html_parts.append('<h3>✅ Kekuatan</h3>')
            html_parts.append('<ul>')
            for kekuatan in hasil.daftar_kekuatan:
                html_parts.append(f'<li>{kekuatan}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Kelemahan
        if hasil.daftar_kelemahan:
            html_parts.append('<div class="section kelemahan">')
            html_parts.append('<h3>⚠️ Kelemahan</h3>')
            html_parts.append('<ul>')
            for kelemahan in hasil.daftar_kelemahan:
                html_parts.append(f'<li>{kelemahan}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Saran
        if hasil.daftar_saran:
            html_parts.append('<div class="section saran">')
            html_parts.append('<h3>💡 Saran Perbaikan</h3>')
            html_parts.append('<ul>')
            for saran in hasil.daftar_saran:
                html_parts.append(f'<li>{saran}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Ringkasan
        html_parts.append(f'''
            <div class="section ringkasan">
                <h3>📝 Ringkasan</h3>
                <p>{hasil.ringkasan}</p>
            </div>
        ''')

        html_parts.append('</div>')

        return "".join(html_parts)

    @staticmethod
    def _dapatkan_warna_skor(skor: int) -> str:
        """
        Mendapatkan warna berdasarkan nilai skor.

        Parameter:
            skor: Nilai skor (0-100)

        Mengembalikan:
            String kode warna hex
        """
        if skor >= 80:
            return "#38A169"  # Hijau
        elif skor >= 60:
            return "#3B82F6"  # Biru
        elif skor >= 40:
            return "#B7791F"  # Kuning/Emas
        else:
            return "#E53E3E"  # Merah

    @staticmethod
    def parse_hasil_mentah(hasil_mentah: dict[str, Any]) -> HasilEvaluasi:
        """
        Mengurai hasil mentah dari LLM menjadi HasilEvaluasi.

        Parameter:
            hasil_mentah: Dictionary hasil dari LLM

        Mengembalikan:
            Objek HasilEvaluasi yang tervalidasi
        """
        return HasilEvaluasi(**hasil_mentah)
