# csv_exporter.py

from pathlib import Path
import json
import csv


class CSVExporter:
    """
    Responsável por:
    - Ler JSONs gerados pelo pipeline
    - Unificar resultados em um CSV único
    - Preparar base para feedback humano e ML
    """

    def __init__(self, csv_path: Path):
        self.csv_path = Path(csv_path)

        # Cabeçalho padrão (ordem importa!)
        self.headers = [
            # Arquivo
            "arquivo",

            # Classificação
            "categoria_predita",
            "score_regras",
            "score_ocr",
            "score_final",
            "rotacao",

            # Feedback humano
            "categoria_correta",
            "feedback_ok",
            "observacao",

            # Entidades (RG – extensível)
            "rg_numero",
            "nome",
            "data_nascimento",
            "naturalidade",
            "filiacao",
        ]

        # Cria CSV com header se não existir
        if not self.csv_path.exists():
            self._create_csv()

    # =====================================================
    # CRIA CSV COM HEADER
    # =====================================================
    def _create_csv(self):
        with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()

    # =====================================================
    # ADICIONA UM DOCUMENTO AO CSV
    # =====================================================
    def append_from_json(self, json_path: Path):
        json_path = Path(json_path)

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        resultado = data.get("resultado_classificacao", {})
        entidades = data.get("entidades", {})

        row = {
            # Arquivo
            "arquivo": json_path.stem,

            # Classificação
            "categoria_predita": resultado.get("categoria"),
            "score_regras": resultado.get("score_regras"),
            "score_ocr": resultado.get("score_ocr"),
            "score_final": resultado.get("score_final"),
            "rotacao": resultado.get("rotacao"),

            # Feedback humano (vazio inicialmente)
            "categoria_correta": "",
            "feedback_ok": "",
            "observacao": "",

            # Entidades
            "rg_numero": entidades.get("rg_numero"),
            "nome": entidades.get("nome"),
            "data_nascimento": entidades.get("data_nascimento"),
            "naturalidade": entidades.get("naturalidade"),
            "filiacao": entidades.get("filiacao"),
        }

        self._append_row(row)

    # =====================================================
    # ESCREVE LINHA NO CSV
    # =====================================================
    def _append_row(self, row: dict):
        with open(self.csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(row)
