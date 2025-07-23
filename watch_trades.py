import os, json, time, requests
from dotenv import load_dotenv
from email_utils import send_email, check_reply

# Load secrets
load_dotenv()

# --- Config ---
TARGET = os.getenv("TARGET_WALLET").lower()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # kept original
BOT_EMAIL = os.getenv("BOT_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")
MAX_RATIO = float(os.getenv("MAX_RATIO", "0.5"))
CASH_BUFFER_RATIO = float(os.getenv("CASH_BUFFER_RATIO", "0.2"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
STATE_FILE = "portfolio_state.json"

# --- State file ---
def load_state():
    return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {
        "cash": 1000.0, "positions": {}, "seen": []
    }

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"), indent=2)

# --- Data Fetch ---
def fetch_trades():
    try:
        url = f"https://data-api.polymarket.com/trades?user={TARGET}&limit=10"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"❌ Error fetching trades: {e}")
        return []

# --- Main ---
def main():
    state = load_state()
    print(f"👁️ Watching trades for {TARGET} — You have ${state['cash']} cash")

    while True:
        trades = fetch_trades()
        for tr in reversed(trades):
            tid = tr["tradeId"]
            if tid in state["seen"]:
                continue

            state["seen"].append(tid)
            title = tr["title"]
            side = tr["side"]
            qty = float(tr["size"])
            price = float(tr["price"])
            total_cost = qty * price
            symbol = title

            available_cash = state["cash"] * (1 - CASH_BUFFER_RATIO)
            adjusted_qty = min(qty * MAX_RATIO, available_cash / price)
            adjusted_cost = adjusted_qty * price

            if adjusted_cost < 0.01:
                print("💸 Not enough cash for this trade. Skipping.")
                continue

            subject = f"Trade Alert: {side.upper()} {adjusted_qty:.2f} of {symbol}"
            body = (
                f"Proposal: {side.upper()} {adjusted_qty:.2f} of '{symbol}' @ ${price:.4f}\n"
                f"Total cost: ${adjusted_cost:.2f}\n"
                f"Cash after trade: ${state['cash'] - adjusted_cost:.2f}\n\n"
                f"Reply YES to approve or NO to skip."
            )

            print(f"📧 Sending trade approval: {subject}")
            send_email(subject, body, YOUR_EMAIL, BOT_EMAIL, APP_PASSWORD)

            print("⏳ Waiting 60s for reply...")
            time.sleep(60)
            decision = check_reply(BOT_EMAIL, APP_PASSWORD, expected_subject="Trade Alert")

            if decision is None:
                print("❓ No response — skipping.")
                continue
            elif not decision:
                print("❌ Trade rejected.")
                continue

            print("✅ Approved. Executing... (simulated)")
            state["cash"] -= adjusted_cost
            pos = state["positions"].get(symbol, {"net": 0, "avg": 0})
            pos["net"] += adjusted_qty
            pos["avg"] = ((pos["avg"] * (pos["net"] - adjusted_qty)) + adjusted_cost) / pos["net"]
            state["positions"][symbol] = pos
            save_state(state)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
