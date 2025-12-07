from playwright.sync_api import sync_playwright, TimeoutError
import time

usuario = "marcelo.lsantos@bhub.ai"
senha = "#Marcellus@2099"

def executar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # --- LOGIN INICIAL ---
        page.goto("https://bhubhelp.zendesk.com/auth/v2/login")
        page.get_by_label("E-mail").fill(usuario)
        page.locator("input[type='password']").fill(senha)
        page.locator("#sign-in-submit-button").click()

        page.wait_for_timeout(2000)

        # --- DETECTA QUAL TELA APARECEU ---
        tela_verificacao_duas_etapas(page)
        tratar_duas_etapas(page)

        # Vai para página principal
        page.goto("https://bhubhelp.zendesk.com/agent/home/tickets")
        time.sleep(10)

        # Vai para página de filtros
        page.goto("https://bhubhelp.zendesk.com/agent/filters/36022217770651")
        print("🎉 Login concluído com sucesso!")
     
        time.sleep(10)
                # Vai para página de id
        page.goto("https://bhubhelp.zendesk.com/agent/tickets/291850")
        print("🎉 Login concluído com sucesso!")
        time.sleep(10)

        page.goto("https://bhubhelp.zendesk.com/agent/tickets/291853")
        time.sleep(10)
        page.goto("https://bhubhelp.zendesk.com/agent/tickets/291852")

        time.sleep(10)
        # Aguarda 60 segundos antes de fechar
        print("⏳ Aguardando 60 segundos antes de fechar o navegador...")
        time.sleep(60)
        browser.close()
        print("🔒 Navegador fechado.")


# ============================================================
#            FUNÇÕES PARA DETECÇÃO DE TELAS
# ============================================================

def tela_verificacao_duas_etapas(page):
    try:
        page.wait_for_selector("text=Verificação em duas etapas", timeout=3000)
        print("➡ Detectada tela de verificação 2FA.")
        return True
    except TimeoutError:
        return False

# ============================================================
#            TRATAMENTO DA TELA DE 2 ETAPAS
# ============================================================

def tratar_duas_etapas(page):
    print("⚠ Código de verificação foi solicitado.")

    codigo = esperar_codigo_usuario(120)

    if not codigo:
        print("❌ Nenhum código informado (timeout).")
        return

    page.get_by_label("Senha").fill(codigo)
    page.get_by_role("button", name="Verificar").click()
    time.sleep(20)

# ============================================================
#            TRATAMENTO DA TELA DE LOGIN EXTRA
# ============================================================

def tratar_login_extra(page, usuario, senha):

    print("Email fields:", page.get_by_label("Endereço de e-mail").count())
    print("Senha fields:", page.get_by_label("Senha").count())

    print("➡ Preenchendo tela adicional de login do Zendesk...")

    page.get_by_label("Endereço de e-mail").fill(usuario)
    time.sleep(10)

    page.locator("input#password").fill(senha)
    time.sleep(10)

    page.get_by_role("button", name="Continuar").click()
    time.sleep(60)

# ============================================================
#            ESPERA DO CÓDIGO COM TIMEOUT
# ============================================================

def esperar_codigo_usuario(timeout=120):
    print(f"⏳ Digite o código de verificação (timeout {timeout}s):")
    start = time.time()

    while time.time() - start < timeout:
        codigo = input("> Código: ").strip()
        if codigo:
            return codigo

    return None
    

# ============================================================

if __name__ == "__main__":
    executar()
