#Classifier_service
from pathlib import Path
from collections import defaultdict

from document_classifier.classifier import DocumentClassifier
from resultado_classificacao import ResultadoClassificacao
from feedback_menager import FeedbackManager


class ClassifierService:

    def __init__(self, feedback_manager: FeedbackManager):
        self.classifier = DocumentClassifier()
        self.feedback_manager = feedback_manager
        self.feedback_stats = self._carregar_estatisticas_feedback()

    def classify_and_rename(self, pdf_path: Path, texto: str):
        resultado_base = self.classifier.classify(texto)

        categoria = resultado_base["categoria"]
        subcategoria = resultado_base["subcategoria"]
        score_regras = resultado_base["score"]

        ajuste = self._get_ajuste_categoria(categoria, subcategoria)
        score_final = round(score_regras * ajuste, 3)

        resultado = ResultadoClassificacao(
            arquivo=pdf_path.name,
            categoria=categoria,
            subcategoria=subcategoria,
            score_regras=score_regras,
            score_ocr=0.0,
            rotacao=0,
            score_final=score_final
        )

        novo_pdf = self._rename_file(pdf_path, resultado)

        self.feedback_manager.registrar_documento(resultado)

        return novo_pdf, resultado

    def _rename_file(self, pdf_path: Path, resultado: ResultadoClassificacao) -> Path:
        partes = [resultado.categoria]

        if resultado.subcategoria:
            partes.append(resultado.subcategoria)

        score = int(resultado.score_final * 100)
        prefixo = "__".join(partes)

        novo_nome = f"{prefixo}_{score}_{pdf_path.name}"
        novo_path = pdf_path.parent / novo_nome

        contador = 1
        while novo_path.exists():
            novo_nome = f"{prefixo}_{score}_{contador}_{pdf_path.name}"
            novo_path = pdf_path.parent / novo_nome
            contador += 1

        pdf_path.rename(novo_path)
        return novo_path
    from collections import defaultdict


    def _carregar_estatisticas_feedback(self):
        """
        Carrega feedback humano e gera estatísticas
        baseadas na categoria CORRETA.
        """

        stats = defaultdict(lambda: {
            "total": 0,
            "peso": 0.0,
            "acertos": 0,
            "erros": 0
        })

        feedbacks = self.feedback_manager.carregar_feedbacks_documentos()

        for row in feedbacks:
            categoria_prevista = row.get("categoria_prevista")
            subcategoria_prevista = row.get("subcategoria_prevista")

            categoria_correta = row.get("categoria_correta")
            subcategoria_correta = row.get("subcategoria_correta")

            confianca = float(row.get("confianca_humana", 1.0))

            # Chave SEMPRE baseada no que o modelo decidiu
            chave = (categoria_prevista, subcategoria_prevista)

            stats[chave]["total"] += 1

            if categoria_prevista == categoria_correta:
                stats[chave]["acertos"] += 1
                stats[chave]["peso"] += confianca
            else:
                stats[chave]["erros"] += 1
                # Penaliza erro (aprendizado negativo)
                stats[chave]["peso"] += (1 - confianca)

        return stats



    def _get_ajuste_categoria(self, categoria, subcategoria):
        chave = (categoria, subcategoria)
        dados = self.feedback_stats.get(chave)

        if not dados or dados["total"] < 3:
            return 1.0  # sem aprendizado ainda

        media = dados["peso"] / dados["total"]

        if media >= 0.85:
            return 1.1   # categoria muito confiável
        elif media >= 0.6:
            return 1.0   # neutro
        elif media >= 0.4:
            return 0.9   # atenção
        else:
            return 0.75  # categoria problemática

