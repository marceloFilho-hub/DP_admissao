import base64
import re
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def conectar_gmail():
    """Autentica no Gmail API e retorna o serviço."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def buscar_codigo_bhub(service):
    """Busca o código 2FA da BHub no Gmail."""
    
    print("🔎 Buscando e-mail da BHub...")

    query = 'subject:"Código de verificação de BHub"'
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=5
    ).execute()

    mensagens = results.get("messages", [])
    
    if not mensagens:
        print("❌ Nenhum e-mail encontrado com esse assunto.")
        return None

    msg_id = mensagens[0]["id"]
    mensagem = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    partes = mensagem.get("payload", {}).get("parts", [])
    corpo_email = None

    for parte in partes:
        if parte["mimeType"] in ["text/plain", "text/html"]:
            corpo_email = base64.urlsafe_b64decode(
                parte["body"].get("data", "")
            ).decode("utf-8")
            break

    if not corpo_email:
        print("❌ Não foi possível ler o corpo do e-mail.")
        return None

    match = re.search(r"\b(\d{4,8})\b", corpo_email)
    if not match:
        print("❌ Nenhum código numérico encontrado.")
        return None

    codigo = match.group(1)
    print(f"📨 Código encontrado: {codigo}")

    return codigo


def executar_conexao_gmail():
    """Conecta ao Gmail e retorna diretamente o código 2FA."""
    service = conectar_gmail()
    return buscar_codigo_bhub(service)

  

