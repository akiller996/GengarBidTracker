from flask import Flask
import threading
import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot è attivo!"

def run_bot():
    bot.main()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)