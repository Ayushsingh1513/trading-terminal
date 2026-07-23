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

SECTOR_MAP = {
    'Financials': 'BANKBEES.NS',
    'Tech': 'ITBEES.NS',
    'Auto': 'AUTOBEES.NS',
    'Pharma': 'PHARMABEES.NS',
    'FMCG': 'CONSUMBEES.NS',
    'PSU Bank': 'PSUBNKBEES.NS'
}

STOCK_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "TATAMOTORS.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LARSEN.NS",
    "BAJFINANCE.NS", "AXISBANK.NS", "KOTAKBANK.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "ULTRACEMCO.NS", "ASIANPAINT.NS", "NTPC.NS", "TATASTEEL.NS", "POWERGRID.NS",
    "M&M.NS", "HCLTECH.NS", "TITAN.NS", "BAJAJFINSV.NS", "ADANIENT.NS"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. SECTOR TREND & SMART MONEY ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def get_sector_trends():
    sector_data = {}
    sector_rows = []
    
    for sec_name, etf_symbol in SECTOR_MAP.items():
        try:
            sdf = yf.Ticker(etf_symbol).history(period="6mo")
            if sdf.empty or len(sdf) < 20: continue
            
            c_price = float(sdf['Close'].iloc[-1])
            m1_ret = float(((c_price - sdf['Close'].iloc[-21]) / sdf['Close'].iloc[-21]) * 100)
            
            # Smart Money Up/Down Volume Ratio
            delta = sdf['Close'].diff()
            up_v = sdf['Volume'].where(delta > 0, 0).rolling(14).sum().iloc[-1]
            dn_v = sdf['Volume'].where(delta < 0, 0).rolling(14).sum().iloc[-1]
            ud_ratio = (up_v / dn_v) if dn_v > 0 else 1.0
            
            # Simplified Plain-English Label
            if ud_ratio >= 1.3:
                flow_label = "Big Money Buying 🟢"
            elif ud_ratio <= 0.7:
                flow_label = "Big Money Selling 🔴"
            else:
                flow_label = "Neutral / Sideways ⚪"

            is_uptrend = m1_ret > 0 and c_price > sdf['Close'].ewm(span=50).mean().iloc[-1]
            sector_data[sec_name] = {"uptrend": is_uptrend, "m1_ret": m1_ret, "flow": flow_label}
            
            sector_rows.append({
                "Sector": sec_name,
                "Today%": round(((c_price - sdf['Close'].iloc[-2]) / sdf['Close'].iloc[-2]) * 100, 2),
                "1M%": round(m1_ret, 2),
                "RSI": round(float(100 - (100 / (1 + (sdf['Close'].diff().where(sdf['Close'].diff() > 0, 0).rolling(14).mean().iloc[-1] / (-sdf['Close'].diff().where(sdf['Close'].diff() < 0, 0).rolling(14).mean().iloc[-1]))))), 1),
                "Smart Money Flow": flow_label,
                "VolPunch": round(float(sdf['Volume'].iloc[-1] / sdf['Volume'].rolling(20).mean().iloc[-1]), 1) if sdf['Volume'].rolling(20).mean().iloc[-1] > 0 else 1.0,
                "Score": 80 if is_uptrend else 40
            })
        except Exception:
            pass
            
    pd.DataFrame(sector_rows).to_csv("sector_data.csv", index=False)
    return sector_data

