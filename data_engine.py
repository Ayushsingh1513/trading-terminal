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
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message} 
    try: 
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Telegram API Error ({r.status_code}): {r.text}")
    except Exception as e: 
        print(f"⚠️ Telegram request failed: {e}")

def calculate_position_size(entry, sl):
    if pd.isna(entry) or pd.isna(sl) or entry <= 0 or sl >= entry: return 0
    risk_per_share = entry - sl
    if risk_per_share <= 0: return 0
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
        if not news_data: return 0.0, "⚪ NO NEWS FOUND"
        compound_score, article_count = 0, 0
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
    bull_reasons, bear_reasons = [], []
    bull_score, bear_score = 0, 0

    if buy_setup['Score'] >= 80:
        bull_score += 4
        bull_reasons.append(f"High technical conviction ({buy_setup['Score']}/100 score)")
    if buy_setup['VolSurge'] >= 1.5:
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
        bear_reasons.append(f"Market structure indicates fear/caution ({mkt['pcr_status']})")
    if buy_setup['RSI'] > 75:
        bear_score += 2
        bear_reasons.append(f"Near-term RSI highly overbought ({buy_setup['RSI']})")
    if buy_setup['RR'] < 1.5:
        bear_score += 2
        bear_reasons.append(f"Tight Risk-to-Reward ratio (1:{buy_setup['RR']})")

    if not bull_reasons: bull_reasons.append("Base technical setup")
    if not bear_reasons: bear_reasons.append("Standard market volatility risk")

    total_points = max(1, bull_score + bear_score)
    if bull_score >= bear_score:
        return {"verdict": "BUY SIGNAL", "winner": "Bull", "confidence": min(10, max(5, round((bull_score / total_points) * 10))), "bull_case": " - ".join(bull_reasons), "bear_case": " - ".join(bear_reasons)}
    else:
        return {"verdict": "VETO / WATCHLIST", "winner": "Bear", "confidence": min(10, max(5, round((bear_score / total_points) * 10))), "bull_case": " - ".join(bull_reasons), "bear_case": " - ".join(bear_reasons)}

# ══════════════════════════════════════════════════════════════════════════════
# 4. MARKET DATA & SECTOR INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
def get_market_data():
    nifty = yf.Ticker('^NSEI').history(period='1y')
    vix_data = yf.Ticker('^INDIAVIX').history(period='5d')
    if nifty.empty: return None

    c_nifty = float(nifty['Close'].iloc[-1])
    nifty_200 = float(nifty['Close'].ewm(span=200).mean().iloc[-1])
    current_vix = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 15.0
    
    if current_vix > 18.0: pcr_status, synthetic_pcr = f"HIGH FEAR (VIX: {current_vix:.1f})", 1.6 
    elif current_vix < 11.0: pcr_status, synthetic_pcr = f"COMPLACENT (VIX: {current_vix:.1f})", 0.8
    else: pcr_status, synthetic_pcr = f"NEUTRAL (VIX: {current_vix:.1f})", 1.0

    return {"nifty": c_nifty, "pcr": synthetic_pcr, "pcr_status": pcr_status, "mood": "BULLISH" if c_nifty > nifty_200 else "BEARISH"}

def get_sector_trends():
    sector_data = {}
    for sec_name, etf_symbol in SECTOR_MAP.items():
        time.sleep(0.5) 
        try:
            sdf = yf.Ticker(etf_symbol).history(period="6mo")
            if sdf.empty or len(sdf) < 20: continue
            c_price = float(sdf['Close'].iloc[-1])
            sector_data[sec_name] = {"uptrend": c_price > sdf['Close'].ewm(span=50).mean().iloc[-1]}
        except: pass
    return sector_data, pd.DataFrame()

