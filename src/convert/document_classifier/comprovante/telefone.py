import re
from ..base import RegraDocumentoBase


class TelefoneRule(RegraDocumentoBase):
    categoria = "COMPROVANTE_RESIDENCIA"
    subcategoria = "TELEFONE"
    score_minimo = 0.6

    palavras_chave = [
        "TELEFONE",
        "TELEFONIA",
        "CELULAR",
        "FATURA",
        "OPERADORA",
        "INTERNET",
        "BANDA LARGA"
    ]

    def match(self, texto: str) -> bool:
        texto = texto.upper()

        for palavra in self.palavras_chave:
            if palavra in texto:
                return True

        # Padrão telefone brasileiro
        if re.search(r"\(\d{2}\)\s?\d{4,5}-?\d{4}", texto):
            return True

        return False

    def score(self, texto: str) -> float:
        texto = texto.upper()
        pontos = 0

        for palavra in self.palavras_chave:
            if palavra in texto:
                pontos += 1

        if re.search(r"\(\d{2}\)\s?\d{4,5}-?\d{4}", texto):
            pontos += 1

        return pontos / (len(self.palavras_chave) + 1)
