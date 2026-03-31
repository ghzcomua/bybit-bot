from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os

app = Flask(__name__)

session = HTTP(
    testnet=True,
    api_key=os.environ.get("BYBIT_API_KEY"),
    api_secret=os.environ.get("BYBIT_API_SECRET"),
)

SECRET = os.environ.get("WEBHOOK_SECRET")

def close_long(symbol):
    positions = session.get_positions(category="linear", symbol=symbol)

    for p in positions["result"]["list"]:
        if float(p["size"]) > 0 and p["side"] == "Buy":
            return session.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty=p["size"],
                reduceOnly=True
            )

    return {"msg": "No long position"}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("secret") != SECRET:
        return jsonify({"error": "wrong secret"}), 403

    if data.get("action") == "close_position":
        return jsonify(close_long(data.get("symbol")))

    return jsonify({"msg": "ignored"})

@app.route("/")
def home():
    return "Bot is running"
