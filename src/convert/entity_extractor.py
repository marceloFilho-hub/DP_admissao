import re
import unicodedata
from typing import Dict


class EntityExtractor:
    """
    Extrator unificado, sensível à categoria do documento.
    """

    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================
    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return re.sub(r"\s+", " ", text).strip()

    # =====================================================
    # ORQUESTRADOR
    # =====================================================
    def extract(self, raw_text: str, categoria: str) -> Dict:
        text = self.normalize(raw_text)
        categoria = categoria.upper()

        campos = {}

        if categoria == "RG":
            campos.update(self._extract_rg(text))
            campos.update(self._extract_nome(text))

        elif categoria == "CPF":
            campos.update(self._extract_cpf(text))

        elif categoria.startswith("COMPROVANTE_RESIDENCIA"):
            campos.update(self._extract_endereco(text))

        return campos

    # =====================================================
    # EXTRATORES
    # =====================================================
    def _extract_rg(self, text: str) -> Dict:
        match = re.search(r"\b\d{2}\.?\d{3}\.?\d{3}-?\d\b", text)
        return {
            "rg": {
                "valor": re.sub(r"\D", "", match.group()) if match else None,
                "score": 0.95 if match else 0.0
            }
        }

    def _extract_nome(self, text: str) -> Dict:
        match = re.search(r"nome[:\s]+([a-z\s]+)", text)
        return {
            "nome": {
                "valor": match.group(1).upper().strip() if match else None,
                "score": 0.9 if match else 0.0
            }
        }

    def _extract_cpf(self, text: str) -> Dict:
        match = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", text)
        return {
            "cpf": {
                "valor": re.sub(r"\D", "", match.group()) if match else None,
                "score": 0.95 if match else 0.0
            }
        }

    def _extract_endereco(self, text: str) -> Dict:
        match = re.search(r"(rua|avenida|av\.|travessa)[^,\n]+", text)
        return {
            "endereco": {
                "valor": match.group().upper() if match else None,
                "score": 0.85 if match else 0.0
            }
        }