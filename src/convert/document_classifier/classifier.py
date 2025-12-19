from .rg import RGRule
from .cpf import CPFRule
from .comprovante.agua import AguaRule
from .comprovante.luz import LuzRule
from .comprovante.telefone import TelefoneRule


class DocumentClassifier:
    """
    Orquestrador principal de classificação.
    """

    def __init__(self):
        self.regras_principais = [
            RGRule(),
            CPFRule()
        ]

        self.regras_comprovante = [
            AguaRule(),
            LuzRule(),
            TelefoneRule()
        ]

    def classify(self, texto: str) -> dict:
        melhor = {
            "categoria": "NAO_IDENTIFICADO",
            "subcategoria": None,
            "score": 0.0
        }

        # -----------------------------
        # 1️⃣ RG / CPF
        # -----------------------------
        for regra in self.regras_principais:
            score = regra.score(texto)
            if score >= regra.SCORE_MINIMO and score > melhor["score"]:
                melhor = {
                    "categoria": regra.CATEGORIA,
                    "subcategoria": None,
                    "score": round(score, 3)
                }

        # -----------------------------
        # 2️⃣ COMPROVANTE
        # -----------------------------
        for regra in self.regras_comprovante:
            score = regra.score(texto)
            if score >= regra.SCORE_MINIMO and score > melhor["score"]:
                melhor = {
                    "categoria": regra.CATEGORIA,
                    "subcategoria": regra.SUBCATEGORIA,
                    "score": round(score, 3)
                }

        return melhor