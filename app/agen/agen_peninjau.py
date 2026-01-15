"""
Modul agent peninjau proposal.

Implementasi LangChain Agent untuk meninjau
dan mengevaluasi proposal akademik.
"""

import json
import logging
from typing import Any

from langchain.chains import LLMChain  # type: ignore[import-untyped]
from langchain.prompts import PromptTemplate  # type: ignore[import-untyped]
from langchain_openai import AzureChatOpenAI

from app.pengecualian import GagalMemproses

pencatat = logging.getLogger(__name__)


class AgenPeninjauProposal:
    """
    Agent LangChain untuk meninjau dan mengevaluasi proposal akademik.

    Agent ini menggunakan structured reasoning untuk menilai:
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

    def __init__(self, llm: AzureChatOpenAI):
        """
        Inisialisasi agent peninjau proposal.

        Parameter:
            llm: Instance Azure OpenAI LLM
        """
        self._llm = llm
        self._prompt = PromptTemplate(
            input_variables=["teks_proposal", "jenis_proposal"],
            template=self.TEMPLAT_PROMPT
        )
        self._rantai = LLMChain(llm=self._llm, prompt=self._prompt)
        pencatat.info("AgenPeninjauProposal berhasil diinisialisasi")

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

        try:
            hasil = await self._rantai.ainvoke({
                "teks_proposal": teks_proposal,
                "jenis_proposal": jenis_proposal
            })
            pencatat.info("Review proposal selesai")
            return self._parse_hasil(hasil.get("text", ""))
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

            pencatat.warning(f"Gagal parse JSON dari respons LLM")
            raise GagalMemproses(
                pesan="Format respons tidak valid dari AI",
                kode="FORMAT_TIDAK_VALID"
            )