def scan_hybrid_setups(sector_trends, mkt):
    scanner_results = []
    for ticker in STOCK_UNIVERSE:
        time.sleep(0.8) 
        try:
            df = yf.Ticker(ticker).history(period="1y")
            if df.empty or len(df) < 200: continue
            
            weekly_20_ema = df['Close'].resample('W').last().ewm(span=20).mean().iloc[-1]
            is_weekly_uptrend = float(df['Close'].iloc[-1]) > float(weekly_20_ema)
            
            # --- CALCULATE EMAS ---
            df['EMA_9'] = df['Close'].ewm(span=9).mean()
            df['EMA_20'] = df['Close'].ewm(span=20).mean()
            df['EMA_50'] = df['Close'].ewm(span=50).mean()
            df['EMA_200'] = df['Close'].ewm(span=200).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))
            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
            df['ATR'] = df['TR'].rolling(14).mean()
            df['Vol_20'] = df['Volume'].rolling(20).mean()

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            atr = float(latest['ATR'])
            vol_surge = float(latest['Volume'] / latest['Vol_20']) if float(latest['Vol_20']) > 0 else 0
            high_52w = float(df['High'].max())

            sec_name = "Nifty Bank" if "BANK" in ticker else ("Nifty IT" if "TCS" in ticker or "INFY" in ticker else "Nifty Auto")
            sec_trend = sector_trends.get(sec_name, {}).get("uptrend", False)
            range_pct = ((df['High'].tail(10).max() - df['Low'].tail(10).min()) / df['Low'].tail(10).min()) * 100

            # ─── STRICT CONFLUENCE MATRIX ───
            is_trend_aligned = (price > float(latest['EMA_50'])) and (price > float(latest['EMA_200']))
            
            is_golden = (price >= high_52w * 0.95) and (vol_surge > 2.0) and (rsi > 60) and is_trend_aligned
            is_vcp = (range_pct <= 4.0) and (vol_surge > 2.0) and (price > float(latest['EMA_20'])) and is_trend_aligned
            
            ema_dist = abs(price - float(latest['EMA_20'])) / float(latest['EMA_20'])
            is_ema_pullback = (ema_dist <= 0.015) and (45 < rsi < 60) and sec_trend and is_trend_aligned
            
            ema9_today, ema20_today = float(latest['EMA_9']), float(latest['EMA_20'])
            ema9_prev, ema20_prev = float(prev['EMA_9']), float(prev['EMA_20'])
            is_crossover = (ema9_prev <= ema20_prev) and (ema9_today > ema20_today) and (vol_surge > 1.5) and is_trend_aligned

            if is_golden: setup_type, score = "Golden Momentum 🏆", 95
            elif is_vcp: setup_type, score = "VCP Breakout 📈", 90
            elif is_crossover: setup_type, score = "9/20 EMA Crossover ⚔️", 88
            elif is_ema_pullback: setup_type, score = "EMA Pullback 🧲", 85
            else: continue

            signal = "BUY"
            sl = round(price - (atr * 1.5), 2)
            t1 = round(price + (atr * 1.5), 2)
            t2 = round(price + (atr * 4.0), 2)

            scanner_results.append({
                "Stock": ticker, "Signal": signal, "Setup": setup_type, "WeeklyTrend": "UP" if is_weekly_uptrend else "DOWN",
                "MTF": "MTF Eligible", "Price": round(price, 2), "Score": score, "RSI": round(rsi, 1),
                "VolSurge": round(vol_surge, 2), "Entry": round(price, 2), 
                "SL": sl, "Target1": t1, "Target2": t2, "RR": round((t2 - price) / (price - sl), 1) if (price - sl) > 0 else 0, 
                "Sector": sec_name
            })
        except: pass

    scan_df = pd.DataFrame(scanner_results)
    if not scan_df.empty:
        # THE SNIPER RULE: ONLY KEEP THE TOP 5
        scan_df = scan_df.sort_values(by=["Score", "RR"], ascending=[False, False]).head(5)
    
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
        time.sleep(0.8) 
        try:
            stock = trade.get('Stock', trade.get('Symbol', ''))
            curr_df = yf.Ticker(stock).history(period="1d")
            entry, sl = float(trade.get('Entry', 0)), float(trade.get('SL', 0))
            target2 = float(trade.get('Target2', trade.get('Target', 0)))
            target1 = float(trade.get('Target1', target2 * 0.9))
            is_watchlist = "WATCHLIST" in str(trade.get('Status', ''))

            if not curr_df.empty:
                c_low, c_high = float(curr_df['Low'].iloc[-1]), float(curr_df['High'].iloc[-1])
                
                if c_low <= sl:
                    c_open = float(curr_df['Open'].iloc[-1])
                    exit_price = c_open if c_open < sl else sl
                    trade['Exit Price'] = exit_price 
                    trade['Status'] = "WATCHLIST - SL HIT" if is_watchlist else "CLOSED - SL HIT"
                    if not is_watchlist: send_telegram_alert(f"🛑 STOP LOSS HIT\n{stock} Exit: Rs {exit_price:.2f}")
                    history['closed_trades'].append(trade)
                    continue
                elif c_high >= target2:
                    trade['Exit Price'] = target2 
                    trade['Status'] = "WATCHLIST - TARGET 2 HIT" if is_watchlist else "CLOSED - TARGET 2 HIT"
                    if not is_watchlist: send_telegram_alert(f"🚀 TARGET 2 HIT! (RUNNER)\n{stock} Exit: Rs {target2:.2f}")
                    history['closed_trades'].append(trade)
                    continue
                elif c_high >= target1 and not trade.get('T1_Hit', False):
                    trade['T1_Hit'] = True
                    trade['SL'] = entry
                    if not is_watchlist: send_telegram_alert(f"✅ TARGET 1 HIT! (LOCK 50%)\n{stock} Price: Rs {c_high:.2f}\nSL moved to Entry.")
            still_active.append(trade)
        except: still_active.append(trade)

    history['active_trades'] = still_active
    
    # STRICT FILTER for Execution Engine
    top_buys = scanner_df[
        scanner_df['Signal'].isin(['BUY', 'WATCH']) & 
        scanner_df['Setup'].str.contains('Golden|VCP|EMA|Crossover', case=False, na=False)
    ].copy()
    
    if not top_buys.empty: top_buys = top_buys.sort_values(by=["Score", "RR"], ascending=[False, False])
    
    for buy in top_buys.to_dict('records'):
        stock = buy['Stock']
        entry, sl = float(buy["Entry"]), float(buy["SL"])
        if any(t.get('Stock', t.get('Symbol')) == stock for t in history['active_trades']): continue

        required_qty = max(1, calculate_position_size(entry, sl))
        required_margin = required_qty * entry
        
        time.sleep(1) 
        news_score, news_label = get_ai_news_sentiment(stock)
        debate_result = run_ai_debate_and_judge(buy, news_score, news_label, mkt)

        if debate_result['winner'].startswith("Bear") or news_score <= -0.15:
            history['active_trades'].append({
                "Symbol": stock, "Stock": stock, "Date": datetime.now(IST).strftime("%Y-%m-%d"),
                "Entry": entry, "Target1": float(buy.get("Target1", 0)), 
                "Target2": float(buy.get("Target2", 0)), 
                "Target": float(buy.get("Target2", 0)), 
                "SL": sl, "Status": f"WATCHLIST ({news_label})", 
                "Score": f"{buy['Score']}/100", "Lot Size": 0, "T1_Hit": False
            })
            
            veto_msg = f"""🛑 AI JUDGE VETO — {stock}
-------------------
Verdict: SENT TO SHADOW WATCHLIST
Debate Winner: {debate_result['winner']} ({debate_result['confidence']}/10)
Setup Type: {buy['Setup']}

Why it was rejected:
{debate_result['bear_case']}

News Sentiment: {news_label}
-------------------
Action: Margins set to Rs 0."""
            send_telegram_alert(veto_msg)
            continue 
            
        history['active_trades'].append({
            "Symbol": stock, "Stock": stock, "Date": datetime.now(IST).strftime("%Y-%m-%d"),
            "Entry": entry, "Target1": float(buy["Target1"]), "Target2": float(buy["Target2"]), 
            "Target": float(buy["Target2"]), "SL": sl, "Status": "ACTIVE", 
            "Score": f"{buy['Score']}/100", "Lot Size": required_qty, "T1_Hit": False
        })
        
        if "Golden" in buy['Setup']: header_msg = f"🏆 52-WEEK HIGH MOMENTUM — {stock}"
        elif "VCP" in buy['Setup']: header_msg = f"📈 VCP BREAKOUT DETECTED — {stock}"
        elif "Crossover" in buy['Setup']: header_msg = f"⚔️ 9/20 EMA CROSSOVER — {stock}"
        elif "EMA" in buy['Setup']: header_msg = f"🧲 20-EMA PULLBACK BUY — {stock}"
        else: header_msg = f"⚡ NEW TRADE ALERT — {stock}"

        alert_msg = f"""{header_msg}
-------------------
Verdict: {debate_result['verdict']} | Confidence: {debate_result['confidence']}/10

Bull Case: {debate_result['bull_case']}
Bear Caveat: {debate_result['bear_case']}

Entry Zone: Rs {entry}
Stop Loss: Rs {sl}
Target: Rs {buy['Target2']} (1:{buy['RR']} R:R)
-------------------
Paper Capital: Rs {required_margin:,.2f} ({required_qty} shares)"""
        send_telegram_alert(alert_msg)

    flat_history = history.get("active_trades", []) + history.get("closed_trades", [])
    with open(history_file, "w") as f: json.dump(flat_history, f, indent=4)
    print("Multi-Agent Debate Engine Complete.")

def run_pipeline():
    print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Executing Multi-Agent Engine...")
    mkt = get_market_data()
    if mkt:
        sector_trends, _ = get_sector_trends()
        scanner_df = scan_hybrid_setups(sector_trends, mkt)
        track_targets_and_notify(scanner_df, sector_df=None, mkt=mkt)
        
        buy_count = len(scanner_df) # Scanner now only outputs max 5
        send_telegram_alert(f"✅ Momentum Scan Completed!\nTop Sniper Setups Found: {buy_count}\nMarket Mood: {mkt['mood']}")

if __name__ == "__main__":
    run_pipeline()
