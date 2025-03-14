from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import requests
from ebaysdk.finding import Connection as Finding
from bs4 import BeautifulSoup
import os

# 🔑 Variabili d'ambiente (Render le leggerà in automatico)
TOKEN = os.getenv("BOT_TOKEN")
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
PRICECHARTING_API_KEY = os.getenv("PRICECHARTING_API_KEY")
USER_AGENT = os.getenv("USER_AGENT")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📌 Cerca carte Pokémon su eBay (Aste e Compralo Subito)
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

# 📌 Prezzo medio su PriceCharting
def prezzo_medio_pricecharting(nome_carta):
    url = f"https://www.pricecharting.com/api/product?t={PRICECHARTING_API_KEY}&title={nome_carta}"
    response = requests.get(url).json()
    return f"💰 Prezzo Medio PriceCharting: {response.get('price', {}).get('value', 'N/A')}€"

# 📌 Prezzo medio su Cardmarket
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

# 📌 Comando Start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Ciao! Dimmi quale carta Pokémon vuoi cercare!")

# 📌 Ricerca Carte Pokémon
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

executor.start_polling(dp)
