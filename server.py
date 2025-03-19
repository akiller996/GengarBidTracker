import threading
import asyncio
from flask import Flask
import bot  # Importa il tuo bot

app = Flask(__name__)

@app.route('/')
def home():
    return "GengarBidTracker is running!"

def run_bot():
    asyncio.run(bot.main())  # Usa asyncio.run() per avviare il bot correttamente

if __name__ == "__main__":
    # Avvia il bot in un thread separato
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Avvia il server Flask
    app.run(host="0.0.0.0", port=5000)