import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from datetime import datetime
import pytz

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8651727429:AAG3zE6_lLHgVhJIVEzeFs2-eMY-GisSU7E"
TELEGRAM_CHAT_ID = "-1003707574219"
IST = pytz.timezone('Asia/Kolkata')

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. UPGRADED RISK & CONFLUENCE (PULLBACK + RS)
# ══════════════════════════════════════════════════════════════════════════════
def calculate_confluence(row, nifty_rs):
    score = 0
    # 1. Trend Alignment (20 pts)
    if row['EMA_20'] > row['EMA_50']: score += 20
    
    # 2. Pullback Proximity to 20 EMA (30 pts)
    dist_to_20 = abs(row['Price'] - row['EMA_20']) / row['EMA_20']
    if dist_to_20 <= 0.025: score += 30   # Within 2.5% of 20 EMA (Perfect Pullback)
    elif dist_to_20 <= 0.05: score += 15  # Within 5%

    # 3. Relative Strength vs Nifty (25 pts)
    if row['Return_21'] > nifty_rs: score += 25
    
    # 4. RSI Pullback Zone (25 pts) - Not overbought. We want 45-65.
    if 45 <= row['RSI'] <= 65: score += 25
    
    return min(score, 100)

def calculate_targets(entry_price, atr):
    # Tighter SL for pullbacks, huge runners
    sl = round(entry_price - (atr * 1.2), 2)
    t1 = round(entry_price + (atr * 1.5), 2) # Stage 1: Lock in Win
    t2 = round(entry_price + (atr * 3.5), 2) # Stage 2: Runner
    rr = round((t2 - entry_price) / (entry_price - sl), 1) if (entry_price - sl) > 0 else 0
    return sl, t1, t2, rr

# ══════════════════════════════════════════════════════════════════════════════
# 3. SMART TRAILING PERFORMANCE TRACKER
# ══════════════════════════════════════════════════════════════════════════════
def track_performance_and_alert(current_scanner_df):
    history_file = "performance_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = {"closed_trades": [], "active_trades": []}

    updated_active = []
    
    for trade in history.get("active_trades", []):
        stock_data = current_scanner_df[current_scanner_df['Stock'] == trade['Stock']]
        if not stock_data.empty:
            current_price = float(stock_data.iloc[0]['Price'])
            
            # Check Target 2 (Full Win)
            if current_price >= trade['Target2']:
                trade['Status'] = 'WIN (FULL)'
                trade['Exit_Price'] = current_price
                history['closed_trades'].append(trade)
                msg = f"🏆 *MASSIVE WIN!*\n\n📈 *{trade['Stock']}* hit Target 2!\n💰 *Entry:* ₹{trade['Entry']} ➔ *Exit:* ₹{current_price}\n🔥 *Result:* Maximum Profit Booked!"
                send_telegram_alert(msg)
                
            # Check Target 1 (Partial Win + Trailing SL)
            elif current_price >= trade['Target1'] and not trade.get('T1_Hit', False):
                trade['T1_Hit'] = True
                trade['SL'] = trade['Entry'] # Move SL to Breakeven
                updated_active.append(trade)
                msg = f"🎯 *TARGET 1 HIT!*\n\n📈 *{trade['Stock']}* reached T1.\n🔒 *Action:* 50% Profit Booked. SL moved to Breakeven (₹{trade['Entry']}). Risk-Free Trade!"
                send_telegram_alert(msg)
                
            # Check Stop Loss
            elif current_price <= trade['SL']:
                if trade.get('T1_Hit', False):
                    trade['Status'] = 'BREAKEVEN'
                    trade['Exit_Price'] = current_price
                    history['closed_trades'].append(trade)
                    msg = f"🛡️ *TRAILING SL HIT*\n\n📉 *{trade['Stock']}* returned to entry.\n💰 *Exit:* ₹{current_price}\n⚖️ *Result:* Risk-Free Breakeven (T1 profits secured)."
                    send_telegram_alert(msg)
                else:
                    trade['Status'] = 'LOSS'
                    trade['Exit_Price'] = current_price
                    history['closed_trades'].append(trade)
                    msg = f"🛑 *STOP LOSS HIT*\n\n📉 *{trade['Stock']}* hit SL.\n💰 *Entry:* ₹{trade['Entry']} ➔ *Exit:* ₹{current_price}\n🛡️ *Result:* Capital Protected."
                    send_telegram_alert(msg)
            else:
                updated_active.append(trade)
        else:
            updated_active.append(trade)

    history['active_trades'] = updated_active

    # Add New Setups
    new_buys = current_scanner_df[current_scanner_df['Signal'] == 'BUY'].to_dict('records')
    for buy in new_buys:
        if not any(t['Stock'] == buy['Stock'] for t in history['active_trades']):
            history['active_trades'].append({
                "Stock": buy["Stock"],
                "Entry": float(buy["Entry"]),
                "Target1": float(buy["Target1"]),
                "Target2": float(buy["Target2"]),
                "SL": float(buy["SL"]),
                "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Status": "ACTIVE",
                "T1_Hit": False
            })
            # Alert for New Trade
            msg = f"🚀 *NEW PULLBACK SETUP*\n\n📈 *{buy['Stock']}* showed Relative Strength on a 20-EMA Pullback!\n⚡ *Confluence:* {buy['Score']}/100\n💰 *Entry:* ₹{buy['Entry']}\n🎯 *Target 1 (Lock):* ₹{buy['Target1']}\n🎯 *Target 2 (Runner):* ₹{buy['Target2']}\n🛑 *SL:* ₹{buy['SL']}"
            send_telegram_alert(msg)

    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN DATA PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Running Upgraded Engine...")

    # 1. Nifty Baseline for Relative Strength
    nifty = yf.Ticker('^NSEI').history(period='2mo')
    if nifty.empty: return
    nifty['Return_21'] = nifty['Close'].pct_change(21)
    nifty_rs = float(nifty['Return_21'].iloc[-1])

    # 2. Stock Scanner
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS"]
    scanner_data = []
    
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="6mo")
            if df.empty or len(df) < 50: continue
            
            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()
            df['Return_21'] = df['Close'].pct_change(21)
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs_val = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs_val))
            
            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(14).mean()

            latest = df.iloc[-1]
            price = float(latest['Close'])
            
            row = {
                'Stock': ticker,
                'Price': price,
                'EMA_20': float(latest['EMA_20']),
                'EMA_50': float(latest['EMA_50']),
                'Return_21': float(latest['Return_21']),
                'RSI': float(latest['RSI']),
            }
            
            row['Score'] = calculate_confluence(row, nifty_rs)
            
            if row['Score'] >= 80:
                row['Signal'] = 'BUY'
                row['Setup'] = 'Pullback/RS'
            elif row['Score'] >= 50:
                row['Signal'] = 'WATCH'
                row['Setup'] = 'Consolidating'
            else:
                row['Signal'] = 'AVOID'
                row['Setup'] = 'Weak'

            sl, t1, t2, rr = calculate_targets(price, latest['ATR'])
            row['Entry'] = round(price, 2)
            row['SL'] = sl
            row['Target1'] = t1
            row['Target2'] = t2
            row['RR'] = rr
            
            scanner_data.append(row)
        except Exception as e:
            print(f"Error {ticker}: {e}")

    scanner_df = pd.DataFrame(scanner_data).sort_values(by='Score', ascending=False)
    scanner_df.to_csv("scanner_data.csv", index=False)
    track_performance_and_alert(scanner_df)
    print("Engine Update Complete.")

if __name__ == "__main__":
    run_pipeline()
