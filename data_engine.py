import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
import io 
import time  
from datetime import datetime
import pytz

# --- FREE AI NLP AGENT IMPORTS ---
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the AI dictionary silently
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# Inject Financial Context into the AI
financial_lexicon = {
    'upgrade': 2.0, 'upgrades': 2.0, 'downgrade': -2.0, 'downgrades': -2.0,
    'bullish': 2.0, 'bearish': -2.0, 'profit': 1.5, 'loss': -1.5,
    'beat': 1.5, 'missed': -1.5, 'dividend': 1.0, 'slashes debt': 2.0,
    'default': -3.0, 'bankruptcy': -3.0, 'record high': 2.0, 'surges': 1.5
}
sia.lexicon.update(financial_lexicon)

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & DYNAMIC UNIVERSE
# ══════════════════════════════════════════════════════════════════════════════
# Securely fetch credentials from environment variables (GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
IST = pytz.timezone('Asia/Kolkata')

TOTAL_CORPUS = 100000.0        
MAX_TRADE_CAPITAL = 50000.0    
MAX_RISK_PCT = 0.01            

SECTOR_MAP = {
    'Nifty Bank': 'BANKBEES.NS', 'Nifty IT': 'ITBEES.NS', 'Nifty Auto': 'AUTOBEES.NS',
    'Nifty Pharma': 'PHARMABEES.NS', 'Nifty FMCG': 'CONSUMBEES.NS', 
    'PSU Bank': 'PSUBNKBEES.NS', 'Nifty Infra': 'INFRABEES.NS'
}

def get_dynamic_universe():
    print("🌐 Fetching live Nifty 500 universe from NSE...")
    try:
        # Spoofing a browser to bypass NSE bot blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        tickers = [f"{symbol}.NS" for symbol in df['Symbol'].tolist()]
        print(f"✅ Successfully loaded {len(tickers)} stocks.")
        return tickers
        
    except Exception as e:
        print(f"⚠️ Failed to fetch live universe: {e}. Using Fallback.")
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
            "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LARSEN.NS", "BAJFINANCE.NS"
        ]

STOCK_UNIVERSE = get_dynamic_universe()

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Missing Telegram credentials. Check GitHub Secrets!")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Removed parse_mode="Markdown" to prevent 400 Bad Request drops due to unescaped characters in tickers
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message} 
    
    try: 
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Telegram API Error ({r.status_code}): {r.text}")
        else:
            print("✅ Telegram notification dispatched successfully.")
    except Exception as e: 
        print(f"⚠️ Telegram request failed: {e}")


def calculate_position_size(entry, sl):
    if entry <= 0 or sl >= entry: return 0
    risk_per_share = entry - sl
    max_risk_allowed = TOTAL_CORPUS * MAX_RISK_PCT
    qty_risk = int(max_risk_allowed / risk_per_share)
    qty_cap = int(MAX_TRADE_CAPITAL / entry)
    return min(qty_risk, qty_cap)

# ══════════════════════════════════════════════════════════════════════════════
# 2. FREE AI NEWSDESK AGENT (VADER NLP)
# ══════════════════════════════════════════════════════════════════════════════
def get_ai_news_sentiment(ticker):
    try:
        news_data = yf.Ticker(ticker).news
        if not news_data: 
            return 0.0, "⚪ NO NEWS FOUND"
            
        compound_score = 0
        article_count = 0
        
        for article in news_data[:4]:
            title = article.get('title', '')
            if title:
                score = sia.polarity_scores(title)['compound']
                compound_score += score
                article_count += 1
                
        if article_count == 0: return 0.0, "⚪ NEUTRAL"
        avg_score = compound_score / article_count
        
        if avg_score >= 0.15: return avg_score, "🟢 BULLISH SENTIMENT"
        elif avg_score <= -0.15: return avg_score, "🔴 BEARISH SENTIMENT"
        else: return avg_score, "⚪ NEUTRAL SENTIMENT"
    except:
        return 0.0, "⚪ NEUTRAL (FETCH ERROR)"