# ══════════════════════════════════════════════════════════════════════════════
# 3. HYBRID STRATEGY SCANNER (OVERSOLD + COMPRESSION + SECTOR TREND)
# ══════════════════════════════════════════════════════════════════════════════
def scan_hybrid_setups(sector_trends, nifty_rs):
    scanner_results = []
    
    for ticker in STOCK_UNIVERSE:
        try:
            df = yf.Ticker(ticker).history(period="6mo")
            if df.empty or len(df) < 50: continue
            
            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))
            
            # ATR & Volatility
            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(14).mean()
            df['Vol_20'] = df['Volume'].rolling(20).mean()
            
            latest = df.iloc[-1]
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            atr = float(latest['ATR'])
            
            sec_name = "Financials" if "BANK" in ticker or "FIN" in ticker else ("Tech" if "TCS" in ticker or "INFY" in ticker or "WIPRO" in ticker or "HCL" in ticker else "Auto")
            sec_trend = sector_trends.get(sec_name, {}).get("uptrend", False)
            
            # Strategy 3: Oversold Rebound (RSI < 42 near EMA 50/20)
            is_oversold_rebound = (rsi < 42) and (price >= float(latest['EMA_50']) * 0.98)
            
            # Strategy 5: Tight Consolidation / Compression (Range < 3.5% over last 5 days)
            recent_high = df['High'].tail(5).max()
            recent_low = df['Low'].tail(5).min()
            range_pct = ((recent_high - recent_low) / recent_low) * 100
            vol_contraction = float(latest['Volume']) < float(latest['Vol_20']) * 0.95
            is_compression = (range_pct <= 3.5) and vol_contraction
            
            setup_type = None
            score = 30
            
            if is_oversold_rebound:
                setup_type = "Oversold Rebound ↩"
                score += 40
            elif is_compression:
                setup_type = "Tight Flag / Vol Compression 🗜️"
                score += 40
                
            if sec_trend: score += 20 # Sector Trend Confluence Bonus
            if price > float(latest['EMA_20']): score += 10
            
            score = min(score, 100)
            signal = "BUY" if score >= 80 else ("WATCH" if score >= 50 else "AVOID")
            
            sl = round(price - (atr * 1.2), 2)
            t1 = round(price + (atr * 1.5), 2)
            t2 = round(price + (atr * 3.5), 2)
            rr = round((t2 - price) / (price - sl), 1) if (price - sl) > 0 else 0
            
            scanner_results.append({
                "Stock": ticker, "Signal": signal, "Setup": setup_type if setup_type else "Consolidating",
                "Risk": "Low" if score >= 80 else "Medium", "Price": round(price, 2), "Score": score,
                "RSI": round(rsi, 1), "VolSurge": round(float(latest['Volume'] / latest['Vol_20']), 2),
                "RS": round(float(df['Close'].pct_change(21).iloc[-1] * 100), 2),
                "52W%": round(float(((price - df['High'].max()) / df['High'].max()) * 100), 2),
                "Entry": round(price, 2), "SL": sl, "Target1": t1, "Target2": t2, "RR": rr,
                "Sector": sec_name
            })
        except Exception:
            pass

    scan_df = pd.DataFrame(scanner_results).sort_values("Score", ascending=False)
    scan_df.to_csv("scanner_data.csv", index=False)
    return scan_df

