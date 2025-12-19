class ResultadoClassificacao:
    def __init__(
        self,
        arquivo: str,
        categoria: str,
        subcategoria: str | None,
        score_regras: float,
        score_ocr: float,
        rotacao: int,
        score_final: float
    ):
        self.arquivo = arquivo
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.score_regras = score_regras
        self.score_ocr = score_ocr
        self.rotacao = rotacao
        self.score_final = score_final

        # Campos extraídos posteriormente
        self.campos = {}
