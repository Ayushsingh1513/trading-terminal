import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from datetime import datetime
import pytz

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & TELEGRAM SETUP
# ══════════════════════════════════════════════════════════════════════════════
# It is best practice to store these in GitHub Repository Secrets
TELEGRAM_BOT_TOKEN = "8651727429:AAG3zE6_lLHgVhJIVEzeFs2-eMY-GisSU7E"
TELEGRAM_CHAT_ID = "-1003707574219"
IST = pytz.timezone('Asia/Kolkata')

def send_telegram_alert(message):
    """Sends a markdown-formatted message to your Telegram channel."""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Telegram Token not set. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. ALGORITHMIC SCORING & CONFLUENCE
# ══════════════════════════════════════════════════════════════════════════════
def calculate_confluence(row, market_regime_is_bullish):
    """
    4-Layer Confluence Scoring Model (Max 100 Points)
    - Layer 1: Price Action & Trend (30 pts)
    - Layer 2: Volume Surge Confirmation (25 pts)
    - Layer 3: RSI & Momentum (25 pts)
    - Layer 4: Market Regime Shield (20 pts)
    """
    score = 0
    
    # Layer 1: Price Action (Trend Alignment)
    if row['Price'] > row['EMA_20']: score += 15
    if row['Price'] > row['EMA_50']: score += 15
    
    # Layer 2: Volume Surge
    if row['VolSurge'] >= 3.0: score += 25
    elif row['VolSurge'] >= 2.0: score += 15
    elif row['VolSurge'] >= 1.2: score += 5

    # Layer 3: RSI & Momentum (Avoid overbought)
    if 55 <= row['RSI'] <= 70: score += 25
    elif 45 <= row['RSI'] < 55: score += 10
    
    # Layer 4: Market Regime (Broader market health)
    if market_regime_is_bullish: score += 20
    
    return min(score, 100)

def calculate_targets(entry_price, atr):
    """Auto-calculates SL and dual Take-Profits using ATR"""
    sl = round(entry_price - (atr * 1.5), 2)
    t1 = round(entry_price + (atr * 2.0), 2)
    t2 = round(entry_price + (atr * 3.5), 2)
    rr = round((t1 - entry_price) / (entry_price - sl), 1) if (entry_price - sl) > 0 else 0
    return sl, t1, t2, rr

