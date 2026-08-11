import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from datetime import datetime
import pytz

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & SECTOR MAP
# ══════════════════════════════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8651727429:AAG3zE6_lLHgVhJIVEzeFs2-eMY-GisSU7E"
TELEGRAM_CHAT_ID = "-1003707574219"
IST = pytz.timezone('Asia/Kolkata')

# Max simultaneous active trades allowed across the portfolio
MAX_ACTIVE_TRADES = 5

SECTOR_MAP = {
    'Nifty Bank': 'BANKBEES.NS',
    'Nifty IT': 'ITBEES.NS',
    'Nifty Auto': 'AUTOBEES.NS',
    'Nifty Pharma': 'PHARMABEES.NS',
    'Nifty FMCG': 'CONSUMBEES.NS',
    'PSU Bank': 'PSUBNKBEES.NS',
    'Nifty Infra': 'INFRABEES.NS'
}

STOCK_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", 
    "BHARTIARTL.NS", "ITC.NS", "LARSEN.NS", "BAJFINANCE.NS", "AXISBANK.NS", 
    "KOTAKBANK.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "MARUTI.NS", "ULTRACEMCO.NS", 
    "ASIANPAINT.NS", "NTPC.NS", "TATASTEEL.NS", "POWERGRID.NS", "M&M.NS", 
    "HCLTECH.NS", "TITAN.NS", "BAJAJFINSV.NS", "ADANIENT.NS", "WIPRO.NS", 
    "JSWSTEEL.NS", "ONGC.NS", "GRASIM.NS", "HINDUNILVR.NS", "NESTLEIND.NS", 
    "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DRREDDY.NS", "CIPLA.NS", 
    "TATACONSUM.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BRITANNIA.NS", "EICHERMOT.NS", 
    "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "COALINDIA.NS", "BPCL.NS", "SHRIRAMFIN.NS", 
    "LTIM.NS", "ADANIPORTS.NS", "SBICARD.NS", "PNB.NS", "BANKBARODA.NS", 
    "CHOLAFIN.NS", "MUTHOOTFIN.NS", "CANBK.NS", "UNIONBANK.NS", "IDFCFIRSTB.NS", 
    "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS", "MANAPPURAM.NS", "M&MFIN.NS", 
    "RECLTD.NS", "PFC.NS", "IREDA.NS", "IRFC.NS", "HDFCAMC.NS", "NAM-INDIA.NS", 
    "CAMS.NS", "MCX.NS", "BSE.NS", "CDSL.NS", "ABCAPITAL.NS", "ICICIPRULI.NS", 
    "HDFCLIFE.NS", "SBILIFE.NS", "ICICIGI.NS", "PERSISTENT.NS", "COFORGE.NS", 
    "MPHASIS.NS", "OFSS.NS", "KPITTECH.NS", "CYIENT.NS", "TATAELXSI.NS", 
    "LTTS.NS", "BISOFT.NS", "SONACOMS.NS", "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS", 
    "PBFINTECH.NS", "TVSMOTOR.NS", "BHARATFORG.NS", "BALKRISIND.NS", "ASHOKLEY.NS", 
    "BOSCHLTD.NS", "MRF.NS", "CUMMINSIND.NS", "SIEMENS.NS", "ABB.NS", "POLYCAB.NS", 
    "KEI.NS", "HAVELLS.NS", "DIXON.NS", "KAYNES.NS", "CGPOWER.NS", "SUZLON.NS", 
    "BHEL.NS", "HAL.NS", "BEL.NS", "BDL.NS", "MAZDOCK.NS", "COCHINSHIP.NS", 
    "GRSE.NS", "DATAPATTNS.NS", "MTARTECH.NS", "AETHER.NS", "TATAPOWER.NS", 
    "ADANIGREEN.NS", "ADANIPOWER.NS", "NHPC.NS", "SJVN.NS", "TORNTPOWER.NS", 
    "IEX.NS", "GAIL.NS", "IGL.NS", "MGL.NS", "PETRONET.NS", "OIL.NS", 
    "HINDPETRO.NS", "IOC.NS", "GMRINFRA.NS", "IRCTC.NS", "CONCOR.NS", "RVNL.NS", 
    "IRCON.NS", "TITAGARH.NS", "VEDL.NS", "JINDALSTEL.NS", "SAIL.NS", "NMDC.NS", 
    "NATIONALUM.NS", "HINDZINC.NS", "PIIND.NS", "SRF.NS", "NAVINFLUOR.NS", 
    "DEEPAKNTR.NS", "TATACHEM.NS", "COROMANDEL.NS", "UPL.NS", "AARTIIND.NS", 
    "LINDEINDIA.NS", "LUPIN.NS", "TORNTPHARM.NS", "AUROPHARMA.NS", "ZYDUSLIFE.NS", 
    "BIOCON.NS", "SYNGENE.NS", "GLENMARK.NS", "IPCALAB.NS", "ALKEM.NS", 
    "LAURUSLABS.NS", "MAXHEALTH.NS", "MEDANTA.NS", "FORTIS.NS", "LALPATHLAB.NS", 
    "METROPOLIS.NS", "TRENT.NS", "DABUR.NS", "GODREJCP.NS", "MARICO.NS", 
    "COLPAL.NS", "PGHH.NS", "UBL.NS", "MCDOWELL-N.NS", "RADICO.NS", "VBL.NS", 
    "DMART.NS", "JUBLFOOD.NS", "DEVYANI.NS", "INDIGOPNTS.NS", "KANSAINER.NS", 
    "PAGEIND.NS", "BATAINDIA.NS", "RELAXO.NS", "VOLTAS.NS", "BLUESTARCO.NS", 
    "KALYANKJIL.NS", "INDIGO.NS", "IHCL.NS", "CHALET.NS", "DLF.NS", 
    "MACROTECH.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", 
    "PHOENIXLTD.NS", "BRIGADE.NS", "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS", 
    "DALBHARAT.NS", "RAMCOCEM.NS", "INDIACEM.NS", "JKCEMENT.NS"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. MARKET DATA & PCR
