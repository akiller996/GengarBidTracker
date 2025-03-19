from flask import Flask
import threading
import asyncio
import bot  # Importa il bot per mantenerlo attivo

app = Flask(__name__)

@app.route("/")
def home():
    return "GengarBidTracker è attivo!"

# Funzione per avviare il bot in un thread separato
def run_bot():
    asyncio.run(bot.main())  # Avvia il bot Telegram senza creare un nuovo loop

# Avvia il bot in un thread separato come daemon
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)