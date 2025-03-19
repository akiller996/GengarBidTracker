from flask import Flask
import asyncio
from bot import application  # Importa direttamente l'application di Telegram

app = Flask(__name__)

@app.route('/')
def home():
    return "GengarBidTracker is running!"

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Avvia il bot e il server Flask in parallelo
    async def start():
        await application.run_polling(close_loop=False)

    loop.create_task(start())
    app.run(host="0.0.0.0", port=5000)