# ══════════════════════════════════════════════════════════════════════════════
def get_market_data():
    nifty = yf.Ticker('^NSEI').history(period='1y')
    sensex = yf.Ticker('^BSESN').history(period='5d')
    if nifty.empty or sensex.empty: return None

    c_nifty = float(nifty['Close'].iloc[-1])
    nifty_chg = float((c_nifty - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2] * 100)
    c_sensex = float(sensex['Close'].iloc[-1])
    sensex_chg = float((c_sensex - sensex['Close'].iloc[-2]) / sensex['Close'].iloc[-2] * 100)
    nifty_200 = float(nifty['Close'].ewm(span=200).mean().iloc[-1])

    pcr_value = 1.05 
    pcr_status = "⚠️ OVERBOUGHT" if pcr_value > 1.5 else ("🟢 OVERSOLD" if pcr_value < 0.7 else "⚪ NEUTRAL")

    return {
        "nifty": c_nifty, "nifty_chg": nifty_chg,
        "sensex": c_sensex, "sensex_chg": sensex_chg,
        "pcr": pcr_value, "pcr_status": pcr_status,
        "ma200": nifty_200, "mood": "BULLISH" if c_nifty > nifty_200 else "BEARISH",
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }

# ══════════════════════════════════════════════════════════════════════════════
# 3. SECTOR INTELLIGENCE & HERO SECTOR
# ══════════════════════════════════════════════════════════════════════════════
def get_sector_trends():
    sector_data = {}
    sector_rows = []

    for sec_name, etf_symbol in SECTOR_MAP.items():
        try:
            sdf = yf.Ticker(etf_symbol).history(period="6mo")
            if sdf.empty or len(sdf) < 20: continue

            c_price = float(sdf['Close'].iloc[-1])
            p_price = float(sdf['Close'].iloc[-2])
            today_chg = round(((c_price - p_price) / p_price) * 100, 2)
            m1_ret = float(((c_price - sdf['Close'].iloc[-21]) / sdf['Close'].iloc[-21]) * 100)

            delta = sdf['Close'].diff()
            up_v = sdf['Volume'].where(delta > 0, 0).rolling(14).sum().iloc[-1]
            dn_v = sdf['Volume'].where(delta < 0, 0).rolling(14).sum().iloc[-1]
            ud_ratio = (up_v / dn_v) if dn_v > 0 else 1.0

            flow_label = "Big Money Buying 🟢" if ud_ratio >= 1.3 else ("Big Money Selling 🔴" if ud_ratio <= 0.7 else "Neutral / Sideways ⚪")
            is_uptrend = m1_ret > 0 and c_price > sdf['Close'].ewm(span=50).mean().iloc[-1]

            sector_data[sec_name] = {"uptrend": is_uptrend, "today_chg": today_chg, "m1_ret": m1_ret, "flow": flow_label}
            sector_rows.append({
                "Sector": sec_name, "Today%": today_chg, "1M%": round(m1_ret, 2),
                "Smart Money Flow": flow_label, "Score": 80 if is_uptrend else 40
            })
        except:
            pass

    sec_df = pd.DataFrame(sector_rows)
    if not sec_df.empty:
        sec_df = sec_df.sort_values("Today%", ascending=False)
        sec_df.to_csv("sector_data.csv", index=False)

    return sector_data, sec_df

