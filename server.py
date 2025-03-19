import asyncio
from flask import Flask
import bot  # Importa il tuo bot

app = Flask(__name__)

@app.route('/')
def home():
    return "GengarBidTracker is running!"

async def start_bot():
    await bot.main()  # Avvia il bot in modo asincrono

if __name__ == "__main__":
    # Avvia il bot e Flask nello stesso event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(start_bot())  # Avvia il bot come task
    app.run(host="0.0.0.0", port=5000)  # Avvia Flask