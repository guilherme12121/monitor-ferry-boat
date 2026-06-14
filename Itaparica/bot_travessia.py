import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

# Carrega as variáveis do arquivo .env
load_dotenv()

# ==========================================
# 1. CONFIGURAÇÕES DE SEGURANÇA
# ==========================================
USUARIO_SIGOM = os.environ.get("USUARIO_SIGOM")
SENHA_SIGOM = os.environ.get("SENHA_SIGOM")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Defina a data e a lista de horários permitidos
DATA_DESEJADA = "10/06/2026"
HORARIOS_DESEJADOS = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

# ==========================================
# 2. FUNÇÕES DO BOT
# ==========================================
def enviar_notificacao(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, json=payload)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Notificação enviada com sucesso no Telegram!")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro ao enviar notificação: {e}")

def monitorar_travessia():
    with sync_playwright() as p:
        # headless=True para rodar invisível no seu computador e não atrapalhar
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Acessando o portal...")
            page.goto("https://portalsigomits.internacionaltravessias.com.br:8744/wbc-st5/ui/login.faces?uat=12", timeout=60000)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Preenchendo login...")
            page.fill('[id="frm_login_component:formLogin:username"]', USUARIO_SIGOM)
            page.fill('[id="frm_login_component:formLogin:password"]', SENHA_SIGOM)
            page.click('[id="frm_login_component:formLogin:btnConectarLogin"]')

            page.wait_for_timeout(4000)

            page.click("text=Tickets")
            page.click("text=Hora Marcada - Veículo")

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Preenchendo os filtros para {DATA_DESEJADA}...")
            
            page.evaluate('(data) => { document.getElementById("form:dataViagem_input").removeAttribute("readonly"); document.getElementById("form:dataViagem_input").value = data; }', DATA_DESEJADA)
            
            page.click('[id="form:trecho"] .ui-selectonemenu-trigger')
            page.click('li:has-text("SÃO JOAQUIM (SALVADOR) / BOM DESPACHO (ITAPARICA)")')
            
            page.click('[id="form:saveRequestButton"]')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando o site carregar os resultados...")

            page.wait_for_timeout(5000)

            alertas_vagas = []

            for numero_pagina in range(1, 4):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Lendo horários da página {numero_pagina}...")
                
                linhas = page.locator('[id="form:dataTableListaViagens"] tbody tr').all()
                
                for linha in linhas:
                    colunas = linha.locator('td').all()
                    if len(colunas) >= 5:
                        horario_tabela = colunas[2].inner_text().strip()
                        vagas_texto = colunas[4].inner_text().strip()
                        
                        vagas_disponiveis = int(vagas_texto) if vagas_texto.isdigit() else 0

                        if horario_tabela in HORARIOS_DESEJADOS and vagas_disponiveis > 0:
                            alertas_vagas.append(f"⏰ {horario_tabela} -> 🚗 Vagas: {vagas_disponiveis}")

                botao_proximo = page.locator('.ui-paginator-next').first
                classe_botao = botao_proximo.get_attribute('class') or ""
                
                if botao_proximo.count() > 0 and 'ui-state-disabled' not in classe_botao:
                    botao_proximo.click()
                    page.wait_for_timeout(3000)
                else:
                    break 

            if alertas_vagas:
                linhas_mensagem = "\n".join(alertas_vagas)
                mensagem = f"🚨 VAGA(S) ENCONTRADA(S) NO FERRY! 🚨\n\n🗓 Data: {DATA_DESEJADA}\n\n{linhas_mensagem}\n\nCorra no site para comprar!"
                enviar_notificacao(mensagem)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma vaga disponível para os horários selecionados.")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro durante a navegação: {e}")
        finally:
            browser.close()

# ==========================================
# 3. LOOP DE EXECUÇÃO LOCAL
# ==========================================
if __name__ == "__main__":
    print("Iniciando o bot de monitoramento do Ferry Boat...")
    
    mensagem_inicio = f"✅ *Bot Iniciado Localmente!*\nMonitorando vagas no Ferry Boat para o dia {DATA_DESEJADA}."
    enviar_notificacao(mensagem_inicio)

    while True:
        monitorar_travessia()
        
        tempo_espera = 300 
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando {tempo_espera // 60} minutos para a próxima checagem...\n")
        time.sleep(tempo_espera)