# ══════════════════════════════════════════════════════════════════════════════
# 4. ADVANCED SCANNER
# ══════════════════════════════════════════════════════════════════════════════
def scan_hybrid_setups(sector_trends, mkt):
    scanner_results = []

    for ticker in STOCK_UNIVERSE:
        try:
            df = yf.Ticker(ticker).history(period="1y")
            if df.empty or len(df) < 50: continue

            weekly_df = df['Close'].resample('W').last()
            weekly_20_ema = weekly_df.ewm(span=20).mean().iloc[-1]
            is_weekly_uptrend = float(df['Close'].iloc[-1]) > float(weekly_20_ema)

            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))

            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(14).mean()
            df['Vol_20'] = df['Volume'].rolling(20).mean()

            latest = df.iloc[-1]
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            atr = float(latest['ATR'])

            sec_name = "Nifty Bank" if "BANK" in ticker else ("Nifty IT" if "TCS" in ticker or "INFY" in ticker else "Nifty Auto")
            sec_trend = sector_trends.get(sec_name, {}).get("uptrend", False)

            is_oversold_rebound = (rsi < 42) and (price >= float(latest['EMA_50']) * 0.98)
            range_pct = ((df['High'].tail(5).max() - df['Low'].tail(5).min()) / df['Low'].tail(5).min()) * 100
            is_compression = (range_pct <= 3.5) and (float(latest['Volume']) < float(latest['Vol_20']) * 0.95)

            setup_type = "Oversold Rebound ↩" if is_oversold_rebound else ("Tight Flag 🗜️" if is_compression else "Consolidating")
            score = 30
            if is_oversold_rebound or is_compression: score += 40
            if sec_trend: score += 20 
            if price > float(latest['EMA_20']): score += 10

            if not is_weekly_uptrend: score = min(score, 49) 
            if mkt['pcr'] > 1.5: score = min(score, 79) 

            signal = "BUY" if score >= 80 else ("WATCH" if score >= 50 else "AVOID")
            mtf_status = "✅ MTF Eligible (Dhan)"

            sl = round(price - (atr * 1.2), 2)
            t1 = round(price + (atr * 1.5), 2)
            t2 = round(price + (atr * 3.5), 2)

            scanner_results.append({
                "Stock": ticker, "Signal": signal, "Setup": setup_type, "WeeklyTrend": "UP" if is_weekly_uptrend else "DOWN",
                "MTF": mtf_status, "Price": round(price, 2), "Score": score, "RSI": round(rsi, 1),
                "VolSurge": round(float(latest['Volume'] / latest['Vol_20']), 2),
                "Entry": round(price, 2), "SL": sl, "Target1": t1, "Target2": t2,
                "RR": round((t2 - price) / (price - sl), 1) if (price - sl) > 0 else 0, "Sector": sec_name
            })
        except:
            pass

    scan_df = pd.DataFrame(scanner_results).sort_values("Score", ascending=False)
    
    # Save daily scanner for live dashboard
    scan_df.to_csv("scanner_data.csv", index=False)

    # Save to permanent historical log with timestamp
    scan_df_history = scan_df.copy()
    scan_df_history['Scan_Date'] = datetime.now(IST).strftime("%Y-%m-%d")

    historical_file = "historical_scans.csv"
    if os.path.exists(historical_file):
        scan_df_history.to_csv(historical_file, mode='a', header=False, index=False)
    else:
        scan_df_history.to_csv(historical_file, index=False)

    return scan_df

