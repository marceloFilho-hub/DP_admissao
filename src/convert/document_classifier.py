import re
from typing import Tuple


class DocumentClassifier:
    """
    Classificador determinístico para documentos de RH
    Retorna (categoria, score)
    """

    def __init__(self):
        self.rules = self._build_rules()

    # =====================================================
    # MÉTODO PRINCIPAL
    # =====================================================
    def classify(self, text: str) -> Tuple[str, float]:
        text = self._normalize(text)

        best_match = ("nao_identificado", 0.0)

        for categoria, rule in self.rules.items():
            score = self._score(text, rule)
            if score > best_match[1]:
                best_match = (categoria, score)

        # 🔐 Threshold de segurança
        if best_match[1] < 0.55:
            return "nao_identificado", best_match[1]

        return best_match

    # =====================================================
    # SCORE POR REGRA
    # =====================================================
    def _score(self, text: str, rule: dict) -> float:
        score = 0.0

        # Palavras-chave
        for kw in rule.get("keywords", []):
            if kw in text:
                score += rule.get("kw_weight", 0.1)

        # Regex forte
        for pattern in rule.get("regex", []):
            if re.search(pattern, text):
                score += rule.get("regex_weight", 0.3)

        # Penalidade
        for bad in rule.get("negative", []):
            if bad in text:
                score -= 0.2

        return min(score, 1.0)

    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================
    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text

    # =====================================================
    # REGRAS
    # =====================================================
    def _build_rules(self):
        return {

            # ================= IDENTIFICAÇÃO =================

            "rg": {
                "keywords": ["registro geral", "carteira de identidade", "rg"],
                "regex": [r"\d{2}\.\d{3}\.\d{3}", r"\d{9}"],
                "kw_weight": 0.15,
                "regex_weight": 0.35
            },

            "cpf": {
                "keywords": ["cpf", "cadastro de pessoas fisicas"],
                "regex": [r"\d{3}\.\d{3}\.\d{3}-\d{2}", r"\d{11}"],
                "kw_weight": 0.2,
                "regex_weight": 0.4
            },

            "cnh": {
                "keywords": ["carteira nacional de habilitacao", "habilitacao", "cnh"],
                "regex": [r"registro", r"categoria [a-e]"],
                "kw_weight": 0.2,
                "regex_weight": 0.4
            },

            "passaporte": {
                "keywords": ["passport", "passaporte"],
                "regex": [r"[a-z]{1}\d{6}"],
                "kw_weight": 0.3,
                "regex_weight": 0.4
            },

            "ctps": {
                "keywords": ["carteira de trabalho", "ctps"],
                "regex": [r"\d{7}", r"serie"],
                "kw_weight": 0.25,
                "regex_weight": 0.4
            },

            "titulo_eleitor": {
                "keywords": ["titulo de eleitor", "justica eleitoral"],
                "regex": [r"\d{12}"],
                "kw_weight": 0.3,
                "regex_weight": 0.4
            },

            # ================= ENDEREÇO =================

            "comprovante_endereco": {
                "keywords": [
                    "endereco", "cep", "rua", "avenida",
                    "energia", "agua", "telefone", "gás", "fatura"
                ],
                "regex": [r"\d{5}-\d{3}"],
                "kw_weight": 0.1,
                "regex_weight": 0.3
            },

            "contrato_aluguel": {
                "keywords": ["contrato de locacao", "aluguel"],
                "regex": [r"locador", r"locatario"],
                "kw_weight": 0.3,
                "regex_weight": 0.4
            },

            # ================= TRABALHISTAS =================

            "pis": {
                "keywords": ["pis", "pasep"],
                "regex": [r"\d{11}"],
                "kw_weight": 0.3,
                "regex_weight": 0.4
            },

            "holerite": {
                "keywords": ["holerite", "contracheque", "salario bruto", "inss"],
                "regex": [r"r\$"],
                "kw_weight": 0.25,
                "regex_weight": 0.35
            },

            "comprovante_vinculo": {
                "keywords": ["vinculo empregaticio", "empregado", "empresa"],
                "regex": [],
                "kw_weight": 0.3
            },

            "atestado_medico": {
                "keywords": ["atestado", "crm", "medico"],
                "regex": [r"crm\s?\d+"],
                "kw_weight": 0.3,
                "regex_weight": 0.4
            },

            # ================= CERTIDÕES =================

            "certidao_nascimento": {
                "keywords": ["certidao de nascimento"],
                "regex": [],
                "kw_weight": 0.5
            },

            "certidao_casamento": {
                "keywords": ["certidao de casamento"],
                "regex": [],
                "kw_weight": 0.5
            },

            "certidao_reservista": {
                "keywords": ["certificado de reservista"],
                "regex": [],
                "kw_weight": 0.5
            },

            # ================= OUTROS =================

            "assinatura": {
                "keywords": ["assinatura"],
                "regex": [],
                "kw_weight": 0.6
            },

            "foto_candidato": {
                "keywords": ["foto", "imagem"],
                "negative": ["cpf", "rg", "carteira"],
                "kw_weight": 0.4
            },

            "selfie": {
                "keywords": ["selfie"],
                "kw_weight": 0.6
            },

            "plano_saude": {
                "keywords": ["plano de saude", "carteirinha"],
                "regex": [],
                "kw_weight": 0.4
            },
        }
