import asyncio
import websockets
import json

TARGET_WALLET = "0x509587cbb541251c74f261df3421f1fcc9fdc97c"

async def listen_to_trades():
    url = "wss://clob.polymarket.com/ws"

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "type": "subscribe",
            "channel": "fills"
        }))

        print("Watching trades...")

        while True:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "fill":
                fill = data["data"]
                if fill["maker"] == TARGET_WALLET or fill["taker"] == TARGET_WALLET:
                    print(f"💰 Trade detected from target wallet!")
                    print(f"Market: {fill['marketId']}")
                    print(f"Side: {'Buy' if fill['side']=='buy' else 'Sell'}")
                    print(f"Amount: {fill['amount']}")
                    print("---------")
                    # 👉 Here you would place your copy-trade logic

asyncio.run(listen_to_trades())
