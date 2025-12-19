#agenteClassificador

from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_DIR = BASE_DIR / "src" / "convert" / "arq_descompactado"
FEEDBACK_DIR = BASE_DIR / "data"
PDF_PATH = list(PDF_DIR.rglob("*.pdf"))

API_URL = "https://bhubai-agents-app-392333876030.us-central1.run.app/api/v1/document_classifier/"
    
def classificadorAPI():
    for pdf in PDF_PATH:
        with pdf.open("rb") as f:
            files = {
                "file": (
                    pdf.name,
                    f,
                    "application/pdf"
                )
            }
            response = requests.post(API_URL, files=files, timeout=60)
            data = response.json()

        f.close()
        categoria = data["data"]["document_category"]
        descricao = data["data"]["document_description"]
        novo_nome = f"{categoria}_{pdf.stem}{pdf.suffix}"
        novo_caminho = pdf.with_name(novo_nome)
        pdf.rename(novo_caminho)
        print(categoria)
        
        extrair_dados(novo_caminho,data)

import json

def extrair_dados(pdf,data):

        # Criar caminho do arquivo .txt com mesmo nome do PDF
        txt_path = pdf.with_suffix(".txt")
        
        # Salvar os dados no .txt
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            json.dump(data, txt_file, ensure_ascii=False, indent=4)




if __name__ == "__main__":

    classificadorAPI()