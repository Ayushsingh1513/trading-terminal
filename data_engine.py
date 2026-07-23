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
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. STRATEGY & TARGETS
# ══════════════════════════════════════════════════════════════════════════════
def calculate_confluence(row, nifty_rs):
    score = 0
    if row['EMA_20'] > row['EMA_50']: score += 20
    
    dist_to_20 = abs(row['Price'] - row['EMA_20']) / row['EMA_20']
    if dist_to_20 <= 0.025: score += 30
    elif dist_to_20 <= 0.05: score += 15

    if row['Return_21'] > nifty_rs: score += 25
    if 45 <= row['RSI'] <= 65: score += 25
    
    return min(score, 100)

def calculate_targets(entry_price, atr):
    sl = round(entry_price - (atr * 1.2), 2)
    t1 = round(entry_price + (atr * 1.5), 2)
    t2 = round(entry_price + (atr * 3.5), 2)
    rr = round((t2 - entry_price) / (entry_price - sl), 1) if (entry_price - sl) > 0 else 0
    return sl, t1, t2, rr

# ══════════════════════════════════════════════════════════════════════════════
# 3. PERFORMANCE TRACKER
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
            
            if current_price >= trade['Target2']:
                trade['Status'] = 'WIN (FULL)'
                trade['Exit_Price'] = current_price
                history['closed_trades'].append(trade)
                send_telegram_alert(f"🏆 *MASSIVE WIN!*\n\n📈 *{trade['Stock']}* hit Target 2!\n💰 *Entry:* ₹{trade['Entry']} ➔ *Exit:* ₹{current_price}")
                
            elif current_price >= trade['Target1'] and not trade.get('T1_Hit', False):
                trade['T1_Hit'] = True
                trade['SL'] = trade['Entry']
                updated_active.append(trade)
                send_telegram_alert(f"🎯 *TARGET 1 HIT!*\n\n📈 *{trade['Stock']}* reached T1.\n🔒 *Action:* 50% Profit Booked. SL moved to Breakeven.")
                
            elif current_price <= trade['SL']:
                if trade.get('T1_Hit', False):
                    trade['Status'] = 'BREAKEVEN'
                    trade['Exit_Price'] = current_price
                    history['closed_trades'].append(trade)
                    send_telegram_alert(f"🛡️ *TRAILING SL HIT*\n\n📉 *{trade['Stock']}* returned to entry.\n⚖️ *Result:* Risk-Free Breakeven.")
                else:
                    trade['Status'] = 'LOSS'
                    trade['Exit_Price'] = current_price
                    history['closed_trades'].append(trade)
                    send_telegram_alert(f"🛑 *STOP LOSS HIT*\n\n📉 *{trade['Stock']}* hit SL at ₹{current_price}.")
            else:
                updated_active.append(trade)
        else:
            updated_active.append(trade)

    history['active_trades'] = updated_active

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
            send_telegram_alert(f"🚀 *NEW PULLBACK SETUP*\n\n📈 *{buy['Stock']}* showed Relative Strength on a 20-EMA Pullback!\n⚡ *Confluence:* {buy['Score']}/100\n💰 *Entry:* ₹{buy['Entry']}\n🎯 *Target 1 (Lock):* ₹{buy['Target1']}\n🎯 *Target 2 (Runner):* ₹{buy['Target2']}\n🛑 *SL:* ₹{buy['SL']}")

    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Running Full Live Data Engine...")

    nifty = yf.Ticker('^NSEI').history(period='1y')
    if nifty.empty: return
    
    nifty['Return_21'] = nifty['Close'].pct_change(21)
    nifty_rs = float(nifty['Return_21'].iloc[-1])
    current_nifty = float(nifty['Close'].iloc[-1])
    nifty_200_ema = float(nifty['Close'].ewm(span=200, adjust=False).mean().iloc[-1])

    market_payload = {
        "nifty": current_nifty,
        "nifty_chg": float((current_nifty - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2] * 100),
        "bank": 50000.0, 
        "bank_chg": 0.5,
        "vix": 14.2,     
        "vix_chg": -1.2,
        "ma200": nifty_200_ema,
        "ma50": float(nifty['Close'].ewm(span=50, adjust=False).mean().iloc[-1]),
        "mood": "BULLISH" if current_nifty > nifty_200_ema else "BEARISH",
        "mood_score": 85 if current_nifty > nifty_200_ema else 35,
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }
    with open("market_data.json", "w") as f:
        json.dump(market_payload, f, indent=4)

    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS"]
    scanner_data = []
    
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="6mo")
            if df.empty or len(df) < 50: continue
            
            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()
            df['Return_21'] = df['Close'].pct_change(21)
            df['Vol_20'] = df['Volume'].rolling(20).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))
            
            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(14).mean()

            latest = df.iloc[-1]
            price = float(latest['Close'])
            vol_surge = float(latest['Volume'] / latest['Vol_20']) if latest['Vol_20'] > 0 else 1.0
            
            row = {
                'Stock': ticker, 'Price': price, 'EMA_20': float(latest['EMA_20']),
                'EMA_50': float(latest['EMA_50']), 'Return_21': float(latest['Return_21']),
                'RSI': float(latest['RSI']), 'VolSurge': vol_surge,
                'RS': float(latest['Return_21'] * 100),
                '52W%': float(((price - df['High'].max()) / df['High'].max()) * 100),
                'Sector': 'Financials' if 'BANK' in ticker else 'Tech'
            }
            
            row['Score'] = calculate_confluence(row, nifty_rs)
            if row['Score'] >= 80:
                row['Signal'], row['Risk'], row['Setup'] = 'BUY', 'Low', 'Pullback/RS'
            elif row['Score'] >= 50:
                row['Signal'], row['Risk'], row['Setup'] = 'WATCH', 'Medium', 'Consolidating'
            else:
                row['Signal'], row['Risk'], row['Setup'] = 'AVOID', 'High', 'Weak'

            sl, t1, t2, rr = calculate_targets(price, latest['ATR'])
            row.update({'Entry': round(price, 2), 'SL': sl, 'Target1': t1, 'Target2': t2, 'RR': rr})
            scanner_data.append(row)
        except Exception:
            pass

    scanner_df = pd.DataFrame(scanner_data).sort_values(by='Score', ascending=False)
    scanner_df.to_csv("scanner_data.csv", index=False)
    track_performance_and_alert(scanner_df)

    # ══════════════════════════════════════════════════════════════════════════════
    # MARKET CLOSE SUMMARY ALERT (Runs only between 3:15 PM and 3:30 PM IST)
    # ══════════════════════════════════════════════════════════════════════════════
    current_time = datetime.now(IST)
    if current_time.hour == 15 and 15 <= current_time.minute <= 30:
        buys = scanner_df[scanner_df['Signal'] == 'BUY']
        watches = scanner_df[scanner_df['Signal'] == 'WATCH']
        
        msg = "📊 *MARKET CLOSE SUMMARY*\n\n"
        msg += "🟢 *BUY Signals:*\n"
        for _, r in buys.iterrows(): msg += f"• {r['Stock']} ({r['Score']}/100)\n"
        if buys.empty: msg += "None\n"
        
        msg += "\n🟡 *WATCH List:*\n"
        for _, r in watches.iterrows(): msg += f"• {r['Stock']} ({r['Score']}/100)\n"
        if watches.empty: msg += "None\n"
        
        send_telegram_alert(msg)

    # 3. FIX: USE ETFs INSTEAD OF INDICES FOR INDIAN SECTOR DATA
    sector_payload = []
    sector_mapping = {'Financials': 'BANKBEES.NS', 'Tech': 'ITBEES.NS'} # Extremely reliable
    
    for sec_name, symbol in sector_mapping.items():
        try:
            sdf = yf.Ticker(symbol).history(period="1y")
            if sdf.empty or len(sdf) < 65: continue
            
            latest_c = float(sdf['Close'].iloc[-1])
            today_pct = ((latest_c - float(sdf['Close'].iloc[-2])) / float(sdf['Close'].iloc[-2])) * 100
            m1_pct = ((latest_c - float(sdf['Close'].iloc[-21])) / float(sdf['Close'].iloc[-21])) * 100
            m3_pct = ((latest_c - float(sdf['Close'].iloc[-63])) / float(sdf['Close'].iloc[-63])) * 100
            w52_pct = ((latest_c - float(sdf['High'].max())) / float(sdf['High'].max())) * 100
            
            delta = sdf['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_latest = float(100 - (100 / (1 + (gain / loss))).iloc[-1])
            
            sdf['Vol_20'] = sdf['Volume'].rolling(20).mean()
            vol_20 = float(sdf['Vol_20'].iloc[-1])
            vol_punch = round(float(sdf['Volume'].iloc[-1]) / vol_20, 1) if vol_20 > 0 else 1.0

            sec_score = 50
            if rsi_latest > 60: sec_score += 20
            elif rsi_latest < 40: sec_score -= 20
            if m1_pct > 0: sec_score += 15
            if today_pct > 0: sec_score += 15
            
            sector_payload.append({
                "Sector": sec_name, "Today%": round(today_pct, 2), "1M%": round(m1_pct, 2),
                "3M%": round(m3_pct, 2), "RSI": round(rsi_latest, 1), "52W%": round(w52_pct, 2),
                "VolPunch": vol_punch, "Score": max(0, min(100, sec_score))
            })
        except Exception:
            pass

    if sector_payload:
        pd.DataFrame(sector_payload).to_csv("sector_data.csv", index=False)

if __name__ == "__main__":
    run_pipeline()
