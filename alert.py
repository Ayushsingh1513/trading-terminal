import requests

def send_trade_alert(symbol, entry, sl, target, lot_size):
    # Paste your existing bot credentials here:
    bot_token = "PASTE_YOUR_EXISTING_TOKEN_HERE"
    chat_id = "PASTE_YOUR_CHAT_ID_HERE"
    
    message = (
        f"🚨 100/100 SCORE DETECTED 🚨\n\n"
        f"📈 Symbol: {symbol}\n"
        f"🎯 Entry: ₹{entry}\n"
        f"🛑 SL: ₹{sl}\n"
        f"💰 Target: ₹{target}\n"
        f"📦 Qty/Lots: {lot_size}\n\n"
        f"⚡ Momentum Frenzy Terminal"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Telegram alert sent successfully for {symbol}!")
        else:
            print(f"Error sending alert: {response.text}")
    except Exception as e:
        print(f"Alert system failed: {e}")