import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from telegram import Bot

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["7999272722:AAF_col3ZYUYvzZmQIwBAVbrRBbemu0ifs0"]
CHAT_ID = config["-1002874548550"]
TEMPO_ANALISE = config["15s"]
bot = Bot(token=TOKEN)

options = uc.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)

driver.get("https://www.elephantbet.co.ao/en/live-casino/home?openGames=217033-real&gameNames=Lightning%20Roulette")
time.sleep(15)

ultimos_resultados = []

def extrair_resultados():
    global ultimos_resultados
    try:
        elementos = driver.find_elements(By.CLASS_NAME, "roulette-recent-numbers__item")
        numeros = [int(e.text.strip()) for e in elementos if e.text.strip().isdigit()]
        if numeros and numeros != ultimos_resultados:
            ultimos_resultados = numeros
            return numeros[:3]
    except Exception as e:
        print("Erro ao extrair:", e)
    return None

def detectar_estrategias(numeros):
    n1, n2, n3 = numeros
    sinais = []
    u1, u2 = int(str(n1)[-1]), int(str(n2)[-1])
    soma = u1 + u2
    sub = abs(u1 - u2)
    if (str(n1)[::-1] == str(n2)) or (str(n2)[::-1] == str(n3)):
        sinais.append("🔁 Estratégia dos NÚMEROS ESPELHADOS")
    if int(str(n3)[-1]) in [soma % 10, sub % 10]:
        sinais.append("➕ Estratégia de SOMA/SUBTRAÇÃO")
    vz = [1, 5, 8, 11, 14, 23, 26, 32]
    if n1 in vz and n2 in vz and n3 not in vz:
        sinais.append("🟩 Estratégia dos VIZINHOS DO ZERO")
    terminais = [int(str(x)[-1]) for x in numeros]
    if terminais == sorted(terminais):
        sinais.append("📈 Estratégia da ESCADA")
    if abs(n1 - n2) == 2:
        sinais.append(f"📉 ESCADA INVERSA entre {n1} e {n2}")
    if n1 == n2 or n1 == n3 or n2 == n3:
        sinais.append("♻️ Estratégia de NÚMEROS REPETIDOS")
    if all(int(str(n)[-1]) in [3, 6, 9] for n in numeros):
        sinais.append("✖️ Estratégia de NÚMEROS MULTIPLICADOS")
    if n1 == n3 and n1 != n2:
        sinais.append("📛 Estratégia de DUPLOS DE REPETIÇÃO")
    if all(str(n)[-1] == "0" for n in numeros):
        sinais.append("🟩 Estratégia de TERMINAL ZERO")
    return sinais

def enviar_sinais(sinais, numeros):
    for s in sinais:
        bot.send_message(chat_id=CHAT_ID, text=f"📡 SINAL DETECTADO\n🔢 Números: {numeros}\n{s}")

def verificar_win_loss(terminal_esperado):
    time.sleep(60)
    novos = extrair_resultados()
    if novos:
        status = "✅ WIN" if int(str(novos[0])[-1]) == terminal_esperado else "❌ LOSS"
        bot.send_message(chat_id=CHAT_ID, text=f"🎯 Resultado: {novos[0]}\nStatus do sinal: {status}")

bot.send_message(chat_id=CHAT_ID, text="🤖 Bot de sinais iniciado!")
while True:
    numeros = extrair_resultados()
    if numeros:
        sinais = detectar_estrategias(numeros)
        if sinais:
            enviar_sinais(sinais, numeros)
            term_esp = int(str(numeros[2])[-1])
            verificar_win_loss(term_esp)
    time.sleep(TEMPO_ANALISE)
