import re
from .base import RegraDocumentoBase


class CPFRule(RegraDocumentoBase):
    categoria = "CPF"
    score_minimo = 0.6

    palavras_chave = [
        "CPF",
        "CADASTRO DE PESSOAS FISICAS",
        "RECEITA FEDERAL"
    ]

    def match(self, texto: str) -> bool:
        """
        Diz se o documento pode ser CPF
        """
        texto = texto.upper()

        if re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", texto):
            return True

        for palavra in self.palavras_chave:
            if palavra in texto:
                return True

        return False

    def score(self, texto: str) -> float:
        """
        Calcula score contínuo (0–1)
        """
        texto = texto.upper()
        pontos = 0

        for palavra in self.palavras_chave:
            if palavra in texto:
                pontos += 1

        if re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", texto):
            pontos += 1

        return pontos / (len(self.palavras_chave) + 1)
