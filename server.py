import asyncio
import threading
from flask import Flask
import bot  # Importa il tuo bot

app = Flask(__name__)

@app.route('/')
def home():
    return "GengarBidTracker is running!"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

async def start_bot():
    await bot.main()  # Avvia il bot in modo asincrono

if __name__ == "__main__":
    # Avvia Flask in un thread separato
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Avvia il bot
    asyncio.run(start_bot())  # Esegue il bot