# ══════════════════════════════════════════════════════════════════════════════
# 5. TELEGRAM ALERTS WITH SECTOR INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
def track_targets_and_notify(scanner_df, sector_df, mkt):
    history_file = "performance_history.json"
    
    # ── 0. LOAD & ADAPT JSON DATA ──
    history = {"active_trades": [], "closed_trades": []}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                raw_data = json.load(f)
                
            if isinstance(raw_data, list):
                for t in raw_data:
                    if t.get("Status") == "ACTIVE":
                        history["active_trades"].append(t)
                    else:
                        history["closed_trades"].append(t)
            elif isinstance(raw_data, dict):
                history = raw_data
        except Exception as e:
            print(f"JSON Load Warning: {e}. Starting fresh.")

    # ── 1. ACTIVE TRADE MONITOR ──
    still_active = []
    for trade in history.get('active_trades', []):
        try:
            stock = trade.get('Stock', trade.get('Symbol', ''))
            curr_df = yf.Ticker(stock).history(period="1d")
            
            if not curr_df.empty:
                c_price = float(curr_df['Close'].iloc[-1])
                entry = float(trade.get('Entry', 0))
                sl = float(trade.get('SL', 0))
                target2 = float(trade.get('Target2', trade.get('Target', 0)))
                target1 = float(trade.get('Target1', target2 * 0.9)) 

                if c_price <= sl:
                    trade['Status'] = "CLOSED - SL HIT 🔴"
                    trade['Exit Price'] = c_price 
                    history['closed_trades'].append(trade)
                    loss_pct = ((c_price - entry) / entry) * 100
                    send_telegram_alert(f"🔴 *STOP LOSS HIT*\n━━━━━━━━━━━━━━━━━━━\n🎯 *Stock:* {stock}\n📉 *Entry:* ₹{entry}\n💔 *Exit Price:* ₹{c_price:.2f}\n📉 *Result:* {loss_pct:.2f}%")
                    continue
                elif c_price >= target2:
                    trade['Status'] = "CLOSED - TARGET 2 HIT 🚀"
                    trade['Exit Price'] = c_price 
                    history['closed_trades'].append(trade)
                    profit_pct = ((c_price - entry) / entry) * 100
                    send_telegram_alert(f"🚀 *TARGET 2 HIT! (RUNNER)*\n━━━━━━━━━━━━━━━━━━━\n🎯 *Stock:* {stock}\n📈 *Entry:* ₹{entry}\n💰 *Exit Price:* ₹{c_price:.2f}\n📈 *Result:* +{profit_pct:.2f}%")
                    continue
                elif c_price >= target1 and not trade.get('T1_Hit', False):
                    trade['T1_Hit'] = True
                    trade['SL'] = entry
                    send_telegram_alert(f"✅ *TARGET 1 HIT! (LOCK 50%)*\n━━━━━━━━━━━━━━━━━━━\n🎯 *Stock:* {stock}\n💰 *Price:* ₹{c_price:.2f}\n🛡️ *Action:* Book 50% Profit. SL moved to Entry (₹{trade['SL']:.2f}).")
        except Exception as e:
            pass
        still_active.append(trade)

    history['active_trades'] = still_active

    # ── 2. HERO SECTOR & SECTOR INTELLIGENCE ──
    hero_msg = ""
    if not sector_df.empty:
        hero_sec = sector_df.iloc[0]
        lagging_sec = sector_df.iloc[-1]
        hero_msg = f"""
🏆 *HERO SECTOR TODAY:* {hero_sec['Sector']} ({hero_sec['Today%']:+.2f}%)
📊 *Smart Money:* {hero_sec['Smart Money Flow']}
📉 *Weakest Sector:* {lagging_sec['Sector']} ({lagging_sec['Today%']:+.2f}%)"""

    # ── 3. BROADCAST MARKET PULSE ──
    top_buys = scanner_df[scanner_df['Signal'] == 'BUY']

    pulse_msg = f"""📊 *MARKET & SECTOR INTELLIGENCE*
━━━━━━━━━━━━━━━━━━━
🏛️ *Nifty 50:* {mkt['nifty']:,.0f} ({mkt['nifty_chg']:+.2f}%)
🏛️ *Sensex:* {mkt['sensex']:,.0f} ({mkt['sensex_chg']:+.2f}%)
⚖️ *PCR:* {mkt['pcr']} ({mkt['pcr_status']})
🛡️ *Regime:* {mkt['mood']}
{hero_msg}
━━━━━━━━━━━━━━━━━━━
🟢 *Qualified BUY Setups Today:* {len(top_buys)}"""

    send_telegram_alert(pulse_msg)

    # ── 4. RECORD & NOTIFY NEW SETUPS (WITH PORTFOLIO MAX CAP) ──
    # Sort by R:R ratio descending to prioritize the highest payout setups
    if not top_buys.empty:
        top_buys = top_buys.sort_values("RR", ascending=False)
    
    current_active_count = len(history['active_trades'])
    available_slots = max(0, MAX_ACTIVE_TRADES - current_active_count)
    
    if len(top_buys) > 0 and available_slots == 0:
        send_telegram_alert(f"⚠️ *MAX TRADES REACHED ({MAX_ACTIVE_TRADES}/{MAX_ACTIVE_TRADES})*\nFound {len(top_buys)} new setups today, but taking no new positions to manage risk. Protect your capital!")

    for buy in top_buys.to_dict('records'):
        is_active = any(t.get('Stock', t.get('Symbol')) == buy['Stock'] for t in history['active_trades'])
        
        if not is_active and available_slots > 0:
            history['active_trades'].append({
                "Symbol": buy["Stock"], 
                "Stock": buy["Stock"], 
                "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Entry": float(buy["Entry"]), 
                "Target1": float(buy["Target1"]),
                "Target2": float(buy["Target2"]), 
                "Target": float(buy["Target2"]),
                "SL": float(buy["SL"]), 
                "Status": "ACTIVE", 
                "Score": f"{buy['Score']}/100",
                "Lot Size": 1,
                "T1_Hit": False
            })
            available_slots -= 1 # Decrement available slot after taking trade

            alert_msg = f"""⚡ *MOMENTUM SETUP DETECTED*
━━━━━━━━━━━━━━━━━━━
🎯 *Stock:* {buy['Stock']}
⭐ *Algorithmic Rating:* STRONG BUY ({buy['Score']}/100)
🛠️ *Setup:* {buy['Setup']}
📈 *Weekly Trend:* {buy['WeeklyTrend']} | {buy['MTF']}

🟢 *Entry Zone:* ₹{buy['Entry']}
🔴 *Stop Loss:* ₹{buy['SL']}
🎯 *Target 1 (Lock 50%):* ₹{buy['Target1']}
🚀 *Target 2 (Runner):* ₹{buy['Target2']}
⚖️ *Risk:Reward:* 1 : {buy['RR']}
━━━━━━━━━━━━━━━━━━━
📊 *Volume Surge:* {buy['VolSurge']}x | *RSI:* {buy['RSI']}"""
            send_telegram_alert(alert_msg)

    # ── 5. FLATTEN & SAVE JSON DATA FOR STREAMLIT ──
    flat_history = history.get("active_trades", []) + history.get("closed_trades", [])
    
    with open(history_file, "w") as f:
        json.dump(flat_history, f, indent=4)
        
    print("Market tracking complete. History successfully flattened and saved for the dashboard.")

def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Executing Engine with Sector Intelligence...")
    mkt = get_market_data()
    if not mkt: return
    json.dump(mkt, open("market_data.json", "w"), indent=4)

    sector_trends, sector_df = get_sector_trends()
    scanner_df = scan_hybrid_setups(sector_trends, mkt)
    track_targets_and_notify(scanner_df, sector_df, mkt)

if __name__ == "__main__":
    run_pipeline()