import asyncio
import websockets
import requests
import json

# Replace this with the wallet you want to copy:
TARGET_WALLET = "0x509587cbb541251c74f261df3421f1fcc9fdc97c".lower()

# --- Fetch and print current open offers ---
def fetch_current_positions():
    print("\n🔍 Fetching current open offers...")

    url = f"https://api.clob.polymarket.com/api/orders?trader={TARGET_WALLET}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch open offers: {e}")
        return

    offers = response.json()
    if not offers:
        print("ℹ️ No open offers found.")
        return

    for offer in offers:
        print(f"📌 Market: {offer['marketId']}")
        print(f"➡️  Side: {'Buy' if offer['side']=='buy' else 'Sell'}")
        print(f"💵 Price: {offer['price']}")
        print(f"📦 Amount: {offer['amount']}")
        print("-" * 30)


# --- Listen to real-time trades from Polymarket WebSocket ---
async def listen_to_trades():
    url = "wss://api.clob.polymarket.com/ws"

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({
                "type": "subscribe",
                "channel": "fills"
            }))

            print("\n📡 Listening for live trades from the target wallet...\n")

            while True:
                message = await ws.recv()
                data = json.loads(message)

                if data["type"] == "fill":
                    fill = data["data"]
                    maker = fill.get("maker", "").lower()
                    taker = fill.get("taker", "").lower()

                    if maker == TARGET_WALLET or taker == TARGET_WALLET:
                        print("💰 Trade detected:")
                        print(f"🆔 Market ID: {fill['marketId']}")
                        print(f"➡️ Side: {'Buy' if fill['side'] == 'buy' else 'Sell'}")
                        print(f"📦 Amount: {fill['amount']}")
                        print(f"💵 Price: {fill['price']}")
                        print(f"🔄 Role: {'Maker' if maker == TARGET_WALLET else 'Taker'}")
                        print("-" * 40)

    except Exception as e:
        print(f"❗ WebSocket connection failed: {e}")


# --- Main ---
if __name__ == "__main__":
    fetch_current_positions()
    asyncio.run(listen_to_trades())
