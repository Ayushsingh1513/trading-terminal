import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

def get_close(ticker, period="1y"):
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    return df['Close'].squeeze().dropna()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)

# ── Market Data ───────────────────────────────────────────────────────────────
print("Fetching market data...")
nifty = get_close("^NSEI")
bank  = get_close("^NSEBANK")
vix   = get_close("^INDIAVIX", period="1mo")

nl = float(nifty.iloc[-1]); np_ = float(nifty.iloc[-2])
nchg = (nl / np_ - 1) * 100
bl = float(bank.iloc[-1]);  bp  = float(bank.iloc[-2])
bchg = (bl / bp - 1) * 100
vl = float(vix.iloc[-1])
ma200 = float(nifty.rolling(200).mean().iloc[-1])
state = "BULL 🟢" if nl > ma200 else "BEAR 🔴"

# ── Sector Scan ───────────────────────────────────────────────────────────────
sectors = {
    "IT": "^CNXIT", "Bank": "^NSEBANK", "Auto": "^CNXAUTO",
    "Pharma": "^CNXPHARMA", "FMCG": "^CNXFMCG", "Metal": "^CNXMETAL",
    "Energy": "^CNXENERGY", "Realty": "^CNXREALTY"
}
sector_rows = []
for name, ticker in sectors.items():
    try:
        close = get_close(ticker, period="3mo")
        if len(close) < 20: continue
        ret_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100)
        ret_3m = float((close.iloc[-1] / close.iloc[0]   - 1) * 100)
        sector_rows.append({"Sector": name, "1M%": round(ret_1m,1), "3M%": round(ret_3m,1)})
    except: pass

sector_df  = pd.DataFrame(sector_rows).sort_values("1M%", ascending=False)
top_sector = sector_df.iloc[0] if len(sector_df) > 0 else None

# ── Stock Scanner (Top 50) ────────────────────────────────────────────────────
watchlist = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","BHARTIARTL.NS","AXISBANK.NS","LT.NS","BAJFINANCE.NS",
    "MARUTI.NS","SUNPHARMA.NS","TITAN.NS","HINDUNILVR.NS","HCLTECH.NS",
    "WIPRO.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","TATAPOWER.NS",
    "DIXON.NS","HAL.NS","BEL.NS","IRCTC.NS","ZOMATO.NS",
    "TRENT.NS","ADANIENT.NS","KOTAKBANK.NS","ITC.NS","DIVISLAB.NS",
    "DRREDDY.NS","TECHM.NS","LTIM.NS","PERSISTENT.NS","MPHASIS.NS",
    "POLYCAB.NS","HAVELLS.NS","VOLTAS.NS","CHOLAFIN.NS","BAJAJ-AUTO.NS",
    "EICHERMOT.NS","HEROMOTOCO.NS","M&M.NS","TATAMOTORS.NS","JSWSTEEL.NS",
    "HINDALCO.NS","VEDL.NS","ONGC.NS","BPCL.NS","GAIL.NS"
]

nifty_1m = float((nifty.iloc[-1] / nifty.iloc[-21] - 1) * 100)
buys = []; watches = []; top_scores = []

print("Scanning stocks...")
for t in watchlist:
    try:
        df = yf.download(t, period="1y", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 50: continue
        close  = df['Close'].squeeze().dropna()
        volume = df['Volume'].squeeze().dropna()

        price  = float(close.iloc[-1])
        ema20  = float(close.ewm(span=20).mean().iloc[-1])
        ema50  = float(close.ewm(span=50).mean().iloc[-1])
        ema200 = float(close.ewm(span=200).mean().iloc[-1])
        stage2 = price > ema20 > ema50 > ema200

        delta  = close.diff()
        gain   = delta.clip(lower=0).rolling(14).mean()
        loss   = -delta.clip(upper=0).rolling(14).mean()
        rsi    = float(100 - (100 / (1 + gain.iloc[-1] / (loss.iloc[-1] + 1e-9))))

        week52_high   = float(close.rolling(min(252, len(close))).max().iloc[-1])
        pct_from_high = (price / week52_high - 1) * 100

        vol_avg = float(volume.rolling(20).mean().iloc[-1])
        vol_surge = float(volume.iloc[-1]) / vol_avg if vol_avg > 0 else 0

        stock_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100)
        rs = stock_1m - nifty_1m

        vcp = sum([stage2, pct_from_high > -10, vol_surge >= 1.5, rs > 0])
        score = round(min(
            min(max((rsi-40)/30*25,0),25) +
            min(max(rs/10*20,0),20) +
            min(max((vol_surge-1)/2*20,0),20) +
            vcp/4*25 +
            min(max((10+pct_from_high)/10*10,0),10), 100
        ))

        name = t.replace(".NS","")
        top_scores.append((name, score))

        if score >= 65 and stage2:
            buys.append(f"{name}({score})")
        elif score >= 45:
            watches.append(f"{name}({score})")
    except: pass

top_scores.sort(key=lambda x: x[1], reverse=True)
top5 = [f"{n}({s})" for n,s in top_scores[:5]]

# ── Build & Send Message ──────────────────────────────────────────────────────
hour = datetime.utcnow().hour
label = "🌅 MORNING ALERT — Market Open" if hour < 8 else "🌆 EVENING ALERT — Market Close"

sector_line = ""
if top_sector is not None:
    sector_line = f"<b>🏆 Top Sector:</b> {top_sector['Sector']} ({top_sector['1M%']:+.1f}% 1M)\n"

sector_table = ""
for _, row in sector_df.iterrows():
    arrow = "▲" if row["1M%"] >= 0 else "▼"
    sector_table += f"  {row['Sector']}: {arrow}{abs(row['1M%']):.1f}%\n"

msg = (
    f"<b>⚡ MOMENTUM FRENZY TERMINAL</b>\n"
    f"<b>{label}</b>\n"
    f"{datetime.now().strftime('%d %b %Y %H:%M IST')}\n\n"
    f"━━━━━━━━━━━━━━━━━━\n"
    f"<b>📊 Market Snapshot</b>\n"
    f"<b>Nifty 50:</b> {nl:,.0f} ({'▲' if nchg>=0 else '▼'}{abs(nchg):.2f}%)\n"
    f"<b>BankNifty:</b> {bl:,.0f} ({'▲' if bchg>=0 else '▼'}{abs(bchg):.2f}%)\n"
    f"<b>India VIX:</b> {vl:.1f}\n"
    f"<b>Market:</b> {state}\n\n"
    f"━━━━━━━━━━━━━━━━━━\n"
    f"<b>🔄 Sector Rotation</b>\n"
    f"{sector_table}\n"
    f"━━━━━━━━━━━━━━━━━━\n"
    f"<b>🔍 Scanner Results</b>\n"
    f"<b>🟢 BUY Signals:</b>\n{chr(10).join(buys[:5]) if buys else 'None'}\n\n"
    f"<b>🟡 WATCH List:</b>\n{chr(10).join(watches[:5]) if watches else 'None'}\n\n"
    f"<b>🏆 Top Momentum:</b>\n{', '.join(top5)}\n\n"
    f"━━━━━━━━━━━━━━━━━━\n"
    f"<i>www.momentumfrenzy.online</i>"
)

print("Sending Telegram alert...")
send_telegram(msg)
print(f"✅ Alert sent successfully at {datetime.now().strftime('%H:%M IST')}")

