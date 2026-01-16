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
        
        Pengecualian:
            ValueError: Jika API key tidak valid
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key tidak boleh kosong")
        
        if not api_key.startswith("gsk_"):
            pencatat.warning("API key tidak memiliki format Groq yang benar (seharusnya dimulai dengan 'gsk_')")
        
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
            # Log untuk debugging
            pencatat.info(f"Memanggil Groq API: {self._api_endpoint}")
            pencatat.info(f"Model: {self._model}")
            pencatat.info(f"API Key tersedia: {bool(self._api_key and len(self._api_key) > 10)}")
            
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

                pencatat.info(f"Groq API response status: {response.status_code}")

                if response.status_code != 200:
                    error_detail = response.text
                    pencatat.error(f"Groq API error: {response.status_code} - {error_detail}")
                    raise GagalMemproses(
                        pesan=f"Gagal memanggil Groq API (status {response.status_code}). Silakan coba lagi.",
                        kode="GROQ_API_ERROR"
                    )

                hasil_json = response.json()
                hasil_teks = hasil_json["choices"][0]["message"]["content"]
                pencatat.info(f"Panjang respons: {len(hasil_teks)} karakter")

            pencatat.info("Review proposal selesai")
            return self._parse_hasil(hasil_teks)

        except httpx.TimeoutException as e:
            pencatat.error(f"Timeout saat memanggil Groq API: {str(e)}")
            raise GagalMemproses(
                pesan="Timeout saat memproses proposal. Silakan coba lagi.",
                kode="TIMEOUT"
            )
        except httpx.HTTPError as e:
            pencatat.error(f"HTTP error saat memanggil Groq API: {str(e)}")
            raise GagalMemproses(
                pesan="Gagal terhubung ke server AI. Periksa koneksi internet.",
                kode="HTTP_ERROR"
            )
        except KeyError as e:
            pencatat.error(f"Format respons tidak sesuai: {str(e)}")
            raise GagalMemproses(
                pesan="Format respons dari AI tidak valid.",
                kode="FORMAT_ERROR"
            )
        except GagalMemproses:
            # Re-raise GagalMemproses
            raise
        except Exception as e:
            pencatat.error(f"Gagal melakukan review: {type(e).__name__}: {str(e)}", exc_info=True)
            raise GagalMemproses(
                pesan=f"Terjadi kesalahan tidak terduga: {str(e)}",
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
