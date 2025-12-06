import imaplib
import email
import re
from datetime import datetime, timedelta

# CONFIGURAÇÕES DO GMAIL
GMAIL_USER = 'marcelo.lsantos@bhub.ai'
GMAIL_PASS = '#Marcellus@2099'

REMETENTE_2FA = "meajuda@bhub.ai"      # remetente fixo
ASSUNTO_2FA = "Código de verificação de BHUb"  # assunto fixo


def buscar_codigo_2fa():
    """
    Busca o código de 2FA enviado pela BHUB no Gmail.
    Retorna o código (string de 6 números) ou None.
    """

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        # --- BUSCAR APENAS E-MAILS RECEBIDOS HOJE ---
        hoje = datetime.now().strftime("%d-%b-%Y")
        status, ids = mail.search(None, f'(SINCE "{hoje}")')

        if status != "OK":
            return None

        ids = ids[0].split()

        # Processa do mais recente para o mais antigo
        for num in reversed(ids):
            status, dados = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(dados[0][1])

            # Filtra por remetente
            remetente = msg.get("From", "")
            if REMETENTE_2FA not in remetente:
                continue

            # Filtra por assunto
            assunto = msg.get("Subject", "")
            if ASSUNTO_2FA not in assunto:
                continue

            # Extrair corpo do e-mail
            if msg.is_multipart():
                corpo = ""
                for parte in msg.walk():
                    if parte.get_content_type() == "text/plain":
                        corpo += parte.get_payload(decode=True).decode()
            else:
                corpo = msg.get_payload(decode=True).decode()

            # Regex para capturar código de 6 dígitos
            codigo = re.search(r"\b\d{6}\b", corpo)
            if codigo:
                return codigo.group(0)

        return None

    except Exception as erro:
        print("Erro ao buscar código 2FA:", erro)
        return None
