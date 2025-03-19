import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configura il logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "TUO_TOKEN_BOT"

async def start(update: Update, context: CallbackContext) -> None:
    """Risponde al comando /start"""
    await update.message.reply_text("Ciao! Sono GengarBidTracker. Sono pronto per aiutarti!")

def main():
    """Avvia il bot"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    application.run_polling()

if __name__ == "__main__":
    main()