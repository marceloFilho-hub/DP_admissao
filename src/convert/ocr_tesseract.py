from pathlib import Path
import pdfplumber
import pytesseract
import cv2
import numpy as np
import re
from document_classifier import DocumentClassifier


# =====================================================
# CONFIGURAÇÃO FORÇADA DO TESSERACT (AMBIENTE RESTRITO)
# =====================================================
TESSERACT_DIR = r"C:\Users\marcelo.lsantos_bhub\AppData\Local\Programs\Tesseract-OCR"
pytesseract.pytesseract.tesseract_cmd = str(Path(TESSERACT_DIR) / "tesseract.exe")

# força tessdata
import os
os.environ["TESSDATA_PREFIX"] = str(Path(TESSERACT_DIR) / "tessdata")


class PDFTextExtractorTesseract:

    def __init__(self, lang="por", resolution=300):
        print("[INFO] Inicializando Tesseract OCR...")
        self.lang = lang
        self.resolution = resolution
        self.classifier = DocumentClassifier()

        self.tess_config = (
            "--oem 3 "
            "--psm 6 "
            "-c preserve_interword_spaces=1"
        )

    # =====================================================
    # EXTRAÇÃO DE TEXTO (PDF DIGITAL + OCR)
    # =====================================================
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        full_text = ""

        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                print(f"[INFO] Página {i}/{len(pdf.pages)}")

                # 1️⃣ Texto digital
                text = page.extract_text()
                if text and len(text.strip()) > 30:
                    full_text += text + "\n"
                    continue

                # 2️⃣ OCR
                print("[OCR] Aplicando OCR com Tesseract...")

                img = page.to_image(resolution=self.resolution).original
                img = np.array(img)

                processed = self._preprocess_image(img)

                ocr_text = pytesseract.image_to_string(
                    processed,
                    lang=self.lang,
                    config=self.tess_config
                )

                full_text += ocr_text + "\n"

        return self._normalize_text(full_text)

    # =====================================================
    # PRÉ-PROCESSAMENTO DE IMAGEM
    # =====================================================
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 10
        )
        return thresh

    # =====================================================
    # CLASSIFICAR + RENOMEAR (COM SCORE)
    # =====================================================
    def classify_and_rename(self, pdf_path: Path, text: str):
        categoria, score = self.classifier.classify(text)

        print(f"[CLASSIFICAÇÃO] {categoria} | score={score:.2f}")

        if score < 0.55:
            categoria = "nao_identificado"

        novo_nome = f"{categoria}.pdf"
        novo_path = pdf_path.parent / novo_nome

        # evita sobrescrever
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
# EXECUÇÃO PRINCIPAL — VARRE A PASTA
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

