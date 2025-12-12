import os
import zipfile
import time
import shutil


# ======================================================
# LOCALIZA TODOS OS ZIP NA PASTA
# ======================================================
def encontre_zips(pasta_origem):
    arquivos = [
        os.path.join(pasta_origem, f)
        for f in os.listdir(pasta_origem)
        if f.endswith(".zip")
    ]

    if not arquivos:
        print(f"❌ Nenhum arquivo ZIP encontrado em: {pasta_origem}")
        return None

    # Ordena por data (mais recentes primeiro)
    arquivos.sort(key=os.path.getctime, reverse=True)
    
    print(f"📦 {len(arquivos)} arquivo(s) ZIP encontrado(s):")
    for arq in arquivos:
        print(f"   - {os.path.basename(arq)}")
    
    return arquivos


# ======================================================
# EXTRAI O ZIP E RENOMEIA A PASTA (14 PRIMEIROS DIGITOS)
# ======================================================
def extrair_zip_preservando_pasta(caminho_zip, pasta_destino):

    # Nome do arquivo sem extensão
    nome_zip = os.path.splitext(os.path.basename(caminho_zip))[0]

    # Novo nome baseado nos 14 primeiros caracteres
    novo_nome_pasta = nome_zip[:14]

    # Caminho final já renomeado
    destino_final = os.path.join(pasta_destino, novo_nome_pasta)
    os.makedirs(destino_final, exist_ok=True)

    print(f"\n📂 Extraindo '{nome_zip}' → Pasta final: {novo_nome_pasta}")

    # Extrair diretamente para a pasta final
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(destino_final)

    print("✅ Estrutura extraída com sucesso!")


# ======================================================
# EXECUÇÃO PRINCIPAL
# ======================================================
def descompact_anexos():
    pasta_origem = os.path.join("src", "convert", "arq_save")
    pasta_destino = os.path.join("src", "convert", "arq_descompactado")

    print("\n🔎 Procurando todos os arquivos ZIP...")

    arquivos_zip = encontre_zips(pasta_origem)

    if arquivos_zip:
        for caminho_zip in arquivos_zip:
            extrair_zip_preservando_pasta(caminho_zip, pasta_destino)
        
        # Limpar a pasta de origem após descompactar tudo
        print(f"\n🗑️  Limpando pasta: {pasta_origem}")
        if os.path.exists(pasta_origem):
            shutil.rmtree(pasta_origem)
            os.makedirs(pasta_origem, exist_ok=True)
            print(f"✅ Pasta {pasta_origem} limpa!")
    else:
        print("⚠️  Nenhum ZIP foi processado.")


if __name__ == "__main__":
    descompact_anexos()