# ══════════════════════════════════════════════════════════════════════════════
# 3. BULL & BEAR DEBATE ENGINE + JUDGE AGENT
# ══════════════════════════════════════════════════════════════════════════════
def run_ai_debate_and_judge(buy_setup, news_score, news_label, mkt):
    bull_reasons = []
    bear_reasons = []
    bull_score = 0
    bear_score = 0

    if buy_setup['Score'] >= 80:
        bull_score += 4
        bull_reasons.append(f"High technical conviction ({buy_setup['Score']}/100 score)")
    if buy_setup['VolSurge'] >= 1.2:
        bull_score += 2
        bull_reasons.append(f"Institutional volume surge ({buy_setup['VolSurge']}x 20-day avg)")
    if buy_setup['WeeklyTrend'] == "UP":
        bull_score += 2
        bull_reasons.append("Aligned with high-timeframe (Weekly) Uptrend")
    if news_score > 0.1:
        bull_score += 2
        bull_reasons.append(f"Positive news flow ({news_label})")

    if news_score < -0.1:
        bear_score += 4
        bear_reasons.append(f"Negative news headlines ({news_label})")
    if mkt['pcr'] > 1.3:
        bear_score += 2
        bear_reasons.append(f"Market structure indicates caution/fear ({mkt['pcr_status']})")
    if buy_setup['RSI'] > 65:
        bear_score += 2
        bear_reasons.append(f"Near-term RSI elevated ({buy_setup['RSI']})")
    if buy_setup['RR'] < 1.5:
        bear_score += 2
        bear_reasons.append(f"Tight Risk-to-Reward ratio (1:{buy_setup['RR']})")

    if not bull_reasons: bull_reasons.append("Base technical breakout pattern")
    if not bear_reasons: bear_reasons.append("Standard market volatility risk")

    total_points = max(1, bull_score + bear_score)
    
    if bull_score >= bear_score:
        winner = "Bull"
        verdict_status = "BUY SIGNAL"
        confidence = min(10, max(5, round((bull_score / total_points) * 10)))
    else:
        winner = "Bear"
        verdict_status = "VETO / WATCHLIST"
        confidence = min(10, max(5, round((bear_score / total_points) * 10)))

    return {
        "verdict": verdict_status,
        "winner": winner,
        "confidence": confidence,
        "bull_case": " - ".join(bull_reasons),
        "bear_case": " - ".join(bear_reasons)
    }

# ══════════════════════════════════════════════════════════════════════════════
# 4. MARKET DATA & SECTOR INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
def get_market_data():
    nifty = yf.Ticker('^NSEI').history(period='1y')
    sensex = yf.Ticker('^BSESN').history(period='5d')
    vix_data = yf.Ticker('^INDIAVIX').history(period='5d')
    
    if nifty.empty or sensex.empty: return None

    c_nifty = float(nifty['Close'].iloc[-1])
    nifty_chg = float((c_nifty - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2] * 100)
    c_sensex = float(sensex['Close'].iloc[-1])
    sensex_chg = float((c_sensex - sensex['Close'].iloc[-2]) / sensex['Close'].iloc[-2] * 100)
    nifty_200 = float(nifty['Close'].ewm(span=200).mean().iloc[-1])
    
    current_vix = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 15.0
    
    if current_vix > 18.0:
        pcr_status = f"HIGH FEAR (VIX: {current_vix:.1f})"
        synthetic_pcr = 1.6 
    elif current_vix < 11.0:
        pcr_status = f"COMPLACENT (VIX: {current_vix:.1f})"
        synthetic_pcr = 0.8
    else:
        pcr_status = f"NEUTRAL (VIX: {current_vix:.1f})"
        synthetic_pcr = 1.0

    return {
        "nifty": c_nifty, "nifty_chg": nifty_chg, "sensex": c_sensex, "sensex_chg": sensex_chg,
        "pcr": synthetic_pcr, "pcr_status": pcr_status, "ma200": nifty_200, "vix": current_vix,
        "mood": "BULLISH" if c_nifty > nifty_200 else "BEARISH",
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %I:%M %p IST")
    }

def get_sector_trends():
    sector_data = {}
    sector_rows = []
    for sec_name, etf_symbol in SECTOR_MAP.items():
        time.sleep(1) 
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
            flow_label = "Big Money Buying" if ud_ratio >= 1.3 else ("Big Money Selling" if ud_ratio <= 0.7 else "Neutral / Sideways")
            is_uptrend = m1_ret > 0 and c_price > sdf['Close'].ewm(span=50).mean().iloc[-1]
            sector_data[sec_name] = {"uptrend": is_uptrend, "today_chg": today_chg, "m1_ret": m1_ret, "flow": flow_label}
            sector_rows.append({"Sector": sec_name, "Today%": today_chg, "1M%": round(m1_ret, 2), "Smart Money Flow": flow_label, "Score": 80 if is_uptrend else 40})
        except: pass
    sec_df = pd.DataFrame(sector_rows)
    if not sec_df.empty: sec_df.sort_values("Today%", ascending=False).to_csv("sector_data.csv", index=False)
    return sector_data, sec_df

