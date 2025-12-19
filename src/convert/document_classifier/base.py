# base.py
from abc import ABC, abstractmethod


class RegraDocumentoBase(ABC):
    """
    Classe base única para qualquer tipo de documento.
    """

    # Constantes padrão (podem ser sobrescritas nas regras)
    CATEGORIA: str = "NAO_IDENTIFICADO"
    SUBCATEGORIA: str | None = None
    SCORE_MINIMO: float = 0.0

    # ===============================
    # PROPRIEDADES PADRONIZADAS
    # ===============================
    @property
    def categoria(self) -> str:
        return self.CATEGORIA

    @property
    def subcategoria(self) -> str | None:
        return self.SUBCATEGORIA

    @property
    def score_minimo(self) -> float:
        return self.SCORE_MINIMO

    # ===============================
    # CONTRATO DAS REGRAS
    # ===============================
    @abstractmethod
    def match(self, texto: str) -> bool:
        """
        Retorna True se a regra se aplica ao texto.
        """
        pass

    @abstractmethod
    def score(self, texto: str) -> float:
        """
        Retorna score normalizado entre 0 e 1.
        """
        pass
