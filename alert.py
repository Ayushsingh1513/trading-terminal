import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8651727429:AAG3zE6_lLHgVhJIVEzeFs2-eMY-GisSU7E")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003707574219")

def send_trade_alert(symbol, entry, sl, target, lot_size=1):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
        
    msg = f"""⚡ *MANUAL TEST ALERT*
━━━━━━━━━━━━━━━━━━━
🎯 *Symbol:* {symbol}
🟢 *Entry:* ₹{entry}
🔴 *SL:* ₹{sl}
🚀 *Target:* ₹{target}
📦 *Lots:* {lot_size}
━━━━━━━━━━━━━━━━━━━"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False