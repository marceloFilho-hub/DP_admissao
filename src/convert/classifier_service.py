from pathlib import Path
from collections import defaultdict
from document_classifier import DocumentClassifier
from resultado_classificacao import ResultadoClassificacao
from feedback_menager import FeedbackManager




class ClassifierService:
    """
    Serviço de classificação com aprendizado incremental via feedback humano.
    """

    def __init__(self, feedback_manager):
        self.rule_classifier = DocumentClassifier()
        self.feedback_manager = feedback_manager
        self.feedback_stats = self._carregar_estatisticas_feedback()

    # =====================================================
    # CLASSIFICA + RENOMEIA
    # =====================================================
    def classify_and_rename(self, pdf_path: Path, texto: str):
        resultado_base = self.rule_classifier.classify(texto)

        if isinstance(resultado_base, tuple):
            categoria = str(resultado_base[0])
            score_regras = float(resultado_base[1])
        elif isinstance(resultado_base, dict):
            categoria = str(resultado_base.get("tipo", "NAO_IDENTIFICADO"))
            score_regras = float(resultado_base.get("score", 0.0))
        else:
            categoria = str(resultado_base)
            score_regras = 0.0

        categoria = categoria.upper().replace(" ", "_")

        ajuste = self._get_ajuste_categoria(categoria)
        score_regras_ajustado = round(score_regras * ajuste, 3)

        resultado = ResultadoClassificacao(
            arquivo=pdf_path.name,
            categoria=categoria,
            score_regras=score_regras_ajustado,
            score_ocr=0.0,
            rotacao=0
        )

        novo_pdf = self._rename_file(pdf_path, resultado)

        # registra feedback do documento
        self.feedback_manager.registrar_documento(resultado)

        # 🔥 RETORNO CERTO
        return novo_pdf, resultado

    # =====================================================
    # RENOMEIO CONTROLADO
    # =====================================================
    def _rename_file(self, pdf_path: Path, resultado: ResultadoClassificacao) -> Path:
        original_name = pdf_path.name

        # Evita renomear duas vezes
        if original_name.startswith(resultado.categoria):
            print("[INFO] Arquivo já renomeado.")
            return pdf_path

        score = int(resultado.score_final * 100)
        novo_nome = f"{resultado.categoria}_{score}_{original_name}"
        novo_path = pdf_path.parent / novo_nome

        contador = 1
        while novo_path.exists():
            novo_nome = f"{resultado.categoria}_{score}_{contador}_{original_name}"
            novo_path = pdf_path.parent / novo_nome
            contador += 1

        pdf_path.rename(novo_path)
        print(f"[RENOMEADO] {pdf_path.name} → {novo_path.name}")

        return novo_path

    # =====================================================
    # CARREGA ESTATÍSTICAS DO FEEDBACK
    # =====================================================
    def _carregar_estatisticas_feedback(self) -> dict:
        stats = defaultdict(lambda: {
            "total": 0,
            "acertos": 0,
            "erros": 0
        })

        feedbacks = self.feedback_manager.carregar_feedbacks_documentos()

        for row in feedbacks:
            prevista = row["categoria_prevista"]
            correta = row["categoria_correta"]

            stats[prevista]["total"] += 1

            if prevista == correta:
                stats[prevista]["acertos"] += 1
            else:
                stats[prevista]["erros"] += 1

        return stats



    # =====================================================
    # AJUSTE POR CATEGORIA
    # =====================================================
    def _get_ajuste_categoria(self, categoria: str) -> float:
        """
        Retorna multiplicador de confiança baseado no histórico humano.
        """
        dados = self.feedback_stats.get(categoria)

        if not dados or dados["total"] < 5:
            return 1.0  # ainda não há dados suficientes

        taxa_acerto = dados["acertos"] / dados["total"]

        if taxa_acerto >= 0.9:
            return 1.1   # muito confiável
        elif taxa_acerto >= 0.75:
            return 1.0   # normal
        elif taxa_acerto >= 0.5:
            return 0.9   # atenção
        else:
            return 0.75  # categoria problemática