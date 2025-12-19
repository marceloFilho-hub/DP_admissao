# entity_extractor.py

import re
import unicodedata
from typing import Dict


class EntityExtractor:
    """
    Responsável por transformar TEXTO OCR em DADOS estruturados
    com score por campo.
    """

    # =====================================================
    # NORMALIZAÇÃO GLOBAL
    # =====================================================
    @staticmethod
    def normalize(text: str) -> str:
        """
        Remove acentos, normaliza espaços e caixa.
        ESSENCIAL para regex funcionar.
        """
        text = text.lower()

        # Remove acentos
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))

        # Normaliza espaços
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =====================================================
    # MÉTODO PRINCIPAL
    # =====================================================
    def extract(self, raw_text: str) -> Dict:
        text = self.normalize(raw_text)

        return {
            "rg": self._extract_rg(text),
            "nome": self._extract_nome(text),
            "data_nascimento": self._extract_data_nascimento(text),
            "data_expedicao": self._extract_data_expedicao(text),
            "naturalidade": self._extract_naturalidade(text),
            "filiacao": self._extract_filiacao(text)
        }

    # =====================================================
    # EXTRAÇÕES INDIVIDUAIS COM SCORE
    # =====================================================

    def _extract_rg(self, text: str) -> Dict:
        regex = r"\b\d{2}\.?\d{3}\.?\d{3}-?\d\b"
        match = re.search(regex, text)

        if not match:
            return self._empty_field()

        valor = re.sub(r"\D", "", match.group())

        score = 0.6
        evidencias = ["regex_rg"]

        if "registro geral" in text:
            score += 0.2
            evidencias.append("contexto_rg")

        if len(valor) == 9:
            score += 0.1
            evidencias.append("tamanho_valido")

        return self._build_field(valor, score, "regex", evidencias)

    def _extract_nome(self, text: str) -> Dict:
        match = re.search(r"nome:\s*([a-z\s]+)", text)

        if not match:
            return self._empty_field()

        nome = match.group(1).strip().upper()
        score = 0.5
        evidencias = ["rotulo_nome"]

        if len(nome.split()) >= 2:
            score += 0.2
            evidencias.append("nome_composto")

        if not re.search(r"\d", nome):
            score += 0.1
            evidencias.append("sem_numeros")

        return self._build_field(nome, score, "heuristica", evidencias)

    def _extract_data_nascimento(self, text: str) -> Dict:
        match = re.search(r"data de nascimento:\s*(\d{2}/\d{2}/\d{4})", text)

        if not match:
            return self._empty_field()

        d, m, y = match.group(1).split("/")
        valor = f"{y}-{m}-{d}"

        return self._build_field(
            valor,
            score=0.9,
            fonte="regex",
            evidencias=["data_valida", "contexto_nascimento"]
        )

    def _extract_data_expedicao(self, text: str) -> Dict:
        match = re.search(r"data de expedicao:\s*(\d{2}/\d{2}/\d{4})", text)

        if not match:
            return self._empty_field()

        d, m, y = match.group(1).split("/")
        valor = f"{y}-{m}-{d}"

        return self._build_field(
            valor,
            score=0.85,
            fonte="regex",
            evidencias=["data_valida", "contexto_expedicao"]
        )

    def _extract_naturalidade(self, text: str) -> Dict:
        match = re.search(r"naturalidade:\s*([a-z\- ]+)", text)

        if not match:
            return self._empty_field()

        valor = match.group(1).strip().upper()

        return self._build_field(
            valor,
            score=0.7,
            fonte="regex",
            evidencias=["contexto_naturalidade"]
        )

    def _extract_filiacao(self, text: str) -> Dict:
        match = re.search(r"filiacao:\s*([a-z\s]+)", text)

        if not match:
            return self._empty_field()

        valor = match.group(1).strip().upper()

        score = 0.6
        evidencias = ["rotulo_filiacao"]

        if len(valor.split()) >= 2:
            score += 0.2
            evidencias.append("nome_composto")

        return self._build_field(valor, score, "heuristica", evidencias)

    # =====================================================
    # HELPERS
    # =====================================================

    def _build_field(self, valor, score, fonte, evidencias):
        return {
            "valor": valor,
            "score": round(min(score, 1.0), 3),
            "fonte": fonte,
            "evidencias": evidencias
        }

    def _empty_field(self):
        return {
            "valor": None,
            "score": 0.0,
            "fonte": None,
            "evidencias": []
        }

