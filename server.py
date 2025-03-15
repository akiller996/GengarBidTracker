from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/ebay-notification', methods=['POST'])
def ebay_notification():
    data = request.json
    print("🔔 Notifica ricevuta:", data)  # Log della notifica

    return jsonify({"status": "success"}), 200  # Rispondi a eBay con 200 OK

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