def scan_hybrid_setups(sector_trends, mkt):
    scanner_results = []
    for ticker in STOCK_UNIVERSE:
        time.sleep(1) 
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
            
            vol_surge = float(latest['Volume'] / latest['Vol_20']) if float(latest['Vol_20']) > 0 else 0
            is_conqueror = (
                is_compression 
                and vol_surge > 1.8 
                and sec_trend       
                and rsi > 60        
            )

            if is_conqueror:
                setup_type = "Conqueror"
            elif is_oversold_rebound:
                setup_type = "Oversold Rebound"
            elif is_compression:
                setup_type = "Tight Flag"
            else:
                setup_type = "Consolidating"
                
            score = 30
            if is_conqueror: score += 50
            elif is_oversold_rebound or is_compression: score += 40
            if sec_trend: score += 20 
            if price > float(latest['EMA_20']): score += 10
            if not is_weekly_uptrend: score = min(score, 49) 
            if mkt['pcr'] > 1.5: score = min(score, 79) 

            signal = "BUY" if score >= 80 else ("WATCH" if score >= 50 else "AVOID")
            sl = round(price - (atr * 1.2), 2)
            t1 = round(price + (atr * 1.5), 2)
            t2 = round(price + (atr * 3.5), 2)

            scanner_results.append({
                "Stock": ticker, "Signal": signal, "Setup": setup_type, "WeeklyTrend": "UP" if is_weekly_uptrend else "DOWN",
                "MTF": "MTF Eligible", "Price": round(price, 2), "Score": score, "RSI": round(rsi, 1),
                "VolSurge": round(vol_surge, 2), "Entry": round(price, 2), 
                "SL": sl, "Target1": t1, "Target2": t2, "RR": round((t2 - price) / (price - sl), 1) if (price - sl) > 0 else 0, 
                "Sector": sec_name
            })
        except: pass
    scan_df = pd.DataFrame(scanner_results).sort_values("Score", ascending=False)
    scan_df.to_csv("scanner_data.csv", index=False)
    return scan_df

