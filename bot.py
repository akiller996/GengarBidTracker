import os
import requests
import logging
import threading
import time
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

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
def cerca_carte(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Devi inserire il nome della carta da cercare!")
        return

    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=1"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            update.message.reply_text(f"Risultati per '{query}': {url}")
        else:
            update.message.reply_text("Errore nella ricerca su eBay.")
    except Exception as e:
        update.message.reply_text("Errore nella richiesta.")
        logger.error(f"Errore: {e}")

# Funzione per confrontare prezzi con PriceCharting
def confronta_pricecharting(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Devi inserire il nome della carta!")
        return

    url = f"{PRICECHARTING_URL}?q={query.replace(' ', '+')}"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        prezzo_medio = soup.find("span", class_="price").text

        update.message.reply_text(f"Prezzo medio su PriceCharting: {prezzo_medio}")
    except Exception as e:
        update.message.reply_text("Errore nel confronto prezzi.")
        logger.error(f"Errore: {e}")

# Funzione per confrontare prezzi con Cardmarket
def confronta_cardmarket(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Devi inserire il nome della carta!")
        return

    url = f"{CARDMARKET_URL}?searchString={query.replace(' ', '+')}"
    headers = {"User-Agent": MYUSERAGENT}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        prezzo_medio = soup.find("div", class_="price-container").text.strip()

        update.message.reply_text(f"Prezzo medio su Cardmarket: {prezzo_medio}")
    except Exception as e:
        update.message.reply_text("Errore nel confronto prezzi.")
        logger.error(f"Errore: {e}")

# Funzione per attivare notifiche su nuove inserzioni
def attiva_notifiche(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    user_id = update.message.chat_id

    if not query:
        update.message.reply_text("Devi inserire il nome della carta!")
        return

    if user_id not in notifiche_utente:
        notifiche_utente[user_id] = []

    notifiche_utente[user_id].append(query)
    update.message.reply_text(f"Notifiche attivate per '{query}'.")

# Controllo nuove inserzioni su eBay
def controlla_nuove_inserzioni():
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
                        context.bot.send_message(user_id, f"Nuova inserzione trovata per '{query}': {link}")

                except Exception as e:
                    logger.error(f"Errore nel controllo nuove inserzioni: {e}")

        time.sleep(300)  # Controlla ogni 5 minuti

# Avvia il bot
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("cerca", cerca_carte))
    dp.add_handler(CommandHandler("pricecharting", confronta_pricecharting))
    dp.add_handler(CommandHandler("cardmarket", confronta_cardmarket))
    dp.add_handler(CommandHandler("notifiche", attiva_notifiche))

    # Avvia il controllo delle nuove inserzioni in un thread separato
    threading.Thread(target=controlla_nuove_inserzioni, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()