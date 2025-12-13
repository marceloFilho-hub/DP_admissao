from pathlib import Path
import pdfplumber
import easyocr
import numpy as np
import re
from document_classifier import DocumentClassifier


class PDFTextExtractor:

    def __init__(self, lang="pt", resolution=300):
        print("[INFO] Inicializando EasyOCR...")
        self.reader = easyocr.Reader([lang])
        self.resolution = resolution
        self.classifier = DocumentClassifier()

    # =====================================================
    # EXTRAÇÃO DE TEXTO
    # =====================================================
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        pdf_path = Path(pdf_path)
        full_text = ""

        with pdfplumber.open(str(pdf_path)) as pdf:
            for n, page in enumerate(pdf.pages, 1):

                print(f"[INFO] Página {n}/{len(pdf.pages)}")

                text = page.extract_text()
                if text and text.strip():
                    full_text += text + "\n"
                    continue

                print("[OCR] Aplicando OCR...")
                page_img = page.to_image(resolution=self.resolution)
                img_np = np.array(page_img.annotated)

                ocr = self.reader.readtext(img_np, detail=0)
                full_text += "\n".join(ocr) + "\n"

        return full_text

    # =====================================================
    # SALVAR TXT
    # =====================================================
    def save_as_txt(self, pdf_path: Path, text: str):
        txt_path = pdf_path.with_suffix(".txt")
        txt_path.write_text(text, encoding="utf-8")
        print(f"[OK] TXT salvo: {txt_path.name}")

    # =====================================================
    # CLASSIFICAR E RENOMEAR PDF
    # =====================================================
    def classify_and_rename(self, pdf_path: Path, text: str):
        categoria = self.classifier.classify(text)

        novo_nome = f"{categoria}.pdf"
        novo_path = pdf_path.parent / novo_nome

        if novo_path.exists():
            novo_path = pdf_path.parent / f"{categoria}_{pdf_path.stem}.pdf"

        pdf_path.rename(novo_path)
        print(f"[RENOMEADO] {pdf_path.name} → {novo_path.name}")

        return novo_path, categoria


# =========================================================
# EXECUÇÃO PRINCIPAL
# =========================================================
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]
    PDF_DIR = BASE_DIR / "src" / "convert" / "arq_descompactado"

    extractor = PDFTextExtractor()

    for pdf in PDF_DIR.glob("*.pdf"):
        print(f"\n[PROCESSANDO] {pdf.name}")

        try:
            texto = extractor.extract_text_from_pdf(pdf)
            novo_pdf, categoria = extractor.classify_and_rename(pdf, texto)
            extractor.save_as_txt(novo_pdf, texto)

        except Exception as e:
            print(f"[ERRO] {pdf.name} → {e}")

    print("\n[FINALIZADO] Processamento concluído.")






