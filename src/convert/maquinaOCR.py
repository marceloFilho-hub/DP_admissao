#maquinaOCR.py
from pathlib import Path
import json
from classifier_service import ClassifierService
from entity_extractor import EntityExtractor
from feedback_menager import FeedbackManager
from ocr_engine import OCREngine





if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parents[2]
    PDF_DIR = BASE_DIR / "src" / "convert" / "arq_descompactado"
    FEEDBACK_DIR = BASE_DIR / "data"

    ocr_engine = OCREngine(resolution=300)
    entity_extractor = EntityExtractor()
    feedback_manager = FeedbackManager(FEEDBACK_DIR)
    classifier_service = ClassifierService(feedback_manager)

    pdfs = list(PDF_DIR.rglob("*.pdf"))

    for pdf in pdfs:
        print(f"\n[PROCESSANDO] {pdf.relative_to(PDF_DIR)}")

        try:
            ocr_result = ocr_engine.extract_text(pdf)
            texto = ocr_result["text"]

            novo_pdf, resultado = classifier_service.classify_and_rename(pdf, texto)

            campos = entity_extractor.extract(texto, resultado.categoria)


            resultado.campos = campos

            feedback_manager.registrar_campos(resultado)

            txt_path = novo_pdf.with_suffix(".txt")
            txt_path.write_text(texto, encoding="utf-8")

            json_path = novo_pdf.with_suffix(".json")
            json_path.write_text(
                json.dumps(campos, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print("[OK] Processado com sucesso")

        except Exception as e:
            print(f"[ERRO] {pdf.name} → {e}")

    print("\n[FINALIZADO] Processamento concluído.")