from pathlib import Path
import os
import re
import cv2
import numpy as np
import pdfplumber
import pytesseract
import easyocr

from document_classifier import DocumentClassifier


# =====================================================
# CONFIGURAÇÃO FORÇADA DO TESSERACT (WINDOWS / RESTRITO)
# =====================================================
TESSERACT_DIR = r"C:\Users\marcelo.lsantos_bhub\AppData\Local\Programs\Tesseract-OCR"

pytesseract.pytesseract.tesseract_cmd = str(
    Path(TESSERACT_DIR) / "tesseract.exe"
)

os.environ["TESSDATA_PREFIX"] = str(
    Path(TESSERACT_DIR) / "tessdata"
)


class PDFTextExtractorTesseract:
    """
    OCR PROFISSIONAL + CLASSIFICAÇÃO
    --------------------------------
    - Texto digital (pdfplumber)
    - OCR híbrido (Tesseract + EasyOCR)
    - Escolhe melhor OCR automaticamente
    - Classifica documentos de RH
    - Renomeia PDFs
    - Salva TXT
    """

    def __init__(self, lang="por", resolution=300):
        print("[INFO] Inicializando OCR híbrido...")
        self.lang = lang
        self.resolution = resolution

        self.easyocr = easyocr.Reader([lang])
        self.classifier = DocumentClassifier()

        self.tess_config = (
            "--oem 3 "
            "--psm 6 "
            "-c preserve_interword_spaces=1"
        )

    # =====================================================
    # EXTRAÇÃO COMPLETA DO PDF
    # =====================================================
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        full_text = ""

        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                print(f"[INFO] Página {i}/{len(pdf.pages)}")

                # 1️⃣ TEXTO DIGITAL
                text = page.extract_text()
                if text and len(text.strip()) > 40:
                    full_text += text + "\n"
                    continue

                # 2️⃣ OCR
                print("[OCR] Aplicando OCR híbrido...")

                image = page.to_image(resolution=self.resolution).original
                image = np.array(image)

                processed = self._preprocess_image(image)

                tess_text = pytesseract.image_to_string(
                    processed,
                    lang=self.lang,
                    config=self.tess_config
                )

                easy_text = self._ocr_easyocr(processed)

                best_text = self._choose_best_text(tess_text, easy_text)

                full_text += best_text + "\n"

        return self._normalize_text(full_text)

    # =====================================================
    # OCR EASYOCR
    # =====================================================
    def _ocr_easyocr(self, img: np.ndarray) -> str:
        result = self.easyocr.readtext(img, detail=0)
        return "\n".join(result)

    # =====================================================
    # ESCOLHA DO MELHOR OCR
    # =====================================================
    def _choose_best_text(self, tesseract_text: str, easyocr_text: str) -> str:
        score_t = self._score_text(tesseract_text)
        score_e = self._score_text(easyocr_text)

        print(f"[OCR SCORE] Tesseract={score_t:.2f} | EasyOCR={score_e:.2f}")

        return tesseract_text if score_t >= score_e else easyocr_text

    # =====================================================
    # SCORE DE QUALIDADE DO TEXTO
    # =====================================================
    def _score_text(self, text: str) -> float:
        if not text:
            return 0.0

        text = text.lower()

        palavras_chave = [
            "cpf", "rg", "carteira", "identidade",
            "nascimento", "república", "brasil",
            "título", "eleitor", "trabalho", "pis",
            "ctps", "contrato", "endereço"
        ]

        score = 0.0
        score += min(len(text) / 1500, 1.0) * 0.4
        score += sum(1 for p in palavras_chave if p in text) * 0.1
        score -= len(re.findall(r"[#@%&*]", text)) * 0.05

        return max(0.0, min(score, 1.0))

    # =====================================================
    # PRÉ-PROCESSAMENTO DE IMAGEM
    # =====================================================
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        thresh = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )
        return thresh

    # =====================================================
    # CLASSIFICAR E RENOMEAR
    # =====================================================
    def classify_and_rename(self, pdf_path: Path, text: str):
        categoria, score = self.classifier.classify(text)

        print(f"[CLASSIFICAÇÃO] {categoria} | score={score:.2f}")

        if score < 0.55:
            categoria = "nao_identificado"

        novo_nome = f"{categoria}.pdf"
        novo_path = pdf_path.parent / novo_nome

        if novo_path.exists():
            novo_path = pdf_path.parent / f"{categoria}_{pdf_path.stem}.pdf"

        pdf_path.rename(novo_path)
        print(f"[RENOMEADO] {pdf_path.name} → {novo_path.name}")

        return novo_path, categoria, score

    # =====================================================
    # SALVAR TXT
    # =====================================================
    def save_as_txt(self, pdf_path: Path, text: str):
        txt_path = pdf_path.with_suffix(".txt")
        txt_path.write_text(text, encoding="utf-8")
        print(f"[TXT] Salvo: {txt_path.name}")

    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================
    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# =====================================================
# EXECUÇÃO PRINCIPAL
# =====================================================
if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parents[2]
    PDF_DIR = BASE_DIR / "src" / "convert" / "arq_descompactado"

    extractor = PDFTextExtractorTesseract()

    print(f"[INFO] Varrendo pasta: {PDF_DIR}")

    for pdf in PDF_DIR.rglob("*.pdf"):
        print(f"\n[PROCESSANDO] {pdf.name}")

        try:
            texto = extractor.extract_text_from_pdf(pdf)
            novo_pdf, categoria, score = extractor.classify_and_rename(pdf, texto)
            extractor.save_as_txt(novo_pdf, texto)

        except Exception as e:
            print(f"[ERRO] {pdf.name} → {e}")

    print("\n[FINALIZADO] OCR + Classificação concluídos.")
