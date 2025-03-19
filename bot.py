from flask import Flask, request, jsonify
from threading import Thread
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from ebaysdk.finding import Connection as Finding
from bs4 import BeautifulSoup

# 🔑 Variabili d'ambiente (Render le leggerà in automatico)
TOKEN = os.getenv("BOT_TOKEN")
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
USER_AGENT = os.getenv("USER_AGENT")
VERIFICATION_TOKEN = os.getenv("EBAY_VERIFICATION_TOKEN", "TOKEN_NON_IMPOSTATO")

# 📌 Avvio Flask per eBay Notifications
app = Flask(__name__)

@app.route('/ebay-notification', methods=['POST'])
def ebay_notification():
    data = request.json
    print("🔔 Notifica ricevuta:", data)  # Log della notifica

    # Se eBay sta cercando di verificare l'endpoint
    if "challenge" in data:
        print("🔑 eBay Verification Token ricevuto:", data["challenge"])
        return jsonify({"challenge": data["challenge"]}), 200

    return jsonify({"status": "success"}), 200  # Rispondi a eBay con 200 OK

# 📌 Funzioni del bot Telegram
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def cerca_carte_ebay(nome_carta):
    api = Finding(domain="svcs.ebay.com", appid=EBAY_APP_ID, config_file=None)
    risultati = {"Aste": [], "Compralo Subito": []}

    for tipo in ["Auction", "FixedPrice"]:
        response = api.execute("findItemsByKeywords", {
            "keywords": nome_carta,
            "sortOrder": "PricePlusShippingLowest",
            "itemFilter": [{"name": "ListingType", "value": tipo}]
        })

        items = response.dict().get("searchResult", {}).get("item", [])
        for item in items[:5]:  # Mostriamo solo i primi 5 risultati
            titolo = item["title"]
            prezzo = item["sellingStatus"]["currentPrice"]["value"]
            link = item["viewItemURL"]
            risultati["Aste" if tipo == "Auction" else "Compralo Subito"].append(f"{titolo} - {prezzo}€\n🔗 {link}")

    return risultati

def prezzo_medio_pricecharting(nome_carta):
    url = f"https://www.pricecharting.com/search-products?type=prices&q={nome_carta.replace(' ', '+')}"
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        prezzo = soup.find("span", class_="price").text.strip()
        return f"💰 Prezzo Medio PriceCharting: {prezzo}"
    except:
        return "❌ Prezzo non trovato su PriceCharting."

def prezzo_medio_cardmarket(nome_carta):
    url = f"https://www.cardmarket.com/en/Pokemon/Products/Singles?searchString={nome_carta}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    try:
        prezzo = soup.find("span", class_="price").text.strip()
        return f"💰 Prezzo Medio Cardmarket: {prezzo}"
    except:
        return "❌ Prezzo non trovato su Cardmarket."

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Ciao! Dimmi quale carta Pokémon vuoi cercare!")

@dp.message_handler()
async def cerca_carta(message: types.Message):
    nome_carta = message.text

    risultati_ebay = cerca_carte_ebay(nome_carta)
    pricecharting = prezzo_medio_pricecharting(nome_carta)
    cardmarket = prezzo_medio_cardmarket(nome_carta)

    risposta = f"🔎 **Risultati per {nome_carta}:**\n\n"
    risposta += f"🛒 **Aste:**\n" + "\n\n".join(risultati_ebay["Aste"]) + "\n\n"
    risposta += f"⚡ **Compralo Subito:**\n" + "\n\n".join(risultati_ebay["Compralo Subito"]) + "\n\n"
    risposta += f"{pricecharting}\n\n"
    risposta += f"{cardmarket}"

    await message.reply(risposta, parse_mode="Markdown")

# 📌 Avvio Flask in un thread separato
def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    # Avvia Flask in un thread separato
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Avvia il bot Telegram in modalità polling
    executor.start_polling(dp)