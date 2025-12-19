# document_classifier.py

import re
from collections import defaultdict
from typing import Dict, Tuple
import unicodedata


class DocumentClassifier:
    """
    Classificador determinístico baseado em regras.

    Responsável por:
    - Normalizar texto OCR
    - Aplicar regras (keywords + regex)
    - Gerar score por categoria
    - Retornar resultado estruturado

    NÃO:
    - Faz OCR
    - Renomeia arquivos
    """

    def __init__(self):

        # ==========================================
        # DEFINIÇÃO DAS REGRAS (OCR-AWARE)
        # ==========================================
        self.rules = {

            "RG": {
                "keywords": {
                    # Keywords curtas e robustas
                    "registro geral": 4,
                    "carteira de identidade": 3,
                    "republica federativa": 2,
                    "secretaria de seguranca": 2,
                    "instituto de identificacao": 2,
                },
                "regex": {
                    # RG com tolerância a OCR
                    r"\b\d{2}[.,]\d{3}[.,]\d{3}-?\d?\b": 4,

                    # Datas comuns em RG
                    r"\bdata\s+de\s+expedicao\b": 2,
                    r"\bdata\s+de\s+nascimento\b": 2,
                },
                "threshold": 6
            },

            # Futuras categorias:
            # "CPF": {...}
            # "CNH": {...}
        }

    # =================================================
    # NORMALIZAÇÃO DE TEXTO (ANTI-OCR RUIM)
    # =================================================
    def _normalize_text(self, text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))

        text = re.sub(r"\s+", " ", text)

        return text.strip()



    # =================================================
    # CLASSIFICAÇÃO PRINCIPAL
    # =================================================
    def classify(self, text: str) -> Tuple[str, float, Dict]:
        """
        Retorna:
        (
            categoria,
            score_normalizado (0-1),
            detalhes
        )
        """

        if not text or len(text.strip()) < 20:
            return "NAO_IDENTIFICADO", 0.0, {}

        text_norm = self._normalize_text(text)

        category_scores = {}
        debug_info = {}

        # ==========================================
        # AVALIA CADA CATEGORIA
        # ==========================================
        for category, rule in self.rules.items():

            score = 0
            hits = []

            # ----------------------------
            # KEYWORDS
            # ----------------------------
            for keyword, weight in rule["keywords"].items():
                if keyword in text_norm:
                    score += weight
                    hits.append(f"KW:{keyword}")

            # ----------------------------
            # REGEX
            # ----------------------------
            for pattern, weight in rule["regex"].items():
                if re.search(pattern, text_norm):
                    score += weight
                    hits.append(f"RX:{pattern}")

            category_scores[category] = score
            debug_info[category] = {
                "score": score,
                "threshold": rule["threshold"],
                "hits": hits
            }

        # ==========================================
        # DECISÃO FINAL
        # ==========================================
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        threshold = self.rules[best_category]["threshold"]

        if best_score < threshold:
            return "NAO_IDENTIFICADO", round(best_score / threshold, 2), debug_info

        # Normaliza score entre 0 e 1
        confidence = min(best_score / (threshold * 1.2), 1.0)

        return best_category, round(confidence, 2), debug_info


