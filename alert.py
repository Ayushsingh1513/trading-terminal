import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_trade_alert(symbol, entry, sl, target, lot_size=1):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram secrets missing.")
        return False

    msg = (
        f"TEST ALERT\n"
        f"Symbol: {symbol}\n"
        f"Entry: Rs {entry}\n"
        f"SL: Rs {sl}\n"
        f"Target: Rs {target}\n"
        f"Qty: {lot_size}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False