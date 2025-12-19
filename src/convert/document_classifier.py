from typing import Dict, List

from document_classifier.rg import RGRule
from document_classifier.cpf import CPFRule
from document_classifier.comprovante.agua import AguaRule
from document_classifier.comprovante.luz import LuzRule
from document_classifier.comprovante.telefone import TelefoneRule


class DocumentClassifier:
    """
    Orquestrador de regras.
    Executa todas e escolhe o maior score.
    """

    def __init__(self):
        self.regras = [
            RGRule(),
            CPFRule(),
            AguaRule(),
            LuzRule(),
            TelefoneRule()
        ]

    def classify(self, texto: str) -> Dict:
        melhor_resultado = {
            "categoria": "NAO_IDENTIFICADO",
            "subcategoria": None,
            "score": 0.0
        }

        for regra in self.regras:
            if not regra.match(texto):
                continue

            score = regra.score(texto)

            if score >= regra.score_minimo and score > melhor_resultado["score"]:
                melhor_resultado = {
                    "categoria": regra.categoria,
                    "subcategoria": getattr(regra, "subcategoria", None),
                    "score": round(score, 3)
                }

        return melhor_resultado