# feedback_manager.py

from pathlib import Path
import csv
from resultado_classificacao import ResultadoClassificacao


class FeedbackManager:
    """
    Responsável por:
    - Registrar histórico de classificações
    - Armazenar feedback humano (documento e campo)
    - Servir dataset para aprendizado futuro
    """

    def __init__(
        self,
        base_dir: Path,
        doc_csv_name: str = "feedback_documentos.csv",
        campo_csv_name: str = "feedback_campos.csv"
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.doc_csv = self.base_dir / doc_csv_name
        self.campo_csv = self.base_dir / campo_csv_name

        if not self.doc_csv.exists():
            self._create_doc_csv()

        if not self.campo_csv.exists():
            self._create_campo_csv()

    # =====================================================
    # CSV DE DOCUMENTOS
    # =====================================================
    def _create_doc_csv(self):
        with self.doc_csv.open(mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "arquivo",
                "categoria_prevista",
                "score_final",
                "score_regras",
                "score_ocr",
                "rotacao",
                "categoria_correta",
                "observacao"
            ])

    def registrar_documento(self, resultado: ResultadoClassificacao):
        """
        Registra histórico de classificação do documento.
        """
        with self.doc_csv.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                resultado.arquivo,
                resultado.categoria,
                resultado.score_final,
                resultado.score_regras,
                resultado.score_ocr,
                resultado.rotacao,
                "",  # categoria_correta (humano)
                ""   # observacao
            ])

    # =====================================================
    # CSV DE CAMPOS
    # =====================================================
    def _create_campo_csv(self):
        with self.campo_csv.open(mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "arquivo",
                "categoria",
                "campo",
                "valor_extraido",
                "score",
                "valor_correto",
                "observacao"
            ])

    def registrar_campos(self, resultado: ResultadoClassificacao):
        """
        Registra feedback em nível de campo.
        """
        if not resultado.campos:
            return

        with self.campo_csv.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            for campo, dados in resultado.campos.items():
                writer.writerow([
                    resultado.arquivo,
                    resultado.categoria,
                    campo,
                    dados.get("valor"),
                    dados.get("score"),
                    "",  # valor_correto (humano)
                    ""   # observacao
                ])

    # =====================================================
    # LEITURA DE FEEDBACKS CORRIGIDOS
    # =====================================================
    def carregar_feedbacks_documentos(self) -> list[dict]:
        """
        Retorna apenas documentos corrigidos pelo humano.
        """
        feedbacks = []

        with self.doc_csv.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["categoria_correta"]:
                    feedbacks.append(row)

        return feedbacks

    def carregar_feedbacks_campos(self) -> list[dict]:
        """
        Retorna apenas campos corrigidos pelo humano.
        """
        feedbacks = []

        with self.campo_csv.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["valor_correto"]:
                    feedbacks.append(row)

        return feedbacks

