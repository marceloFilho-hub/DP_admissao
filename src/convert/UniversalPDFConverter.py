import os
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import csv

# =====================================================
# CONFIGURAÇÕES DE DIRETÓRIO (FUNCIONA EM QUALQUER PC)
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_DIR = BASE_DIR / "src" / "input_files"/ "RG"
OUTPUT_DIR = BASE_DIR / "src" / "documentos_pdf"

SUPPORTED_IMAGE_EXT = ["png", "jpg", "jpeg", "bmp", "tiff"]
SUPPORTED_TEXT_EXT = ["txt"]
SUPPORTED_CSV_EXT = ["csv"]


class UniversalPDFConverter:

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def _generate_output_path(self, input_path: str) -> Path:
        filename = Path(input_path).stem + ".pdf"
        return self.output_dir / filename

    def convert(self, filepath: str) -> Path:
        ext = Path(filepath).suffix.lower().replace(".", "")

        if ext == "pdf":
            pdf_path = self._generate_output_path(filepath)
            os.replace(filepath, pdf_path)
            return pdf_path

        if ext in SUPPORTED_IMAGE_EXT:
            return self._convert_image_to_pdf(filepath)

        if ext in SUPPORTED_TEXT_EXT:
            return self._convert_txt_to_pdf(filepath)

        if ext in SUPPORTED_CSV_EXT:
            return self._convert_csv_to_pdf(filepath)

        raise ValueError(f"Formato não suportado: {ext}")

    # =====================================================
    # 1. IMAGEM → PDF
    # =====================================================
    def _convert_image_to_pdf(self, input_path):
        pdf_path = self._generate_output_path(input_path)
        img = Image.open(input_path).convert("RGB")
        img.save(pdf_path)
        return pdf_path

    # =====================================================
    # 2. TXT → PDF
    # =====================================================
    def _convert_txt_to_pdf(self, input_path):
        pdf_path = self._generate_output_path(input_path)

        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        y = height - 40

        for line in lines:
            if y < 40:
                c.showPage()
                y = height - 40
            c.drawString(40, y, line.strip())
            y -= 20

        c.save()
        return pdf_path

    # =====================================================
    # 3. CSV → PDF
    # =====================================================
    def _convert_csv_to_pdf(self, input_path):
        pdf_path = self._generate_output_path(input_path)

        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        y = height - 40

        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                linha = " | ".join(row)
                if y < 40:
                    c.showPage()
                    y = height - 40
                c.drawString(40, y, linha)
                y -= 20

        c.save()
        return pdf_path


# =====================================================
# MÓDULO PRINCIPAL — AUTOMATIZA TUDO
# =====================================================
if __name__ == "__main__":

    print(f"[INFO] Procurando arquivos em: {INPUT_DIR}")

    converter = UniversalPDFConverter(OUTPUT_DIR)

    arquivos = list(INPUT_DIR.iterdir())

    if not arquivos:
        print("[AVISO] Nenhum arquivo encontrado em input_files.")
        exit()

    for file in arquivos:
        try:
            print(f"[PROCESSANDO] {file.name}")
            pdf_path = converter.convert(str(file))
            print(f"[OK] Gerado: {pdf_path}")

        except Exception as e:
            print(f"[ERRO] Não foi possível converter {file.name} → {e}")

    print(f"\n[TUDO CONCLUÍDO]")
    print(f"PDFs disponíveis em: {OUTPUT_DIR}")





