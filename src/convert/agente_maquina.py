#maquinaOCR.py
from pathlib import Path
import json
from agenteClassificador import classificadorAPI

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_DIR = BASE_DIR / "src" / "convert" / "arq_descompactado"
FEEDBACK_DIR = BASE_DIR / "data"

# ocr_engine = OCREngine(resolution=300)
# entity_extractor = EntityExtractor()
# feedback_manager = FeedbackManager(FEEDBACK_DIR)
# classifier_service = ClassifierService(feedback_manager)

EXTENSOES = {".pdf", ".png", ".jpg", ".jpeg"}

pdfs = [
    p for p in PDF_DIR.rglob("*")
    if p.is_file() and p.suffix.lower() in EXTENSOES
]


for pdf in pdfs:
    print(f"\n[PROCESSANDO] {pdf.relative_to(PDF_DIR)}")

    classificadorAPI(pdf)

    print("Processamento concluído.")