import time
from dotenv import load_dotenv
import os
from senhas import BHUB_USER, BHUB_PASS
from pathlib import Path
from playwright.sync_api import Playwright, expect
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from gmail_busca import executar_conexao_gmail


def DownloadListaTickets(page):
        #Baixa o CSV QUE VAI  SER DIRECIONADO PARA O EMAIL
    page.goto("https://bhubhelp.zendesk.com/agent/filters/36022217770651")
    page.locator("[data-test-id=\"views_views-list_item-view-36022217770651\"]").click()
    page.locator("[data-test-id=\"views_views-header-row-option-export-as-csv\"]").click()
    page.wait_for_timeout(15000)




from gmail_busca import executar_conexao_gmail

def tela_verificacao_duas_etapas(page):
    try:
        page.wait_for_selector("text=Verificação em duas etapas", timeout=3000)
        print("➡ Detectada tela de verificação 2FA.")
        tratar_duas_etapas(page)
        return True
    except:
        return False


def tratar_duas_etapas(page):
    print("⚠ Código de verificação foi solicitado...")

    codigo = executar_conexao_gmail()

    if not codigo:
        print("❌ Não foi possível obter o código 2FA.")
        return

    print(f"➡ Preenchendo o código {codigo} no campo...")
    page.get_by_label("Senha").fill(codigo)
    page.get_by_role("button", name="Verificar").click()

    page.wait_for_timeout(2000)


def login(page, usuario, senha):

    page.goto("https://bhubhelp.zendesk.com/auth/v2/login")
    page.get_by_label("E-mail").fill(usuario)
    page.locator("input[type='password']").fill(senha)
    page.locator("#sign-in-submit-button").click()
    page.wait_for_timeout(20000)


def DownloadAllAttachments(page):
 
    print("Estou  rodando a Função de Downloads dos anexos...")
    print("Passei pela linha comentada")
    text_download = page.locator(".sc-8c77jc-0").inner_text()
    print(f"Texto do botão de download: {text_download}")
    page.locator(".sc-8c77jc-0").click()


    time.sleep(2)

    save_path = Path(__file__).resolve().parent / "arq_save"
    save_path.mkdir(parents=True, exist_ok=True)


    iframe_locator = page.frame_locator("iframe[name^='app_Download-All-Attachments_ticket_sidebar']")
    btn = iframe_locator.get_by_role("button", name="Download all attachments")
    expect(btn).to_be_visible(timeout=10000)

    try:
        with page.expect_download() as download_info:

            btn.click()

        download = download_info.value
        download.save_as(str(save_path / download.suggested_filename))
        
        print("📥 Download salvo em:", save_path)
    except Exception as e:
        print("❌ Erro ao tentar baixar anexos:", str(e))
        print("Seguindo para o  próximo ticket...")




