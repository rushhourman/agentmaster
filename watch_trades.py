import requests
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OpenOrderParams
from py_clob_client.clob_types import OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import os

TARGET = "0x509587cbb541251c74f261df3421f1fcc9fdc97c"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Your private key to auth CLOB

def fetch_recent_trades():
    print("\n📊 Fetching recent trades...")
    url = f"https://data-api.polymarket.com/trades?user={TARGET}&limit=10"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    trades = resp.json()
    if not trades:
        print("ℹ️ No recent trades.")
        return
    for t in trades:
        print(f"💰 {t['side']} {t['size']} '{t['title']}' @ {t['price']} — {time.ctime(t['timestamp'])}")

def fetch_open_orders():
    print("\n📌 Fetching open orders via authenticated CLOB…")
    host = "https://clob.polymarket.com"
    client = ClobClient(host, key=PRIVATE_KEY, chain_id=137)
    resp = client.get_orders(OpenOrderParams(market="", asset_id="", id=None))
    if not resp:
        print("ℹ️ No open orders found.")
        return
    for o in resp:
        print(f"📌 Market: {o.market}, Side: {o.side}, Price: {o.price}, Size: {o.original_size}, Filled: {o.size_matched}")

def main():
    fetch_recent_trades()
    fetch_open_orders()

if __name__ == "__main__":
    main()
