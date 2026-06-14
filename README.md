# ⛴️ Bot de Monitoramento - Ferry Boat Bahia

Este é um bot de automação desenvolvido em Python para monitorar a disponibilidade de vagas de veículos no sistema de travessia do Ferry Boat (Salvador - Itaparica). 

## 🚀 Funcionalidades
- Acessa o portal SIGOM da Internacional Travessias automaticamente.
- Faz login no sistema de forma silenciosa (Headless).
- Navega até a página de compra de passagens de veículos.
- Varre a tabela de horários buscando vagas maiores que zero nos horários pré-definidos.
- Envia um alerta em tempo real via **Telegram** assim que uma vaga é encontrada.

## 🛠️ Tecnologias Utilizadas
- **Python 3**
- **Playwright** (Navegação web e Web Scraping)
- **Requests** (Integração com a API do Telegram)
- **python-dotenv** (Gestão de variáveis de ambiente e segurança)

## ⚙️ Como executar localmente
1. Clone este repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Instale o navegador do Playwright: `playwright install chromium`
4. Crie um arquivo `.env` com suas credenciais (SIGOM e Telegram).
5. Execute o script: `python bot_travessia.py`