# ══════════════════════════════════════════════════════════════════════════════
# 5. EXECUTION & MULTI-AGENT TELEGRAM NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
def track_targets_and_notify(scanner_df, sector_df, mkt):
    history_file = "performance_history.json"
    history = {"active_trades": [], "closed_trades": []}
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f: raw_data = json.load(f)
            if isinstance(raw_data, list):
                for t in raw_data:
                    status = str(t.get("Status", ""))
                    if "ACTIVE" in status or "WATCHLIST" in status: history["active_trades"].append(t)
                    else: history["closed_trades"].append(t)
            elif isinstance(raw_data, dict): history = raw_data
        except: pass

    still_active = []
    for trade in history.get('active_trades', []):
        time.sleep(1) 
        try:
            stock = trade.get('Stock', trade.get('Symbol', ''))
            curr_df = yf.Ticker(stock).history(period="1d")
            entry, sl = float(trade.get('Entry', 0)), float(trade.get('SL', 0))
            target2 = float(trade.get('Target2', trade.get('Target', 0)))
            target1 = float(trade.get('Target1', target2 * 0.9))
            is_watchlist = "WATCHLIST" in str(trade.get('Status', ''))

            if not curr_df.empty:
                c_close = float(curr_df['Close'].iloc[-1])
                c_low = float(curr_df['Low'].iloc[-1])
                c_high = float(curr_df['High'].iloc[-1])
                
                if c_low <= sl:
                    c_open = float(curr_df['Open'].iloc[-1])
                    exit_price = c_open if c_open < sl else sl
                    
                    trade['Exit Price'] = exit_price 
                    trade['Status'] = "WATCHLIST - SL HIT" if is_watchlist else "CLOSED - SL HIT"
                    if not is_watchlist: send_telegram_alert(f"STOP LOSS HIT\n{stock} Exit: Rs {exit_price:.2f}")
                    history['closed_trades'].append(trade)
                    continue
                
                elif c_high >= target2:
                    trade['Exit Price'] = target2 
                    trade['Status'] = "WATCHLIST - TARGET 2 HIT" if is_watchlist else "CLOSED - TARGET 2 HIT"
                    if not is_watchlist: send_telegram_alert(f"TARGET 2 HIT! (RUNNER)\n{stock} Exit: Rs {target2:.2f}")
                    history['closed_trades'].append(trade)
                    continue
                
                elif c_high >= target1 and not trade.get('T1_Hit', False):
                    trade['T1_Hit'] = True
                    trade['SL'] = entry
                    if not is_watchlist: send_telegram_alert(f"TARGET 1 HIT! (LOCK 50%)\n{stock} Price: Rs {c_high:.2f}\nSL moved to Entry.")
            
            still_active.append(trade)
        except: still_active.append(trade)

    history['active_trades'] = still_active
    top_buys = scanner_df[scanner_df['Signal'] == 'BUY'].copy()
    if not top_buys.empty: top_buys = top_buys.sort_values(by=["Score", "RR"], ascending=[False, False])
    
    ai_vetoed_stocks = []

    for buy in top_buys.to_dict('records'):
        stock = buy['Stock']
        entry, sl = float(buy["Entry"]), float(buy["SL"])
        if any(t.get('Stock', t.get('Symbol')) == stock for t in history['active_trades']): continue

        required_qty = calculate_position_size(entry, sl)
        if required_qty <= 0: required_qty = 1 
        required_margin = required_qty * entry
        
        time.sleep(1) 
        news_score, news_label = get_ai_news_sentiment(stock)

        debate_result = run_ai_debate_and_judge(buy, news_score, news_label, mkt)

        if debate_result['winner'].startswith("Bear") or news_score <= -0.15:
            history['active_trades'].append({
                "Symbol": stock, "Stock": stock, "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Entry": entry, "Target1": float(buy["Target1"]), "Target2": float(buy["Target2"]), 
                "Target": float(buy["Target2"]), "SL": sl, "Status": f"WATCHLIST ({news_label})", 
                "Score": f"{buy['Score']}/100", "Lot Size": 0, "T1_Hit": False
            })
            ai_vetoed_stocks.append(stock)
            continue 
            
        history['active_trades'].append({
            "Symbol": stock, "Stock": stock, "Date": datetime.now(IST).strftime("%Y-%m-%d"),
            "Entry": entry, "Target1": float(buy["Target1"]), "Target2": float(buy["Target2"]), 
            "Target": float(buy["Target2"]), "SL": sl, "Status": "ACTIVE", 
            "Score": f"{buy['Score']}/100", "Lot Size": required_qty, "T1_Hit": False
        })

        alert_msg = f"""STOCK RESEARCH BOT — {stock}
-------------------
Verdict: {debate_result['verdict']} | Confidence: {debate_result['confidence']}/10
Debate Winner: {debate_result['winner']}

Bull Case: {debate_result['bull_case']}
Bear Caveat: {debate_result['bear_case']}

Entry Zone: Rs {entry}
Stop Loss: Rs {sl}
Target: Rs {buy['Target2']} (1:{buy['RR']} R:R)
-------------------
Paper Capital: Rs {required_margin:,.2f} ({required_qty} shares)"""
        send_telegram_alert(alert_msg)

    if ai_vetoed_stocks:
        send_telegram_alert(f"AI JUDGE VETO: TRADES WATCHLISTED\nDebate lost to Bear case on: {', '.join(ai_vetoed_stocks)}.")

    flat_history = history.get("active_trades", []) + history.get("closed_trades", [])
    with open(history_file, "w") as f: json.dump(flat_history, f, indent=4)
    print("Multi-Agent Debate Engine Complete.")

def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Executing Multi-Agent Engine...")
    mkt = get_market_data()
    if mkt:
        sector_trends, sector_df = get_sector_trends()
        scanner_df = scan_hybrid_setups(sector_trends, mkt)
        track_targets_and_notify(scanner_df, sector_df, mkt)
        
        # Ping Telegram with a summary to confirm execution
        buy_count = len(scanner_df[scanner_df['Signal'] == 'BUY'])
        send_telegram_alert(f"Momentum Scan Completed!\nScanned: {len(scanner_df)} stocks\nBuy Setups Found: {buy_count}\nMarket Mood: {mkt['mood']}")

if __name__ == "__main__":
    run_pipeline()