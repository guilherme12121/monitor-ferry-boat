import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import telebot
from datetime import datetime

# Carrega as variáveis de ambiente
load_dotenv()

USUARIO_SIGOM = os.environ.get("USUARIO_SIGOM")
SENHA_SIGOM = os.environ.get("SENHA_SIGOM")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

BUSCAS = [
    {"data": "19/06/2026", "trecho": "SÃO JOAQUIM (SALVADOR) / BOM DESPACHO (ITAPARICA)", "sentido": "Salvador ➔ Itaparica"},
    {"data": "24/06/2026", "trecho": "BOM DESPACHO (ITAPARICA) / SÃO JOAQUIM (SALVADOR)", "sentido": "Itaparica ➔ Salvador"}
]

HORARIOS_DESEJADOS = ["15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]

def enviar_notificacao(mensagem):
    try:
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        bot.send_message(TELEGRAM_CHAT_ID, mensagem)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Notificação enviada com sucesso no Telegram!")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro no Telegram: {e}")

def monitorar_travessia():
    with sync_playwright() as p:
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
            page.wait_for_timeout(3000)

            for busca in BUSCAS:
                data_atual = busca["data"]
                trecho_atual = busca["trecho"]
                sentido_atual = busca["sentido"]

                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Filtros para {data_atual} ({sentido_atual})...")
                page.evaluate('(data) => { document.getElementById("form:dataViagem_input").removeAttribute("readonly"); document.getElementById("form:dataViagem_input").value = data; }', data_atual)
                
                page.click('[id="form:trecho"] .ui-selectonemenu-trigger')
                page.wait_for_timeout(1000)
                page.click(f'li:has-text("{trecho_atual}")')
                page.click('[id="form:saveRequestButton"]')
                
                page.wait_for_timeout(6000)
                alertas_vagas = []

                for numero_pagina in range(1, 4):
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
                    mensagem = f"🚨 VAGA(S) ENCONTRADA(S) NO FERRY! 🚨\n\n🗓 Data: {data_atual}\n⛴️ Sentido: {sentido_atual}\n\n{linhas_mensagem}\n\nCorra no site para comprar!"
                    enviar_notificacao(mensagem)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma vaga em {data_atual}.")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    monitorar_travessia()
