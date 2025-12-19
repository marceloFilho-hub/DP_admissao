import re
from .base import RegraDocumentoBase


class RGRule(RegraDocumentoBase):
    categoria = "RG"
    score_minimo = 0.6

    palavras_chave = [
        "REGISTRO GERAL",
        "CARTEIRA DE IDENTIDADE",
        "IDENTIDADE",
        "SSP",
        "SECRETARIA DE SEGURANÇA"
    ]

    def match(self, texto: str) -> bool:
        texto = texto.upper()

        # Palavras-chave fortes
        for palavra in self.palavras_chave:
            if palavra in texto:
                return True

        # Padrão comum de RG (variações estaduais)
        if re.search(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b", texto):
            return True

        return False

    def score(self, texto: str) -> float:
        texto = texto.upper()
        pontos = 0

        for palavra in self.palavras_chave:
            if palavra in texto:
                pontos += 1

        if re.search(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b", texto):
            pontos += 1

        return pontos / (len(self.palavras_chave) + 1)

