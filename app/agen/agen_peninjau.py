"""
Modul agent peninjau proposal.

Implementasi Agent untuk meninjau dan mengevaluasi
proposal akademik menggunakan Groq API (Llama 3.3).
"""

import json
import logging
from typing import Any

import httpx

from app.pengecualian import GagalMemproses

pencatat = logging.getLogger(__name__)


class AgenPeninjauProposal:
    """
    Agent untuk meninjau dan mengevaluasi proposal akademik.

    Menggunakan Groq API dengan model Llama 3.3 70B untuk menilai:
    - Kejelasan latar belakang
    - Formulasi masalah
    - Tujuan penelitian
    - Metodologi
    - Luaran yang diharapkan
    """

    TEMPLAT_PROMPT = """
Anda adalah peninjau proposal akademik profesional.

Tinjau proposal {jenis_proposal} berikut ini.

Evaluasi aspek-aspek berikut:
1. Kejelasan latar belakang (0-20 poin)
2. Formulasi masalah (0-20 poin)
3. Tujuan penelitian (0-20 poin)
4. Metodologi (0-20 poin)
5. Luaran yang diharapkan (0-20 poin)

Berikan output dalam format JSON valid (tanpa markdown code block):
{{
    "skor": <total_skor>,
    "detail_skor": {{
        "latar_belakang": <skor>,
        "formulasi_masalah": <skor>,
        "tujuan": <skor>,
        "metodologi": <skor>,
        "luaran": <skor>
    }},
    "daftar_kekuatan": ["kekuatan 1", "kekuatan 2", ...],
    "daftar_kelemahan": ["kelemahan 1", "kelemahan 2", ...],
    "daftar_saran": ["saran 1", "saran 2", ...],
    "ringkasan": "ringkasan evaluasi secara keseluruhan"
}}

Proposal:
{teks_proposal}
"""

    def __init__(
        self,
        api_key: str,
        api_endpoint: str = "https://api.groq.com/openai/v1/chat/completions",
        model: str = "llama-3.3-70b-versatile"
    ):
        """
        Inisialisasi agent peninjau proposal.

        Parameter:
            api_key: API key untuk Groq
            api_endpoint: Endpoint API Groq
            model: Model yang digunakan (default: llama-3.3-70b-versatile)
        """
        self._api_key = api_key
        self._api_endpoint = api_endpoint
        self._model = model
        pencatat.info(f"AgenPeninjauProposal diinisialisasi dengan model: {model}")

    async def tinjau(
        self,
        teks_proposal: str,
        jenis_proposal: str
    ) -> dict[str, Any]:
        """
        Meninjau proposal dan menghasilkan evaluasi terstruktur.

        Parameter:
            teks_proposal: Teks lengkap proposal
            jenis_proposal: Jenis proposal (pkm/skripsi/hibah)

        Mengembalikan:
            Dict berisi hasil evaluasi

        Pengecualian:
            ValueError: Jika teks proposal kosong
            GagalMemproses: Jika terjadi kesalahan saat memproses
        """
        if not teks_proposal or not teks_proposal.strip():
            raise ValueError("Teks proposal tidak boleh kosong")

        pencatat.info(f"Memulai review proposal jenis: {jenis_proposal}")

        # Format prompt
        prompt = self.TEMPLAT_PROMPT.format(
            jenis_proposal=jenis_proposal,
            teks_proposal=teks_proposal
        )

        try:
            # Panggil Groq API
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self._api_endpoint,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Anda adalah peninjau proposal akademik profesional. Berikan respons dalam format JSON valid."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                )

                if response.status_code != 200:
                    pencatat.error(f"Groq API error: {response.status_code} - {response.text}")
                    raise GagalMemproses(
                        pesan=f"Gagal memanggil Groq API: {response.status_code}",
                        kode="GROQ_API_ERROR"
                    )

                hasil_json = response.json()
                hasil_teks = hasil_json["choices"][0]["message"]["content"]

            pencatat.info("Review proposal selesai")
            return self._parse_hasil(hasil_teks)

        except httpx.TimeoutException:
            pencatat.error("Timeout saat memanggil Groq API")
            raise GagalMemproses(
                pesan="Timeout saat memproses proposal. Silakan coba lagi.",
                kode="TIMEOUT"
            )
        except Exception as e:
            pencatat.error(f"Gagal melakukan review: {str(e)}")
            raise GagalMemproses(
                pesan=f"Gagal memproses proposal: {str(e)}",
                kode="GAGAL_REVIEW"
            )

    def _parse_hasil(self, hasil_mentah: str) -> dict[str, Any]:
        """
        Mengurai hasil mentah dari LLM menjadi dictionary.

        Parameter:
            hasil_mentah: String hasil dari LLM

        Mengembalikan:
            Dictionary hasil evaluasi

        Pengecualian:
            GagalMemproses: Jika format respons tidak valid
        """
        try:
            # Coba parse langsung
            return json.loads(hasil_mentah)
        except json.JSONDecodeError:
            # Coba ekstrak JSON dari markdown code block
            try:
                import re
                json_match = re.search(r'```json?\s*([\s\S]*?)```', hasil_mentah)
                if json_match:
                    return json.loads(json_match.group(1))

                # Coba cari object JSON dalam teks
                json_match = re.search(r'\{[\s\S]*\}', hasil_mentah)
                if json_match:
                    return json.loads(json_match.group(0))

            except (json.JSONDecodeError, AttributeError):
                pass

            pencatat.warning("Gagal parse JSON dari respons LLM")
            raise GagalMemproses(
                pesan="Format respons tidak valid dari AI",
                kode="FORMAT_TIDAK_VALID"
            )
