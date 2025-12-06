from pathlib import Path
import pdfplumber
import easyocr
import numpy as np
import re


class PDFTextExtractor:

    def __init__(self, lang="pt", resolution=300):
        print("[INFO] Inicializando EasyOCR...")
        self.reader = easyocr.Reader([lang])
        self.resolution = resolution

    # =====================================================
    # EXTRAÇÃO DE TEXTO DO PDF (OCR + TEXTO NATIVO)
    # =====================================================
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        pdf_path = Path(pdf_path)
        full_text = ""

        with pdfplumber.open(str(pdf_path)) as pdf:
            for n, page in enumerate(pdf.pages, 1):

                print(f"[INFO] Página {n}/{len(pdf.pages)}")

                # 1 — tentativa de texto digital
                text = page.extract_text()
                if text and text.strip():
                    full_text += text + "\n"
                    continue

                # 2 — OCR
                print("[OCR] Aplicando OCR...")

                page_img = page.to_image(resolution=self.resolution)
                pil_img = page_img.annotated
                img_np = np.array(pil_img)

                ocr = self.reader.readtext(img_np, detail=0)
                full_text += "\n".join(ocr) + "\n"

        return full_text

    # =====================================================
    # SALVAR TXT
    # =====================================================
    def save_as_txt(self, pdf_path: str, text: str, output_dir=None):
        pdf_path = Path(pdf_path)

        if output_dir is None:
            output_dir = pdf_path.parent

        txt_path = Path(output_dir) / (pdf_path.stem + ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"[OK] TXT salvo em: {txt_path}")
        return txt_path


# =========================================================
# EXECUÇÃO DIRETA (MODO INDEPENDENTE)
# =========================================================
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]
    PDF_DIR = BASE_DIR / "src" / "documentos_pdf"

    print(f"[INFO] Lendo PDFs de: {PDF_DIR}")

    extractor = PDFTextExtractor()

    for pdf in PDF_DIR.glob("*.pdf"):
        print(f"\n[PROCESSANDO] {pdf.name}")
        text = extractor.extract_text_from_pdf(pdf)
        extractor.save_as_txt(pdf, text)






