import re
from ..base import RegraDocumentoBase


class AguaRule(RegraDocumentoBase):
    categoria = "COMPROVANTE_RESIDENCIA"
    subcategoria = "AGUA"
    score_minimo = 0.6

    palavras_chave = [
        "CONTA DE AGUA",
        "SANEAMENTO",
        "COMPANHIA DE AGUA",
        "ABASTECIMENTO",
        "M3",
        "HIDROMETRO"
    ]

    def match(self, texto: str) -> bool:
        texto = texto.upper()

        for palavra in self.palavras_chave:
            if palavra in texto:
                return True

        # Presença de valor monetário típico
        if re.search(r"R\$ ?\d+,\d{2}", texto):
            return True

        return False

    def score(self, texto: str) -> float:
        texto = texto.upper()
        pontos = 0

        for palavra in self.palavras_chave:
            if palavra in texto:
                pontos += 1

        if re.search(r"R\$ ?\d+,\d{2}", texto):
            pontos += 1

        return pontos / (len(self.palavras_chave) + 1)