# ══════════════════════════════════════════════════════════════════════════════
# 3. PERFORMANCE TRACKING LEDGER
# ══════════════════════════════════════════════════════════════════════════════
def track_performance_and_alert(current_scanner_df):
    """Tracks active trades, logs target hits, and broadcasts to Telegram."""
    history_file = "performance_history.json"
    
    # Load existing history or create a new one
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = {"closed_trades": [], "active_trades": []}

    updated_active = []
    
    # 1. Check Active Trades against Today's Prices
    for trade in history.get("active_trades", []):
        stock_data = current_scanner_df[current_scanner_df['Stock'] == trade['Stock']]
        
        if not stock_data.empty:
            current_price = stock_data.iloc[0]['Price']
            
            # 🎯 Target 1 Hit
            if current_price >= trade['Target1']:
                trade['Status'] = 'WIN'
                trade['Exit_Price'] = float(current_price)
                history['closed_trades'].append(trade)
                
                msg = f"🎯 *TARGET HIT!*\n\n📈 *{trade['Stock']}* blasted past Target 1!\n💰 *Entry:* ₹{trade['Entry']} ➔ *Current:* ₹{current_price}\n🔥 *Result:* WIN"
                send_telegram_alert(msg)
                
            # 🛑 Stop Loss Hit
            elif current_price <= trade['SL']:
                trade['Status'] = 'LOSS'
                trade['Exit_Price'] = float(current_price)
                history['closed_trades'].append(trade)
                
                msg = f"🛑 *STOP LOSS HIT*\n\n📉 *{trade['Stock']}* hit SL level.\n💰 *Entry:* ₹{trade['Entry']} ➔ *Exit:* ₹{current_price}\n🛡️ *Result:* Capital Protected."
                send_telegram_alert(msg)
                
            else:
                updated_active.append(trade) # Still active
        else:
            updated_active.append(trade)

    history['active_trades'] = updated_active

    # 2. Log Today's New STRONG BUYs into Active Trades
    new_buys = current_scanner_df[current_scanner_df['Signal'] == 'BUY'].to_dict('records')
    for buy in new_buys:
        # Only add if it's not already active
        if not any(t['Stock'] == buy['Stock'] for t in history['active_trades']):
            history['active_trades'].append({
                "Stock": buy["Stock"],
                "Entry": float(buy["Entry"]),
                "Target1": float(buy["Target1"]),
                "SL": float(buy["SL"]),
                "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Status": "ACTIVE"
            })

    # Save the updated ledger
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN DATA PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Initializing Data Engine...")

    # Fetch Broader Market Data (Nifty 50)
    nifty = yf.download('^NSEI', period='1y', interval='1d', progress=False)
    if nifty.empty:
        raise Exception("Failed to fetch Nifty data.")
    
    current_nifty = float(nifty['Close'].iloc[-1])
    nifty_200_ema = float(nifty['Close'].ewm(span=200, adjust=False).mean().iloc[-1])
    market_regime_bullish = current_nifty > nifty_200_ema

    # Export basic market JSON
    market_payload = {
        "nifty": current_nifty,
        "nifty_chg": float(nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2]) / float(nifty['Close'].iloc[-2]) * 100,
        "bank": 50000.0, # Placeholder - fetch ^NSEBANK
        "bank_chg": 0.5,
        "vix": 14.2,     # Placeholder - fetch India VIX
        "vix_chg": -1.2,
        "ma200": nifty_200_ema,
        "ma50": float(nifty['Close'].ewm(span=50, adjust=False).mean().iloc[-1]),
        "mood": "BULLISH" if market_regime_bullish else "BEARISH",
        "mood_score": 85 if market_regime_bullish else 35,
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }
    with open("market_data.json", "w") as f:
        json.dump(market_payload, f, indent=4)

    # --- STOCK SCANNER PIPELINE ---
    # In production, load your full list of NSE 500 tickers here.
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS"]
    
    scanner_data = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="6mo", progress=False)
            if df.empty or len(df) < 50:
                continue
            
            # Calculate Techincal Indicators
            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()
            df['Vol_20'] = df['Volume'].rolling(20).mean()
            
            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # ATR Calculation
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['ATR'] = true_range.rolling(14).mean()

            # Current Values
            latest = df.iloc[-1]
            price = float(latest['Close'])
            vol_surge = float(latest['Volume'] / latest['Vol_20']) if latest['Vol_20'] > 0 else 1.0
            
            # Populate Row Data
            row = {
                'Stock': ticker,
                'Price': price,
                'EMA_20': float(latest['EMA_20']),
                'EMA_50': float(latest['EMA_50']),
                'VolSurge': vol_surge,
                'RSI': float(latest['RSI']),
                'RS': float(((price - df['Close'].iloc[-20]) / df['Close'].iloc[-20]) * 100),
                '52W%': float(((price - df['High'].max()) / df['High'].max()) * 100),
                'Sector': 'Financials' if 'BANK' in ticker else 'Tech' # Example mapping
            }
            
            # Confluence Score & Signals
            row['Score'] = calculate_confluence(row, market_regime_bullish)
            
            if row['Score'] >= 80:
                row['Signal'] = 'BUY'
                row['Risk'] = 'Low'
                row['Setup'] = 'Breakout' if vol_surge > 2.0 else 'Trend'
            elif row['Score'] >= 50:
                row['Signal'] = 'WATCH'
                row['Risk'] = 'Medium'
                row['Setup'] = 'Pullback'
            else:
                row['Signal'] = 'AVOID'
                row['Risk'] = 'High'
                row['Setup'] = 'Base'

            # Risk Management
            sl, t1, t2, rr = calculate_targets(price, latest['ATR'])
            row['Entry'] = round(price, 2)
            row['SL'] = sl
            row['Target1'] = t1
            row['Target2'] = t2
            row['RR'] = rr
            
            scanner_data.append(row)
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Build and export Scanner DataFrame
    scanner_df = pd.DataFrame(scanner_data).sort_values(by='Score', ascending=False)
    scanner_df.to_csv("scanner_data.csv", index=False)

    # --- TRACK PERFORMANCE & ALERT ---
    track_performance_and_alert(scanner_df)

    # Export basic Sector mock data (Replace with real sector logic)
    sector_data = pd.DataFrame([
        {"Sector": "Financials", "Today%": 1.2, "1M%": 4.5, "3M%": 12.0, "RSI": 62, "52W%": -2.1, "VolPunch": 1.5, "Score": 85},
        {"Sector": "Tech", "Today%": -0.5, "1M%": 2.1, "3M%": -1.5, "RSI": 48, "52W%": -15.4, "VolPunch": 0.8, "Score": 40}
    ])
    sector_data.to_csv("sector_data.csv", index=False)
    
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Engine Update Complete.")

if __name__ == "__main__":
    run_pipeline()
