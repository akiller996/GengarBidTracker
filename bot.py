import os
import requests
import logging
import asyncio
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token del bot Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
EBAY_AFFILIATE_LINK = os.getenv("EBAY_AFFILIATE_LINK", "")
MYUSERAGENT = os.getenv("MYUSERAGENT")
PRICECHARTING_URL = os.getenv("PRICECHARTING_URL")
CARDMARKET_URL = os.getenv("CARDMARKET_URL")

# Lista per le notifiche delle nuove inserzioni
notifiche_utente = {}

# Funzione per cercare carte su eBay
async def cerca_carte(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Devi inserire il nome della carta da cercare!")
        return

    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=1"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            await update.message.reply_text(f"Risultati per '{query}': {url}")
        else:
            await update.message.reply_text("Errore nella ricerca su eBay.")
    except Exception as e:
        await update.message.reply_text("Errore nella richiesta.")
        logger.error(f"Errore: {e}")

# Funzione per confrontare prezzi con PriceCharting
async def confronta_pricecharting(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Devi inserire il nome della carta!")
        return

    url = f"{PRICECHARTING_URL}?q={query.replace(' ', '+')}"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        prezzo_medio = soup.find("span", class_="price").text

        await update.message.reply_text(f"Prezzo medio su PriceCharting: {prezzo_medio}")
    except Exception as e:
        await update.message.reply_text("Errore nel confronto prezzi.")
        logger.error(f"Errore: {e}")

# Funzione per confrontare prezzi con Cardmarket
async def confronta_cardmarket(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Devi inserire il nome della carta!")
        return

    url = f"{CARDMARKET_URL}?searchString={query.replace(' ', '+')}"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        prezzo_medio = soup.find("div", class_="price-container").text.strip()

        await update.message.reply_text(f"Prezzo medio su Cardmarket: {prezzo_medio}")
    except Exception as e:
        await update.message.reply_text("Errore nel confronto prezzi.")
        logger.error(f"Errore: {e}")

# Funzione per attivare notifiche su nuove inserzioni
async def attiva_notifiche(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    user_id = update.message.chat_id

    if not query:
        await update.message.reply_text("Devi inserire il nome della carta!")
        return

    if user_id not in notifiche_utente:
        notifiche_utente[user_id] = []

    notifiche_utente[user_id].append(query)
    await update.message.reply_text(f"Notifiche attivate per '{query}'.")

# Controllo nuove inserzioni su eBay (funzione asincrona)
async def controlla_nuove_inserzioni(application):
    while True:
        for user_id, queries in notifiche_utente.items():
            for query in queries:
                url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=10"
                headers = {"User-Agent": MYUSERAGENT}

                try:
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    primo_risultato = soup.find("a", class_="s-item__link")

                    if primo_risultato:
                        link = primo_risultato["href"]
                        await application.bot.send_message(user_id, f"Nuova inserzione trovata per '{query}': {link}")

                except Exception as e:
                    logger.error(f"Errore nel controllo nuove inserzioni: {e}")

        await asyncio.sleep(300)  # Controlla ogni 5 minuti

# Avvia il bot
async def main():
    # Creiamo l'applicazione
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Aggiungiamo i comandi al dispatcher
    application.add_handler(CommandHandler("cerca", cerca_carte))
    application.add_handler(CommandHandler("pricecharting", confronta_pricecharting))
    application.add_handler(CommandHandler("cardmarket", confronta_cardmarket))
    application.add_handler(CommandHandler("notifiche", attiva_notifiche))

    # Avvia il controllo delle nuove inserzioni in background
    asyncio.create_task(controlla_nuove_inserzioni(application))

    # Avvia il bot nel thread principale
    await application.run_polling()