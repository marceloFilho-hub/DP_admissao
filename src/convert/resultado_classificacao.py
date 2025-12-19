from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ResultadoClassificacao:
    arquivo: str = ""
    categoria: str = ""
    score_regras: float = 0.0
    score_ocr: float = 0.0
    rotacao: int = 0
    campos: Optional[Dict] = None

    score_final: float = field(init=False)

    def __post_init__(self):
        peso_regras = 0.6
        peso_ocr = 0.4  

        self.score_final = round(
            (self.score_regras * peso_regras) +
            (self.score_ocr * peso_ocr),
            3
        )