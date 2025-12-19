import re
from ..base import RegraDocumentoBase


class LuzRule(RegraDocumentoBase):
    categoria = "COMPROVANTE_RESIDENCIA"
    subcategoria = "LUZ"
    score_minimo = 0.6

    palavras_chave = [
        "ENERGIA ELETRICA",
        "CONTA DE LUZ",
        "KWH",
        "DISTRIBUIDORA",
        "ELETRO",
        "ANEEL"
    ]

    def match(self, texto: str) -> bool:
        texto = texto.upper()

        for palavra in self.palavras_chave:
            if palavra in texto:
                return True

        if re.search(r"\bKWH\b", texto):
            return True

        return False

    def score(self, texto: str) -> float:
        texto = texto.upper()
        pontos = 0

        for palavra in self.palavras_chave:
            if palavra in texto:
                pontos += 1

        if re.search(r"\bKWH\b", texto):
            pontos += 1

        return pontos / (len(self.palavras_chave) + 1)

