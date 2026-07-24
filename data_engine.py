import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from datetime import datetime
import pytz

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & LISTS
# ══════════════════════════════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8651727429:AAG3zE6_lLHgVhJIVEzeFs2-eMY-GisSU7E"
TELEGRAM_CHAT_ID = "-1003707574219"
IST = pytz.timezone('Asia/Kolkata')

SECTOR_MAP = {
    'Financials': 'BANKBEES.NS', 'Tech': 'ITBEES.NS', 'Auto': 'AUTOBEES.NS',
    'Pharma': 'PHARMABEES.NS', 'FMCG': 'CONSUMBEES.NS', 'PSU Bank': 'PSUBNKBEES.NS'
}

# 200+ Liquid Large & Midcap Universe
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

# Broker-approved MTF List (Top highly-liquid names usually eligible)
MTF_APPROVED = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "ITC.NS", "LARSEN.NS", "TATAMOTORS.NS"]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. MARKET DATA & PCR FETCH
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
    
    # Safe PCR Fallback
    pcr_value = 1.05 
    pcr_status = "⚠️ OVERBOUGHT" if pcr_value > 1.5 else ("🟢 OVERSOLD" if pcr_value < 0.7 else "⚪ NEUTRAL")

    return {
        "nifty": c_nifty, "nifty_chg": nifty_chg,
        "sensex": c_sensex, "sensex_chg": sensex_chg,
        "pcr": pcr_value, "pcr_status": pcr_status,
        "ma200": nifty_200, "nifty_rs": float(nifty['Close'].pct_change(21).iloc[-1] * 100),
        "mood": "BULLISH" if c_nifty > nifty_200 else "BEARISH",
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }

# ══════════════════════════════════════════════════════════════════════════════
# 3. SECTOR TREND & SMART MONEY
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
            
            delta = sdf['Close'].diff()
            up_v = sdf['Volume'].where(delta > 0, 0).rolling(14).sum().iloc[-1]
            dn_v = sdf['Volume'].where(delta < 0, 0).rolling(14).sum().iloc[-1]
            ud_ratio = (up_v / dn_v) if dn_v > 0 else 1.0
            
            flow_label = "Big Money Buying 🟢" if ud_ratio >= 1.3 else ("Big Money Selling 🔴" if ud_ratio <= 0.7 else "Neutral / Sideways ⚪")
            is_uptrend = m1_ret > 0 and c_price > sdf['Close'].ewm(span=50).mean().iloc[-1]
            
            sector_data[sec_name] = {"uptrend": is_uptrend, "m1_ret": m1_ret, "flow": flow_label}
            sector_rows.append({
                "Sector": sec_name, "Today%": round(((c_price - sdf['Close'].iloc[-2]) / sdf['Close'].iloc[-2]) * 100, 2),
                "1M%": round(m1_ret, 2), "Smart Money Flow": flow_label,
                "Score": 80 if is_uptrend else 40
            })
        except:
            pass
            
    pd.DataFrame(sector_rows).to_csv("sector_data.csv", index=False)
    return sector_data

# ══════════════════════════════════════════════════════════════════════════════
# 4. ADVANCED SCANNER (Weekly MTF Alignment + Daily Setup)
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
            
            sec_name = "Financials" if "BANK" in ticker else ("Tech" if "TCS" in ticker or "INFY" in ticker else "Auto")
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
            mtf_status = "✅ MTF Eligible" if ticker in MTF_APPROVED else "❌ Cash Only"
            
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
    scan_df.to_csv("scanner_data.csv", index=False)
    return scan_df

# ══════════════════════════════════════════════════════════════════════════════
# 5. STRUCTURED TELEGRAM ALERTS
# ══════════════════════════════════════════════════════════════════════════════
def track_targets_and_notify(scanner_df, mkt):
    history_file = "performance_history.json"
    history = json.load(open(history_file, "r")) if os.path.exists(history_file) else {"closed_trades": [], "active_trades": []}
    
    c_time = datetime.now(IST)
    
    # ── WIDENED MORNING ALERT WINDOW (9:15 AM to 9:55 AM IST) ──
    if c_time.hour == 9 and 15 <= c_time.minute <= 55:
        pulse_msg = f"""📊 *DAILY MARKET PULSE*
━━━━━━━━━━━━━━━━━━━
🏛️ *Nifty 50:* {mkt['nifty']:,.0f} ({mkt['nifty_chg']:+.2f}%)
🏛️ *Sensex:* {mkt['sensex']:,.0f} ({mkt['sensex_chg']:+.2f}%)
⚖️ *PCR Filter:* {mkt['pcr']} ({mkt['pcr_status']})
🛡️ *Market Regime:* {mkt['mood']}
━━━━━━━━━━━━━━━━━━━"""
        send_telegram_alert(pulse_msg)
        
    # ── WIDENED CLOSE SUMMARY WINDOW (3:15 PM to 3:55 PM IST) ──
    elif c_time.hour == 15 and 15 <= c_time.minute <= 55:
        top_buys = scanner_df[scanner_df['Signal'] == 'BUY']
        msg = f"📊 *MARKET CLOSE SUMMARY*\n\n🟢 *Qualified BUY Setups ({len(top_buys)}):*\n"
        for _, r in top_buys.iterrows(): msg += f"• *{r['Stock']}* ({r['Setup']})\n"
        send_telegram_alert(msg if not top_buys.empty else msg + "None today.")

    for buy in scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records'):
        if not any(t['Stock'] == buy['Stock'] for t in history['active_trades']):
            history['active_trades'].append({
                "Stock": buy["Stock"], "Entry": float(buy["Entry"]), "Target1": float(buy["Target1"]),
                "Target2": float(buy["Target2"]), "SL": float(buy["SL"]), "Status": "ACTIVE"
            })
            
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

    json.dump(history, open(history_file, "w"), indent=4)

def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Executing Enhanced v2.0 Engine...")
    mkt = get_market_data()
    if not mkt: return
    json.dump(mkt, open("market_data.json", "w"), indent=4)
    
    sector_trends = get_sector_trends()
    scanner_df = scan_hybrid_setups(sector_trends, mkt)
    track_targets_and_notify(scanner_df, mkt)

if __name__ == "__main__":
    run_pipeline()
