from playwright.sync_api import sync_playwright, TimeoutError
import time
from playwright.sync_api import Playwright, expect
from pathlib import Path
from dotenv import load_dotenv
import os
from senhas import BHUB_USER, BHUB_PASS
from functions import DownloadAllAttachments
from functions import tela_verificacao_duas_etapas
from functions import tratar_duas_etapas
from functions import login
from functions import DownloadListaTickets
from csv_download import executar_download_csv
import pandas as pd
from extrair_zip import executar_extrair_zip
from descompact_pasta import descompact_anexos



usuario = BHUB_USER
senha = BHUB_PASS


def executar():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page, usuario, senha)

        # Function buscar código 2FA no Gmail via API
            # acessar Gmail via API
            # procurar email mais recente com assunto "Código de verificação de BHub"
            # Capturar o código de verificação no corpo do email
            # Retornar o código para a função "tratar_duas_etapas(page)"
            
        if tela_verificacao_duas_etapas(page):
            
        # Function buscar CSV no gmail e baixar anexos
         DownloadListaTickets(page)

        print("Estou buscando  o email e baixando o CSV...")
        time.sleep(5)

        executar_download_csv(page)
        print("baixei o  CSV, agora confira na pasta")
        print("Agora vou extrair o CSV do ZIP...")

        executar_extrair_zip()
        print("Extraí o CSV do ZIP, agora vou ler os IDs dos tickets...")   
        #Limpar a variavel prefixo_arquivo
        prefixo_arquivo = ""
        print("Lendo IDs dos tickets...")
        
        arquivo = "tickets_aberto.csv"
        base = pd.read_csv(os.path.join("src", "convert", "csv", arquivo), sep=",", encoding="utf-8")  
        # extrarir todos os apenas os ID da coluna "ID",s e armazenar em uma lista
        lista_ids = base["ID"].tolist()
        print(lista_ids)
        print("Agora vou baixar os anexos de cada ticket...")
        page.goto("https://bhubhelp.zendesk.com/agent/tickets/295479")
        print('adicionando o plugin de download de anexos...')

        page.locator("[data-test-id=\"omnipanel-selector-item-apps-add-appShortcuts-icon\"]").click()
        page.get_by_role("menuitem", name="Download All Attachments").click()
        page.locator("[data-test-id=\"omnipanel-selector-item-app-shortcuts\"]").click()

        
        print("Inseri o plugins de download,  confira enquanto  aguardo")
        time.sleep(30)
        print("Acessando  def DownloadAllAttachments para baixar os anexos...")
        total = len(lista_ids)
        contador = 0

        for ticket_id in lista_ids:
            contador += 1
            print(f"Baixando anexos do ticket {ticket_id} ({contador} de {total})...")

            page.goto("https://bhubhelp.zendesk.com/agent/tickets/" + str(ticket_id))

            DownloadAllAttachments(page)

            descompact_anexos()

          


if __name__ == "__main__":

    executar()

