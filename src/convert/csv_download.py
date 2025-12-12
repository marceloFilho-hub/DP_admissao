from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import os
import re
import requests
import webbrowser
import time

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ======================================================
# CONECTAR AO GMAIL
# ======================================================
def conectar():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ======================================================
# ABRIR LINK NO NAVEGADOR
# ======================================================
def abrir_link_no_navegador(link):
    print(f"\n🌐 Abrindo link no navegador: {link}")
    webbrowser.open(link)


# ======================================================
# BAIXAR ARQUIVO PELO LINK
# ======================================================
def baixar_arquivo(url, destino):
    print(f"⬇ Baixando arquivo de:\n{url}\n")

    resposta = requests.get(url)

    if resposta.status_code != 200:
        print(f"❌ Erro ao baixar: {resposta.status_code}")
        return None

    with open(destino, "wb") as f:
        f.write(resposta.content)

    print(f"✅ Download concluído: {destino}")
    return destino


# ======================================================
# BUSCAR EMAIL E EXTRAIR LINK
# ======================================================
def buscar_email_por_titulo(service, titulo):
    print(f"🔎 Buscando e-mails com o termo no assunto: {titulo}")

    resultado = service.users().messages().list(
        userId="me", q=f"subject:{titulo}"
    ).execute()

    mensagens = resultado.get("messages", [])

    if not mensagens:
        print("❌ Nenhum e-mail encontrado.")
        return None

    # email mais recente
    msg_id = mensagens[0]["id"]
    email = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

    partes = email["payload"]
    corpo = None

    # corpo em texto puro
    if "parts" in partes:
        for p in partes["parts"]:
            if p["mimeType"] == "text/plain" and "data" in p["body"]:
                corpo = base64.urlsafe_b64decode(
                    p["body"]["data"]
                ).decode("utf-8")
                break

    # fallback: pegar corpo direto
    if not corpo and "body" in partes and "data" in partes["body"]:
        corpo = base64.urlsafe_b64decode(
            partes["body"]["data"]
        ).decode("utf-8")

    print("\n=== CORPO DO EMAIL ===\n")
    print(corpo or "(Email sem corpo em texto puro)")

    if not corpo:
        return None

    # EXTRAIR LINK
    padrao = r"https?://[^\s]+"
    links = re.findall(padrao, corpo)

    if not links:
        print("\n❌ Nenhum link encontrado no corpo.")
        return None

    link = links[0]
    print("\n🔗 LINK ENCONTRADO:")
    print(link)

    # Abrir o link automaticamente no navegador
    abrir_link_no_navegador(link)


    return link


# ======================================================
# EXECUÇÃO PRINCIPAL
# ======================================================
def executar_download_csv(page):
    gmail = conectar()
    buscar_email_por_titulo(gmail, "CSV para")


