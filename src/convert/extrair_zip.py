import os
import zipfile
import time
import shutil


# ======================================================
# LOCALIZA O ÚLTIMO ZIP POR PADRÃO ESPECÍFICO
# ======================================================
def encontrar_zip_recente(prefixo):
    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")

    arquivos = [
        os.path.join(pasta_downloads, f)
        for f in os.listdir(pasta_downloads)
        if f.startswith(prefixo) and f.endswith(".zip")
    ]

    if not arquivos:
        print(f"❌ Nenhum arquivo ZIP encontrado com prefixo: {prefixo}")
        return None

    # Seleciona o mais recente
    arquivo_mais_recente = max(arquivos, key=os.path.getctime)

    print(f"📦 ZIP encontrado: {arquivo_mais_recente}")
    return arquivo_mais_recente


# ======================================================
# EXTRAI O ZIP E MOVE O CSV
# ======================================================
def extrair_zip_e_mover_csv(caminho_zip, destino_csv):
    print("\n📂 Extraindo ZIP...")

    temp_extract_path = "temp_extract"

    # Limpa pasta temporária, se existir
    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)

    os.makedirs(temp_extract_path, exist_ok=True)

    # Extrair o zip
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_path)

    print("✅ ZIP extraído.")

    # Encontrar qualquer CSV dentro da extração
    csv_encontrados = []
    for root, dirs, files in os.walk(temp_extract_path):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_encontrados.append(os.path.join(root, f))

    if not csv_encontrados:
        print("❌ Nenhum CSV encontrado dentro do ZIP.")
        return None

    csv_arquivo = csv_encontrados[0]  # caso tenha mais, pega o primeiro

    print(f"📄 CSV encontrado: {csv_arquivo}")

    # Criar diretório de destino
    os.makedirs(os.path.dirname(destino_csv), exist_ok=True)

    # Mover CSV para destino
    shutil.move(csv_arquivo, destino_csv)

    print(f"✅ CSV movido para: {destino_csv}")

    # Limpar pasta temporária
    shutil.rmtree(temp_extract_path)

    return destino_csv


# ======================================================
# EXECUÇÃO PRINCIPAL
# ======================================================
def executar_extrair_zip():
    prefixo_arquivo = "_c_lula-admiss_o-rpa-view-"

    print("\n🔎 Procurando o arquivo ZIP mais recente...")

    caminho_zip = encontrar_zip_recente(prefixo_arquivo)

    if caminho_zip:
        destino_final = os.path.join("src", "convert", "csv", "tickets_aberto.csv")
        extrair_zip_e_mover_csv(caminho_zip, destino_final)