# ══════════════════════════════════════════════════════════════════════════════
# 4. TARGET TRACKING & TELEGRAM ALERTS
# ══════════════════════════════════════════════════════════════════════════════
def track_targets_and_notify(scanner_df, market_payload):
    history_file = "performance_history.json"
    history = json.load(open(history_file, "r")) if os.path.exists(history_file) else {"closed_trades": [], "active_trades": []}
    
    updated_active = []
    for trade in history.get("active_trades", []):
        stk_data = scanner_df[scanner_df['Stock'] == trade['Stock']]
        if not stk_data.empty:
            c_price = float(stk_data.iloc[0]['Price'])
            if c_price >= trade['Target2']:
                trade['Status'] = 'WIN (FULL)'
                history['closed_trades'].append(trade)
                send_telegram_alert(f"🏆 *TARGET 2 HIT! (FULL WIN)*\n\n📈 *{trade['Stock']}*\n💰 Entry: ₹{trade['Entry']} ➔ Exit: ₹{c_price}")
            elif c_price >= trade['Target1'] and not trade.get('T1_Hit', False):
                trade['T1_Hit'] = True
                trade['SL'] = trade['Entry']
                updated_active.append(trade)
                send_telegram_alert(f"🎯 *TARGET 1 HIT!*\n\n📈 *{trade['Stock']}*\n🔒 50% Profit Booked. SL moved to Breakeven.")
            elif c_price <= trade['SL']:
                trade['Status'] = 'LOSS' if not trade.get('T1_Hit', False) else 'BREAKEVEN'
                history['closed_trades'].append(trade)
                send_telegram_alert(f"🛑 *EXIT ALERT ({trade['Status']})*\n\n📉 *{trade['Stock']}* hit SL at ₹{c_price}")
            else:
                updated_active.append(trade)
        else:
            updated_active.append(trade)

    history['active_trades'] = updated_active

    # Send Fresh BUY Setup Notifications
    for buy in scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records'):
        if not any(t['Stock'] == buy['Stock'] for t in history['active_trades']):
            history['active_trades'].append({
                "Stock": buy["Stock"], "Entry": float(buy["Entry"]), "Target1": float(buy["Target1"]),
                "Target2": float(buy["Target2"]), "SL": float(buy["SL"]), "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Status": "ACTIVE", "T1_Hit": False
            })
            send_telegram_alert(f"🚀 *NEW SETUP DETECTED*\n\n📈 *{buy['Stock']}*\n🎯 Setup: {buy['Setup']}\n💰 Entry: ₹{buy['Entry']} | SL: ₹{buy['SL']}\n🎯 Target 1: ₹{buy['Target1']} | Target 2: ₹{buy['Target2']}")

    json.dump(history, open(history_file, "w"), indent=4)

    # Opening & Closing Market Alerts
    c_time = datetime.now(IST)
    if c_time.hour == 9 and 15 <= c_time.minute <= 30:
        send_telegram_alert(f"🔔 *MORNING MARKET OPENING VIEW*\n\n📊 *Nifty 50:* {market_payload['nifty']:,.0f} ({market_payload['nifty_chg']:+.2f}%)\n🛡️ *Regime:* {market_payload['mood']}\n⚡ *Action Plan:* Focus on sector-aligned dips.")
    elif c_time.hour == 15 and 15 <= c_time.minute <= 30:
        top_buys = scanner_df[scanner_df['Signal'] == 'BUY']
        msg = f"📊 *MARKET CLOSE SUMMARY*\n\n🟢 *Qualified BUY Setups ({len(top_buys)}):*\n"
        for _, r in top_buys.iterrows(): msg += f"• *{r['Stock']}* ({r['Setup']})\n"
        send_telegram_alert(msg if not top_buys.empty else msg + "None today.")

# ══════════════════════════════════════════════════════════════════════════════
# 5. MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Executing v2.0 Engine...")
    nifty = yf.Ticker('^NSEI').history(period='1y')
    if nifty.empty: return
    
    current_nifty = float(nifty['Close'].iloc[-1])
    nifty_200 = float(nifty['Close'].ewm(span=200).mean().iloc[-1])
    
    market_payload = {
        "nifty": current_nifty,
        "nifty_chg": float((current_nifty - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2] * 100),
        "bank": 50000.0, "bank_chg": 0.4, "vix": 13.8, "vix_chg": -0.8,
        "ma200": nifty_200, "ma50": float(nifty['Close'].ewm(span=50).mean().iloc[-1]),
        "mood": "BULLISH" if current_nifty > nifty_200 else "BEARISH",
        "mood_score": 85 if current_nifty > nifty_200 else 35,
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }
    json.dump(market_payload, open("market_data.json", "w"), indent=4)
    
    sector_trends = get_sector_trends()
    scanner_df = scan_hybrid_setups(sector_trends, float(nifty['Close'].pct_change(21).iloc[-1]))
    track_targets_and_notify(scanner_df, market_payload)
    print("Engine v2.0 execution complete.")

if __name__ == "__main__":
    run_pipeline()
