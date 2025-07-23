import asyncio
import websockets
import requests
import json

TARGET_WALLET = "0x509587cbb541251c74f261df3421f1fcc9fdc97c".lower()  # Replace

# --- Part 1: Show Current Offers (open orders) ---

def fetch_current_positions():
    print("\n🔍 Fetching current open offers...\n")

    url = f"https://clob.polymarket.com/api/orders?trader={TARGET_WALLET}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Failed to fetch open offers")
        return

    offers = response.json()
    if not offers:
        print("ℹ️ No open positions found.")
        return

    for offer in offers:
        print(f"📌 Market: {offer['marketId']}")
        print(f"➡️  Side: {'Buy' if offer['side']=='buy' else 'Sell'}")
        print(f"💵 Price: {offer['price']}")
        print(f"📦 Amount: {offer['amount']}")
        print("-" * 30)


# --- Part 2: Listen to Real-Time Trades ---

async def listen_to_trades():
    url = "wss://clob.polymarket.com/ws"

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "type": "subscribe",
            "channel": "fills"
        }))

        print("📡 Listening for live trades from the target wallet...\n")

        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)

                if data["type"] == "fill":
                    fill = data["data"]
                    maker = fill.get("maker", "").lower()
                    taker = fill.get("taker", "").lower()

                    if maker == TARGET_WALLET or taker == TARGET_WALLET:
                        print("💰 Trade detected:")
                        print(f"🆔 Market: {fill['marketId']}")
                        print(f"➡️ Side: {'Buy' if fill['side'] == 'buy' else 'Sell'}")
                        print(f"📦 Amount: {fill['amount']}")
                        print(f"💵 Price: {fill['price']}")
                        print(f"🔄 Role: {'Maker' if maker == TARGET_WALLET else 'Taker'}")
                        print("-" * 40)

            except Exception as e:
                print(f"❗ Error: {e}")
                await asyncio.sleep(5)


# --- Entry Point ---

if __name__ == "__main__":
    fetch_current_positions()
    asyncio.run(listen_to_trades())
