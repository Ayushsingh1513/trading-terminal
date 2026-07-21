import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import requests
import numpy as np

# --- CONFIG & SECRETS ---
BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(
    page_title="Momentum Frenzy — Indian Stock Scanner Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "landing"

today_str = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
if "tg_last_date" not in st.session_state or st.session_state.tg_last_date != today_str:
    st.session_state.tg_last_date = today_str
    st.session_state.tg_open_sent = False
    st.session_state.tg_close_sent = False


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM DISPATCH ENGINE (9:45 AM & 3:30 PM IST)
# ══════════════════════════════════════════════════════════════════════════════
def send_tg_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

def format_opening_message(picks, mood, mood_score):
    now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | 09:45 AM IST")
    text = f"⚡ <b>MOMENTUM FRENZY — MORNING BREAKOUT PICKS</b> ⚡\n"
    text += f"📅 <i>{now_ist}</i>\n"
    text += f"🧭 Market Mood: <b>{mood} ({mood_score}/100)</b>\n"
    text += "───────────────────────────\n\n"
    
    for idx, p in enumerate(picks[:3], 1):
        text += f"🎯 <b>PICK #{idx}: {p['Stock']}</b> ({p['Setup']})\n"
        text += f"• Entry: <b>₹{p['Entry']}</b>\n"
        text += f"• Stop Loss: <b>₹{p['SL']}</b>\n"
        text += f"• Target 1: <b>₹{p['Target1']}</b> | Target 2: <b>₹{p['Target2']}</b>\n"
        text += f"• Risk:Reward: <b>1:{p['RR']}</b> | Score: <b>{p['Score']}/100</b>\n\n"
        
    text += "⚠️ <i>Educational purpose only. Not SEBI advice. Always manage risk!</i>\n"
    text += "🔗 Terminal: <a href='https://momentumfrenzy.online'>momentumfrenzy.online</a>"
    return text

def format_closing_message(picks, mood, mood_score, nl, nchg):
    now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | 03:30 PM IST")
    text = f"🔔 <b>MARKET CLOSING SUMMARY & EVENING WRAP-UP</b> 🔔\n"
    text += f"📅 <i>{now_ist}</i>\n"
    text += f"📈 Nifty 50: <b>{nl:,.0f} ({'+' if nchg>=0 else ''}{nchg:.2f}%)</b>\n"
    text += f"🧭 Market Mood: <b>{mood} ({mood_score}/100)</b>\n"
    text += "───────────────────────────\n\n"
    
    if picks:
        text += "🔥 <b>TOP MOMENTUM GAINERS TO WATCH FOR TOMORROW:</b>\n"
        for idx, p in enumerate(picks[:3], 1):
            text += f"{idx}. <b>{p['Stock']}</b> — CMP: ₹{p['Price']} | Score: {p['Score']}/100 | Setup: {p['Setup']}\n"
        text += "\n"
        
    text += "⚠️ <i>Educational purpose only. Consult a SEBI registered advisor.</i>\n"
    text += "🔗 Terminal: <a href='https://momentumfrenzy.online'>momentumfrenzy.online</a>"
    return text


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
    * { font-family: 'Inter', -apple-system, sans-serif !important; }
    html, body, .stApp { background:#07091A; color:#CBD5E1; }
    .mono { font-family: 'JetBrains Mono', monospace !important; }
    .block-container { padding:0; max-width:100%; }
    header[data-testid="stHeader"], #MainMenu, footer { display:none; }

    .lp-nav {
        display:flex; align-items:center; justify-content:space-between;
        padding:16px 40px; border-bottom:1px solid #0F1A35;
        background:rgba(7, 9, 26, 0.85); backdrop-filter:blur(10px);
        position:sticky; top:0; z-index:99;
    }
    .lp-logo {
        display:flex; align-items:center; gap:10px;
        font-family:'JetBrains Mono',monospace !important; font-size:15px; font-weight:700;
        color:#F1F5F9; letter-spacing:-.01em;
    }
    .lp-logo-dot { width:8px; height:8px; border-radius:50%; background:#3B7DFB; box-shadow:0 0 10px #3B7DFB; }
    .lp-nav-tag { font-size:11px; color:#64748B; border:1px solid #0F1A35; border-radius:4px; padding:4px 10px; text-transform:uppercase; font-weight:600; }
    .lp-hero { min-height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:60px 24px 40px; }
    .lp-eyebrow {
        display:inline-flex; align-items:center; gap:6px; background:#0D1634; border:1px solid #1E3057; border-radius:4px; padding:6px 14px;
        font-family:'JetBrains Mono',monospace !important; font-size:11px; color:#3B7DFB; font-weight:600; letter-spacing:.1em; text-transform:uppercase; margin-bottom:28px;
    }
    .lp-eyebrow-dot { width:6px; height:6px; border-radius:50%; background:#3B7DFB; animation:blink 1.4s infinite; }
    @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:.3;} }
    .lp-h1 { font-size:clamp(42px,6.5vw,80px); font-weight:800; line-height:1.05; letter-spacing:-.03em; color:#F1F5F9; margin:0 0 10px 0; max-width:840px; }
    .lp-h1 span { color:transparent; background:linear-gradient(135deg,#3B7DFB,#06B6D4); -webkit-background-clip:text; background-clip:text; }
    .lp-sub { font-size:clamp(15px,1.8vw,19px); color:#64748B; max-width:540px; line-height:1.75; margin:16px auto 40px; }
    
    .lp-stats { display:flex; border:1px solid #0F1A35; border-radius:10px; background:#0D1120; overflow:hidden; max-width:680px; margin:40px auto 0; }
    .lp-stat { flex:1; padding:20px 24px; text-align:center; border-right:1px solid #0F1A35; }
    .lp-stat:last-child { border-right:none; }
    .lp-stat-n { font-family:'JetBrains Mono',monospace !important; font-size:26px; font-weight:700; color:#3B7DFB; }
    .lp-stat-l { font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:.1em; margin-top:4px; }
    </style>

    <div class="lp-nav">
        <div class="lp-logo"><div class="lp-logo-dot"></div>MomentumFrenzy</div>
        <div class="lp-nav-tag">Free · NSE Terminal · Live</div>
    </div>

    <div class="lp-hero">
        <div class="lp-eyebrow"><div class="lp-eyebrow-dot"></div>Indian Markets · High-Probability Swing Scanner</div>
        <h1 class="lp-h1">Find the trade.<br><span>Before the move.</span></h1>
        <p class="lp-sub">Institutional momentum scanner for NSE. Entry, Stop Loss, Targets, and Sector Rotation auto-calculated in real time.</p>
        
        <div class="lp-stats">
            <div class="lp-stat"><div class="lp-stat-n">84</div><div class="lp-stat-l">Stocks Scanned</div></div>
            <div class="lp-stat"><div class="lp-stat-n">13</div><div class="lp-stat-l">Sectors Tracked</div></div>
            <div class="lp-stat"><div class="lp-stat-n">15 min</div><div class="lp-stat-l">Live Cache</div></div>
            <div class="lp-stat"><div class="lp-stat-n">Free</div><div class="lp-stat-l">Always</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("⚡  Launch Terminal — Free", use_container_width=True, type="primary"):
            st.session_state.page = "terminal"
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL — GLOBAL STYLES & ANIMATIONS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
* { font-family: 'Inter', -apple-system, sans-serif !important; }

.mono, .pick-stock, .pick-buy-badge, .pick-cell-val, .pick-cell-lbl, .sec-hdr-text, 
.ticker-label, .ticker-val, .mood-value, .pick-rr, .pick-meta span, .sq-title, .sq-chip, .sec-stat-val {
    font-family: 'JetBrains Mono', monospace !important;
}

html, body, .stApp { background:#07091A; color:#CBD5E1; }
.block-container { padding: 0 0 4rem 0; max-width: 100%; }
header[data-testid="stHeader"], #MainMenu, footer { display: none; }

@keyframes fadeSlideUp {
    0% { opacity: 0; transform: translateY(16px); }
    100% { opacity: 1; transform: translateY(0); }
}
.animated-entry { animation: fadeSlideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

/* Ticker Bar */
.ticker-bar {
    background:#0A0E1E; border-bottom:1px solid #0F1A35; padding:0 20px;
    display:flex; align-items:center; position:sticky; top:0; z-index:999;
    height:42px; overflow-x: auto; white-space: nowrap; scrollbar-width: none;
}
.ticker-bar::-webkit-scrollbar { display: none; }
.ticker-item { display:flex; align-items:center; gap:8px; padding:0 18px; border-right:1px solid #0F1A35; height:100%; }
.ticker-item:last-child { border-right:none; }
.ticker-label { font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:.1em; font-weight:600; }
.ticker-val { font-size:13px; font-weight:700; color:#F1F5F9; }
.tv-up { color:#00D68F !important; }
.tv-down { color:#FF4C4C !important; }
.tv-blue { color:#3B7DFB !important; }
.ticker-spacer { flex:1; }
.ticker-time { font-size:10px; color:#334155; padding-left:16px; }

/* Tabs Header */
.stTabs [data-baseweb="tab-list"] { background:#07091A; border-bottom:1px solid #0F1A35; padding:0 20px; gap:8px; }
.stTabs [data-baseweb="tab"] { background:transparent; color:#64748B; font-size:13px; font-weight:600; padding:12px 20px; border-bottom:2px solid transparent; }
.stTabs [aria-selected="true"] { color:#3B7DFB !important; border-bottom-color:#3B7DFB !important; background:transparent !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 16px 20px; }

/* Section Headers */
.sec-hdr { display:flex; align-items:center; gap:10px; padding:18px 0 12px 0; border-bottom:1px solid #0A1020; margin-bottom:16px; }
.sec-hdr-line { width:4px; height:18px; background:linear-gradient(180deg, #3B7DFB, #06B6D4); border-radius:2px; }
.sec-hdr-text { font-size:12px; font-weight:700; color:#E2E8F0; text-transform:uppercase; letter-spacing:.12em; }

/* Mood Banner */
.mood-banner { display:flex; align-items:stretch; background:#0D1120; border:1px solid #0F1A35; border-radius:10px; overflow:hidden; margin:12px 0 16px; }
.mood-side { width:5px; flex-shrink:0; }
.mood-content { flex:1; padding:16px 20px; display:flex; align-items:center; gap:24px; flex-wrap:wrap; }
.mood-label-sm { font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.mood-value { font-size:22px; font-weight:800; line-height:1; }
.mood-score-row { display:flex; align-items:center; gap:8px; margin-top:6px; }
.mood-score-bar-bg { flex:1; height:4px; background:#0A1020; border-radius:2px; }
.mood-score-bar-fill { height:4px; border-radius:2px; }
.mood-score-num { font-size:11px; color:#64748B; }
.mood-meta { font-size:11px; color:#475569; line-height:1.8; }
.mood-tip { font-size:12px; color:#64748B; margin-top:6px; padding-top:6px; border-top:1px solid #0A1020; }

/* Trade Cards */
.pick-card {
    background:#0D1120; border:1px solid #1E2D47; border-radius:12px; overflow:hidden; margin-bottom:16px;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
}
.pick-card:hover { border-color:#3B7DFB; transform: translateY(-3px); box-shadow: 0 8px 24px rgba(59, 125, 251, 0.15); }
.pick-card-head { display:flex; align-items:center; justify-content:space-between; padding:14px 16px; border-bottom:1px solid #0F1A35; background:linear-gradient(180deg, #101628, #0D1120); }
.pick-stock { font-size:18px; font-weight:800; color:#FFFFFF; margin:0; line-height:1; }
.pick-setup { font-size:10px; color:#64748B; margin-top:3px; }
.pick-buy-badge { background:rgba(0, 214, 143, 0.12); color:#00D68F; font-size:10px; font-weight:800; padding:4px 10px; border-radius:5px; border:1px solid rgba(0, 214, 143, 0.3); letter-spacing:.08em; }
.pick-grid { display:grid; grid-template-columns:1fr 1fr; gap:1px; background:#0F1A35; }
.pick-cell { background:#0A0E1E; padding:10px 14px; }
.pick-cell-lbl { font-size:9px; color:#475569; text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px; font-weight:600; }
.pick-cell-val { font-size:14px; font-weight:700; }
.pv-entry { color:#E2E8F0; } .pv-sl { color:#FF4C4C; } .pv-t1 { color:#00D68F; } .pv-t2 { color:#06B6D4; }
.pick-foot { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; border-top:1px solid #0F1A35; background:#0A0E1E; }
.pick-rr { font-size:11px; font-weight:700; }
.pick-meta { display:flex; gap:10px; font-size:10px; color:#475569; }

/* Sector Quadrant Grid */
.sq-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.sq-card { border-radius:10px; padding:16px; min-height:110px; background:#0D1120; transition: transform 0.2s; }
.sq-card:hover { transform: translateY(-2px); }
.sq-leading { background:linear-gradient(180deg, #051409, #0D1120); border:1px solid rgba(0, 214, 143, 0.25); }
.sq-improving { background:linear-gradient(180deg, #07100A, #0D1120); border:1px solid rgba(6, 182, 212, 0.25); }
.sq-weakening { background:linear-gradient(180deg, #120E05, #0D1120); border:1px solid rgba(255, 176, 32, 0.25); }
.sq-lagging { background:linear-gradient(180deg, #120505, #0D1120); border:1px solid rgba(255, 76, 76, 0.25); }
.sq-title { font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.12em; margin-bottom:10px; }
.sq-leading .sq-title { color:#00D68F; }
.sq-improving .sq-title { color:#06B6D4; }
.sq-weakening .sq-title { color:#FFB020; }
.sq-lagging .sq-title { color:#FF4C4C; }
.sq-chip { display:inline-flex; align-items:center; gap:4px; font-size:11px; padding:4px 9px; border-radius:5px; background:rgba(255,255,255,0.05); color:#CBD5E1; margin:3px; border:1px solid rgba(255,255,255,0.08); }

/* Sector Mini Stats */
.sec-stat-box { background:#0A0E1E; border:1px solid #0F1A35; border-radius:8px; padding:12px 16px; text-align:center; }
.sec-stat-lbl { font-size:9px; color:#475569; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.sec-stat-val { font-size:18px; font-weight:700; color:#F1F5F9; }

/* Instagram CTA */
.ig-cta { background:#0D1120; border:1px solid #0F1A35; border-radius:10px; padding:24px; text-align:center; margin:20px 0; }
.ig-cta-title { font-size:15px; font-weight:700; color:#E2E8F0; margin-bottom:4px; }
.ig-cta-sub { font-size:12px; color:#475569; margin-bottom:14px; }
.ig-btn { display:inline-block; background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); color:#fff !important; padding:8px 24px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:700; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS & CACHED DATA ENGINE (15 MIN TTL) ─────────────────────────────────
def tc(v):  return "tv-up" if v >= 0 else "tv-down"
def ar(v):  return "▲" if v >= 0 else "▼"

def style_sig(val):
    if val == "BUY":   return "background:#0C1F0F;color:#00D68F;font-weight:700;font-family:JetBrains Mono,monospace"
    if val == "WATCH": return "background:#1A1305;color:#FFB020;font-weight:700;font-family:JetBrains Mono,monospace"
    if val == "AVOID": return "background:#180606;color:#FF4C4C;font-weight:700;font-family:JetBrains Mono,monospace"
    return ""

def style_sc(val):
    if val >= 65: return "color:#00D68F;font-weight:600;font-family:JetBrains Mono,monospace"
    if val >= 45: return "color:#FFB020;font-family:JetBrains Mono,monospace"
    return "color:#FF4C4C;font-family:JetBrains Mono,monospace"

# Reduced cache time to 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def get_close(t, p="6mo"):
    for _ in range(2):
        try:
            df = yf.download(t, period=p, interval="1d", progress=False, auto_adjust=True)
            r = df['Close'].squeeze().dropna()
            if len(r) > 2: return r
        except: pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=900)
def get_top_picks(tickers, nifty_1m):
    picks = []; CHUNK = 50
    for i in range(0, len(tickers), CHUNK):
        chunk = list(tickers[i:i+CHUNK])
        try:
            raw = (yf.download(chunk[0], period="6mo", interval="1d", progress=False, auto_adjust=True)
                   if len(chunk) == 1
                   else yf.download(chunk, period="6mo", interval="1d", progress=False, auto_adjust=True, group_by="ticker"))
            for t in chunk:
                try:
                    if len(chunk) == 1:
                        close = raw['Close'].squeeze().dropna(); high = raw['High'].squeeze().dropna()
                        low   = raw['Low'].squeeze().dropna();  vol  = raw['Volume'].squeeze().dropna()
                    else:
                        close = raw[t]['Close'].squeeze().dropna(); high = raw[t]['High'].squeeze().dropna()
                        low   = raw[t]['Low'].squeeze().dropna();   vol  = raw[t]['Volume'].squeeze().dropna()
                    if len(close) < 50: continue
                    price  = float(close.iloc[-1])
                    ema20  = float(close.ewm(span=20).mean().iloc[-1])
                    ema50  = float(close.ewm(span=50).mean().iloc[-1])
                    ema200 = float(close.ewm(span=200).mean().iloc[-1])
                    atr    = float((high-low).rolling(14).mean().iloc[-1])
                    delta  = close.diff()
                    gain   = delta.clip(lower=0).rolling(14).mean()
                    loss   = -delta.clip(upper=0).rolling(14).mean()
                    rsi    = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
                    w52h   = float(close.rolling(min(252,len(close))).max().iloc[-1])
                    pfh    = round((price/w52h-1)*100, 1)
                    va     = float(vol.rolling(20).mean().iloc[-1])
                    vs     = round(float(vol.iloc[-1])/va, 1) if va > 0 else 0
                    s1m    = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                    rs     = round(s1m-nifty_1m, 1)
                    stage2 = price > ema20 > ema50 > ema200
                    vcp    = sum([stage2, pfh>-10, vs>=1.5, rs>0])
                    sc     = round(min(
                        min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                        min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))
                    if sc < 55 or not stage2: continue
                    entry   = round(price * 1.001, 1)
                    sl      = round(max(ema20 * 0.99, price - atr * 1.5), 1)
                    target1 = round(price + atr * 2, 1)
                    target2 = round(price + atr * 3.5, 1)
                    risk    = round(entry - sl, 1)
                    reward  = round(target1 - entry, 1)
                    rr      = round(reward / risk, 1) if risk > 0 else 0
                    if rr < 1.5: continue
                    setup = ("Breakout" if pfh>-3 and vs>=1.5 else
                             "Pullback" if 40<=rsi<=55 else
                             "Vol Surge" if vs>=2 else "Trend")
                    picks.append({
                        "Stock": t.replace(".NS",""), "Price": round(price,1),
                        "Setup": setup, "Score": sc, "RSI": round(rsi,1),
                        "VolSurge": vs, "RS": rs, "52W%": pfh,
                        "Entry": entry, "Target1": target1, "Target2": target2,
                        "SL": sl, "RR": rr, "ATR": round(atr,1)
                    })
                except: pass
        except: pass
    return sorted(picks, key=lambda x: x["Score"], reverse=True)[:10]

@st.cache_data(ttl=900)
def batch_scan(tickers, nifty_1m):
    all_rows = []; CHUNK = 50
    for i in range(0, len(tickers), CHUNK):
        chunk = list(tickers[i:i+CHUNK])
        try:
            raw = (yf.download(chunk[0], period="6mo", interval="1d", progress=False, auto_adjust=True)
                   if len(chunk) == 1
                   else yf.download(chunk, period="6mo", interval="1d", progress=False, auto_adjust=True, group_by="ticker"))
            for t in chunk:
                try:
                    if len(chunk) == 1:
                        close = raw['Close'].squeeze().dropna(); vol = raw['Volume'].squeeze().dropna()
                    else:
                        close = raw[t]['Close'].squeeze().dropna(); vol = raw[t]['Volume'].squeeze().dropna()
                    if len(close) < 50: continue
                    ema20  = float(close.ewm(span=20).mean().iloc[-1])
                    ema50  = float(close.ewm(span=50).mean().iloc[-1])
                    ema200 = float(close.ewm(span=200).mean().iloc[-1])
                    price  = float(close.iloc[-1])
                    delta  = close.diff()
                    gain   = delta.clip(lower=0).rolling(14).mean()
                    loss   = -delta.clip(upper=0).rolling(14).mean()
                    rsi    = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
                    w52h   = float(close.rolling(min(252,len(close))).max().iloc[-1])
                    pfh    = round((price/w52h-1)*100, 1)
                    va     = float(vol.rolling(20).mean().iloc[-1])
                    vs     = round(float(vol.iloc[-1])/va, 1) if va > 0 else 0
                    s1m    = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                    rs     = round(s1m-nifty_1m, 1)
                    stage2 = price > ema20 > ema50 > ema200
                    vcp    = sum([stage2, pfh>-10, vs>=1.5, rs>0])
                    sc     = round(min(
                        min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                        min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))
                    sig   = "BUY" if sc>=65 and stage2 else ("WATCH" if sc>=45 else "AVOID")
                    setup = ("Breakout" if stage2 and pfh>-3 and vs>=1.5 else
                             "Pullback" if stage2 and 40<=rsi<=55 else
                             "Oversold" if rsi<35 else
                             "Vol Surge" if stage2 and vs>=2 else
                             "Trend" if stage2 else "Base")
                    risk_r = ["Low","Medium","High"][min(sum([vs>3, pfh<-20, rsi>75]),2)]
                    all_rows.append({
                        "Stock": t.replace(".NS",""), "Price": round(price,1),
                        "Setup": setup, "Score": sc, "Signal": sig, "RSI": round(rsi,1),
                        "RS": rs, "VolSurge": vs, "52W%": pfh, "Risk": risk_r,
                        "Stage2": "✅" if stage2 else "❌"
                    })
                except: pass
        except: pass
    if not all_rows: return pd.DataFrame()
    return pd.DataFrame(all_rows).sort_values("Score", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=900)
def get_detailed_sectors(sectors):
    rows = []
    for name, ticker in sectors.items():
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            if len(df) < 30: continue
            close = df['Close'].squeeze().dropna()
            vol   = df['Volume'].squeeze().dropna()
            
            price = float(close.iloc[-1])
            prev  = float(close.iloc[-2]) if len(close)>=2 else price
            pct_today = round((price/prev - 1)*100, 2)
            
            r1m = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
            r3m = float((close.iloc[-1]/close.iloc[0]-1)*100)
            
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = -delta.clip(upper=0).rolling(14).mean()
            rsi   = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
            
            w52h  = float(close.rolling(min(252,len(close))).max().iloc[-1])
            pfh   = round((price/w52h-1)*100, 1)
            
            avg20 = float(vol.rolling(20).mean().iloc[-1]) if len(vol)>=20 else 1.0
            today_vol = float(vol.iloc[-1]) if len(vol)>0 else 1.0
            punch = round(today_vol/avg20, 2) if avg20 > 0 else 1.0
            
            score = round(r1m*0.4 + r3m*0.3 + (rsi/100)*20 + (10+pfh)*1, 2)
            
            rows.append({
                "Sector": name, "Ticker": ticker, "Price": round(price,1),
                "DayChange%": pct_today, "1M%": round(r1m,2), "3M%": round(r3m,2),
                "RSI": round(rsi,1), "52W%": pfh, "VolPunch": punch, "Score": score
            })
        except: pass
    return pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)


# Exact 84 High-Volume Stock Universe
NIFTY500 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS",
    "SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","ITC.NS",
    "BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS",
    "NESTLEIND.NS","WIPRO.NS","ULTRACEMCO.NS","TECHM.NS","HCLTECH.NS","ONGC.NS",
    "NTPC.NS","POWERGRID.NS","COALINDIA.NS","BAJAJFINSV.NS","DIVISLAB.NS",
    "DRREDDY.NS","ADANIENT.NS","ADANIPORTS.NS","AMBUJACEM.NS","APOLLOHOSP.NS",
    "BAJAJ-AUTO.NS","BANKBARODA.NS","BEL.NS","BPCL.NS","BRITANNIA.NS","CANBK.NS",
    "CHOLAFIN.NS","CIPLA.NS","DABUR.NS","DLF.NS","DIXON.NS","EICHERMOT.NS",
    "GAIL.NS","GODREJCP.NS","GRASIM.NS","HAVELLS.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDPETRO.NS","INDUSINDBK.NS","IOC.NS","IRCTC.NS","JSWSTEEL.NS","LTIM.NS",
    "LUPIN.NS","M&M.NS","MOTHERSON.NS","MUTHOOTFIN.NS","NAUKRI.NS","PIDILITIND.NS",
    "PNB.NS","SAIL.NS","SHREECEM.NS","SIEMENS.NS","SRF.NS","TATAPOWER.NS",
    "TATASTEEL.NS","TORNTPHARM.NS","TRENT.NS","VEDL.NS","VOLTAS.NS","ZOMATO.NS",
    "HAL.NS","RVNL.NS","IRFC.NS","BHEL.NS","MAZDOCK.NS","CONCOR.NS","POLYCAB.NS",
    "PERSISTENT.NS","COFORGE.NS"
]

# Exact 13 Sector Indices
SECTORS = {
    "IT": "^CNXIT", "Pvt Bank": "^CNXPVTBANK", "PSU Bank": "^CNXPSUBANK",
    "Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA", "FMCG": "^CNXFMCG",
    "Metal": "^CNXMETAL", "Energy": "^CNXENERGY", "Realty": "^CNXREALTY",
    "Infra": "^CNXINFRA", "Cons Dur": "^CNXCONSUM", "PSE": "^CNXPSE",
    "MNC": "^CNXMNC"
}

SECTOR_STOCKS = {
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","TECHM.NS","HCLTECH.NS","LTIM.NS","PERSISTENT.NS","COFORGE.NS"],
    "Pvt Bank": ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","AXISBANK.NS","INDUSINDBK.NS"],
    "PSU Bank": ["SBIN.NS","BANKBARODA.NS","CANBK.NS","PNB.NS"],
    "Auto": ["MARUTI.NS","EICHERMOT.NS","HEROMOTOCO.NS","M&M.NS","BAJAJ-AUTO.NS"],
    "Pharma": ["SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","LUPIN.NS"],
    "Metal": ["JSWSTEEL.NS","TATASTEEL.NS","HINDALCO.NS","SAIL.NS","VEDL.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","TATAPOWER.NS"],
    "Realty": ["DLF.NS"],
    "Infra": ["LT.NS","BEL.NS","HAL.NS","RVNL.NS","BHEL.NS"]
}


# ── MARKET DATA ENGINE ────────────────────────────────────────────────────────
with st.spinner("Loading live market data..."):
    nifty_c = get_close("^NSEI", "1y")
    bank_c  = get_close("^NSEBANK")
    vix_c   = get_close("^INDIAVIX", "1mo")

if len(nifty_c) < 2 or len(bank_c) < 2:
    st.error("⚠️ Data temporarily unavailable. Refreshing..."); st.stop()

nl    = float(nifty_c.iloc[-1]);  np_ = float(nifty_c.iloc[-2]); nchg = (nl/np_-1)*100
bl    = float(bank_c.iloc[-1]);   bp  = float(bank_c.iloc[-2]);  bchg = (bl/bp-1)*100
vl    = float(vix_c.iloc[-1])   if len(vix_c)>1 else 0
vc_   = float(vix_c.iloc[-2])   if len(vix_c)>1 else 0
vchg  = (vl/vc_-1)*100          if vc_>0 else 0
ma200 = float(nifty_c.rolling(min(200,len(nifty_c))).mean().iloc[-1])
ma50  = float(nifty_c.rolling(min(50,len(nifty_c))).mean().iloc[-1])
state = "BULL" if nl > ma200 else "BEAR"
state_c = "#00D68F" if state == "BULL" else "#FF4C4C"
nifty_1m = float((nifty_c.iloc[-1]/nifty_c.iloc[max(-21,-len(nifty_c))]-1)*100)
nifty_1w = float((nifty_c.iloc[-1]/nifty_c.iloc[max(-5,-len(nifty_c))]-1)*100)

mood_score = 0
mood_score += 30 if nl > ma200 else 0
mood_score += 20 if nl > ma50  else 0
mood_score += 15 if nifty_1m > 0 else 0
mood_score += 15 if nifty_1w > 0 else 0
mood_score += 10 if nchg > 0 else 0
mood_score += 10 if vl < 15 else (5 if vl < 20 else 0)

if mood_score >= 70:   mood, mood_c = "BULLISH", "#00D68F"
elif mood_score >= 45: mood, mood_c = "NEUTRAL", "#FFB020"
else:                  mood, mood_c = "BEARISH", "#FF4C4C"


# ── TICKER BAR ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ticker-bar">
  <div class="ticker-item">
    <span class="ticker-label">Nifty 50</span>
    <span class="ticker-val {tc(nchg)}">{nl:,.0f} &nbsp;{ar(nchg)}{abs(nchg):.2f}%</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">BankNifty</span>
    <span class="ticker-val {tc(bchg)}">{bl:,.0f} &nbsp;{ar(bchg)}{abs(bchg):.2f}%</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">India VIX</span>
    <span class="ticker-val {tc(-vchg)}">{vl:.2f}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">MA200</span>
    <span class="ticker-val tv-blue">{ma200:,.0f}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">Regime</span>
    <span class="ticker-val" style="color:{state_c};">{state}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">Mood</span>
    <span class="ticker-val" style="color:{mood_c};">{mood} {mood_score}/100</span>
  </div>
  <div class="ticker-spacer"></div>
  <span class="ticker-time">{(datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime('%d %b %Y  %H:%M IST')}</span>
</div>
""", unsafe_allow_html=True)

# ── HEADER & MANUAL TELEGRAM TRIGGER ──────────────────────────────────────────
hc1, hc2, hc3 = st.columns([1, 7, 3])
with hc1:
    st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png", width=48)
with hc2:
    st.markdown("""
    <div style='padding:4px 0;'>
      <div style='font-family:"JetBrains Mono",monospace !important;font-size:16px;font-weight:700;color:#F1F5F9;letter-spacing:-.01em;'>
        ⚡ MOMENTUM FRENZY
      </div>
      <div style='font-size:10px;color:#3B7DFB;letter-spacing:.06em;margin-top:2px;'>
        INDIAN MARKETS &nbsp;·&nbsp; SWING TRADING TERMINAL &nbsp;·&nbsp; PRO
      </div>
    </div>""", unsafe_allow_html=True)
with hc3:
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    if st.button("📢 Send Picks to Telegram Now", use_container_width=True):
        with st.spinner("Dispatching Telegram notification..."):
            top_picks = get_top_picks(tuple(NIFTY500), nifty_1m)
            if top_picks:
                msg_body = format_opening_message(top_picks, mood, mood_score)
                if send_tg_message(msg_body):
                    st.success("✅ Picks sent to Telegram!")
                else:
                    st.error("❌ Failed to send Telegram message.")


# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  🎯  Picks & Scanner  ", "  📊  Sector Intelligence  "])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PICKS & SCANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    mood_tips = {"BULLISH": "Market structure is healthy. BUY setups have higher follow-through today.",
                 "NEUTRAL": "Trade selectively. Only high-score setups worth considering.",
                 "BEARISH": "Avoid fresh longs. Focus on capital protection."}
    ma200_txt = "✓ Above MA200" if nl>ma200 else "✗ Below MA200"
    ma50_txt  = "✓ Above MA50"  if nl>ma50  else "✗ Below MA50"
    vix_txt   = "✓ VIX low"    if vl<15 else ("⚠ VIX elevated" if vl<20 else "✗ VIX high")

    st.markdown(f"""
    <div class="mood-banner animated-entry">
      <div class="mood-side" style="background:{mood_c};"></div>
      <div class="mood-content">
        <div>
          <div class="mood-label-sm">Market Mood</div>
          <div class="mood-value" style="color:{mood_c};">{mood}</div>
          <div class="mood-score-row">
            <div class="mood-score-bar-bg" style="width:120px;">
              <div class="mood-score-bar-fill" style="background:{mood_c};width:{mood_score}%;"></div>
            </div>
            <span class="mood-score-num">{mood_score}/100</span>
          </div>
        </div>
        <div style="flex:1;min-width:200px;">
          <div class="mood-meta">
            <span style="color:{'#00D68F' if nl>ma200 else '#FF4C4C'}">{ma200_txt}</span>
            &nbsp;·&nbsp;
            <span style="color:{'#00D68F' if nl>ma50 else '#FF4C4C'}">{ma50_txt}</span>
            &nbsp;·&nbsp;
            <span style="color:{'#00D68F' if vl<15 else '#FFB020' if vl<20 else '#FF4C4C'}">{vix_txt}</span>
          </div>
          <div class="mood-tip">{mood_tips[mood]}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Today's Top Swing Trade Picks</div></div>", unsafe_allow_html=True)

    with st.spinner("Scanning 84 stocks for best momentum setups…"):
        picks = get_top_picks(tuple(NIFTY500), nifty_1m)

    # ── AUTOMATED TELEGRAM SCHEDULE CHECK (9:45 AM IST & 3:30 PM IST) ──
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    
    # Morning Opening Message (Triggered at 9:45 AM IST)
    if now_ist.hour == 9 and now_ist.minute >= 45 and not st.session_state.tg_open_sent and picks:
        msg_body = format_opening_message(picks, mood, mood_score)
        if send_tg_message(msg_body):
            st.session_state.tg_open_sent = True

    # Evening Closing Message (Triggered at 3:30 PM IST)
    if (now_ist.hour == 15 and now_ist.minute >= 30) or (now_ist.hour >= 16) and not st.session_state.tg_close_sent:
        msg_body = format_closing_message(picks, mood, mood_score, nl, nchg)
        if send_tg_message(msg_body):
            st.session_state.tg_close_sent = True

    if picks:
        pc1, pc2, pc3 = st.columns(3)
        for col, pk in zip([pc1, pc2, pc3], picks[:3]):
            rr_c = "#00D68F" if pk["RR"] >= 2 else "#FFB020" if pk["RR"] >= 1.5 else "#FF4C4C"
            setup_map = {"Breakout": "🚀 Breakout", "Pullback": "↩ Pullback", "Vol Surge": "💥 Vol Surge", "Trend": "↗ Trend"}
            with col:
                st.markdown(f"""
                <div class="pick-card animated-entry">
                  <div class="pick-card-head">
                    <div>
                      <div class="pick-stock">{pk["Stock"]}</div>
                      <div class="pick-setup">{setup_map.get(pk["Setup"], pk["Setup"])} &nbsp;·&nbsp; Score {pk["Score"]}/100</div>
                    </div>
                    <div class="pick-buy-badge">STRONG BUY</div>
                  </div>
                  <div class="pick-grid">
                    <div class="pick-cell">
                      <div class="pick-cell-lbl">Entry</div>
                      <div class="pick-cell-val pv-entry">₹{pk["Entry"]}</div>
                    </div>
                    <div class="pick-cell">
                      <div class="pick-cell-lbl">Stop Loss</div>
                      <div class="pick-cell-val pv-sl">₹{pk["SL"]}</div>
                    </div>
                    <div class="pick-cell">
                      <div class="pick-cell-lbl">Target 1</div>
                      <div class="pick-cell-val pv-t1">₹{pk["Target1"]}</div>
                    </div>
                    <div class="pick-cell">
                      <div class="pick-cell-lbl">Target 2</div>
                      <div class="pick-cell-val pv-t2">₹{pk["Target2"]}</div>
                    </div>
                  </div>
                  <div class="pick-foot">
                    <div class="pick-rr" style="color:{rr_c};">R:R &nbsp;1 : {pk["RR"]}</div>
                    <div class="pick-meta">
                      <span>RSI {pk["RSI"]}</span>
                      <span>Vol {pk["VolSurge"]}x</span>
                      <span>RS {pk["RS"]:+.1f}%</span>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

        if len(picks) > 3:
            st.markdown("<div class='sec-hdr animated-entry' style='margin-top:8px;'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>More High-Ranked Setups</div></div>", unsafe_allow_html=True)
            more_df = pd.DataFrame(picks[3:]).rename(columns={
                "Stock":"Stock","Price":"CMP","Setup":"Setup","Score":"Score",
                "Entry":"Entry ₹","SL":"SL ₹","Target1":"T1 ₹","Target2":"T2 ₹","RR":"R:R"
            })[["Stock","CMP","Setup","Score","Entry ₹","SL ₹","T1 ₹","T2 ₹","R:R","RSI","VolSurge"]]
            st.dataframe(
                more_df.style.map(style_sc, subset=["Score"])
                .format({"CMP":"{:.1f}","Entry ₹":"{:.1f}","SL ₹":"{:.1f}","T1 ₹":"{:.1f}","T2 ₹":"{:.1f}","R:R":"{:.1f}","RSI":"{:.1f}","VolSurge":"{:.1f}x"}),
                use_container_width=True, height=220)
    else:
        st.info("No high-probability setups found right now. Market may be consolidating.")

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Full Momentum Scanner</div></div>", unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1: sf     = st.selectbox("Signal", ["All","BUY","WATCH","AVOID"])
    with fc2: rf     = st.selectbox("Risk",   ["All","Low","Medium","High"])
    with fc3: setupf = st.selectbox("Setup",  ["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with fc4: tn     = st.selectbox("Universe",["Top 30","Top 50","All 84 Stocks"], index=2)

    tm = {"Top 30":30, "Top 50":50, "All 84 Stocks":len(NIFTY500)}
    with st.spinner(f"Scanning {tm[tn]} stocks…"):
        scan_df = batch_scan(tuple(NIFTY500[:tm[tn]]), nifty_1m)

    if len(scan_df) > 0:
        filt = scan_df.copy()
        if sf != "All":     filt = filt[filt["Signal"] == sf]
        if rf != "All":     filt = filt[filt["Risk"]   == rf]
        if setupf != "All": filt = filt[filt["Setup"]  == setupf]
        st.dataframe(
            filt.style.map(style_sig, subset=["Signal"]).map(style_sc, subset=["Score"])
            .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"}),
            use_container_width=True, height=360)
    else:
        st.warning("No data available. Try refreshing.")

    st.markdown("""
    <div class="ig-cta animated-entry">
      <div class="ig-cta-title">Follow @momentumfrenzy on Instagram</div>
      <div class="ig-cta-sub">Daily breakout ideas, trade setups and market analysis</div>
      <a class="ig-btn" href="https://instagram.com/momentumfrenzy" target="_blank">Follow Now</a>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SECTOR INTELLIGENCE (EXACTLY 13 SECTORS)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Rotation & Performance Engine (13 NSE Indices)</div></div>", unsafe_allow_html=True)

    with st.spinner("Analyzing 13 NSE Sector Indices..."):
        sec_df = get_detailed_sectors(SECTORS)

    if len(sec_df) > 0:
        med1 = sec_df["1M%"].median()
        med3 = sec_df["3M%"].median()
        
        leading   = sec_df[(sec_df["1M%"]>=med1)&(sec_df["3M%"]>=med3)]
        improving = sec_df[(sec_df["1M%"]>=med1)&(sec_df["3M%"]<med3)]
        weakening = sec_df[(sec_df["1M%"]<med1)&(sec_df["3M%"]>=med3)]
        lagging   = sec_df[(sec_df["1M%"]<med1)&(sec_df["3M%"]<med3)]

        # Summary Metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Leading Sectors</div><div class='sec-stat-val' style='color:#00D68F;'>{len(leading)}</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Improving Sectors</div><div class='sec-stat-val' style='color:#06B6D4;'>{len(improving)}</div></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Weakening</div><div class='sec-stat-val' style='color:#FFB020;'>{len(weakening)}</div></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Lagging</div><div class='sec-stat-val' style='color:#FF4C4C;'>{len(lagging)}</div></div>", unsafe_allow_html=True)
        top_vol = sec_df.sort_values("VolPunch", ascending=False).iloc[0]
        m5.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Top Vol Surge</div><div class='sec-stat-val' style='color:#3B7DFB;'>{top_vol['Sector']} ({top_vol['VolPunch']}x)</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        def make_chips(df_sub):
            if len(df_sub) == 0: return "<span style='color:#475569;font-size:11px;'>No sectors currently in this quadrant</span>"
            chips = ""
            for _, r in df_sub.iterrows():
                c = "#00D68F" if r["1M%"]>=0 else "#FF4C4C"
                chips += f'<span class="sq-chip">{r["Sector"]} <b style="color:{c};">{r["1M%"]:+.1f}%</b></span>'
            return chips

        ql, qr = st.columns([1.2, 1])
        with ql:
            st.markdown(f"""
            <div class="sq-grid animated-entry">
              <div class="sq-card sq-leading">
                <div class="sq-title">↑ Leading (Strong Short & Long Term)</div>{make_chips(leading)}
              </div>
              <div class="sq-card sq-improving">
                <div class="sq-title">↗ Improving (Fresh Momentum Rebound)</div>{make_chips(improving)}
              </div>
              <div class="sq-card sq-weakening">
                <div class="sq-title">↘ Weakening (Momentum Cooling Down)</div>{make_chips(weakening)}
              </div>
              <div class="sq-card sq-lagging">
                <div class="sq-title">↓ Lagging (Underperforming Market)</div>{make_chips(lagging)}
              </div>
            </div>""", unsafe_allow_html=True)

        with qr:
            fig_s = go.Figure(go.Bar(
                x=sec_df["Sector"], y=sec_df["Score"],
                marker_color=["#00D68F" if s>50 else "#06B6D4" if s>30 else "#FFB020" if s>10 else "#FF4C4C" for s in sec_df["Score"]],
                text=[f"{s:.0f}" for s in sec_df["Score"]], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10)
            ))
            fig_s.update_layout(
                title=dict(text="13 Sectors Momentum Score", font=dict(size=12, color="#E2E8F0")),
                plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
                height=290, margin=dict(l=0, r=0, t=30, b=0),
                yaxis=dict(gridcolor="#0A1020"), xaxis=dict(gridcolor="#0A1020", tickangle=-45)
            )
            st.plotly_chart(fig_s, use_container_width=True)

        st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Comprehensive Sector Metrics Table</div></div>", unsafe_allow_html=True)
        disp_sec = sec_df[["Sector", "DayChange%", "1M%", "3M%", "RSI", "52W%", "VolPunch", "Score"]].rename(
            columns={"DayChange%":"Today %", "52W%":"From 52W High %", "VolPunch":"Vol Multiplier"}
        )
        st.dataframe(
            disp_sec.style.map(style_sc, subset=["Score"])
            .format({"Today %":"{:+.2f}%", "1M%":"{:+.2f}%", "3M%":"{:+.2f}%", "RSI":"{:.1f}", "From 52W High %":"{:.1f}%", "Vol Multiplier":"{:.2f}x", "Score":"{:.1f}"}),
            use_container_width=True, height=280
        )

        st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Stock Drilldown Radar</div></div>", unsafe_allow_html=True)
        s_col1, s_col2 = st.columns([1, 3])
        with s_col1:
            selected_sec = st.selectbox("Select Sector to Inspect", list(SECTOR_STOCKS.keys()))
        
        with s_col2:
            st.markdown(f"<p style='font-size:12px;color:#3B7DFB;font-weight:600;margin-top:8px;'>Analyzing components of Nifty {selected_sec}</p>", unsafe_allow_html=True)
            
        sec_stock_list = SECTOR_STOCKS.get(selected_sec, [])
        if sec_stock_list:
            with st.spinner(f"Scanning Nifty {selected_sec}..."):
                sec_stocks_df = batch_scan(tuple(sec_stock_list), nifty_1m)
            if len(sec_stocks_df) > 0:
                st.dataframe(
                    sec_stocks_df.style.map(style_sig, subset=["Signal"]).map(style_sc, subset=["Score"])
                    .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"}),
                    use_container_width=True, height=220
                )


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:24px 20px;border-top:1px solid #0A1020;margin-top:24px;'>
  <p style='color:#1E2D47;font-size:10px;margin:0;font-family:"JetBrains Mono",monospace !important;letter-spacing:.04em;'>
    Educational purposes only. Not financial advice. Always DYOR. Consult a SEBI-registered advisor.<br><br>
    © 2026 Momentum Frenzy &nbsp;·&nbsp;
    <a href='https://instagram.com/momentumfrenzy' style='color:#1E3A8A;text-decoration:none;'>@momentumfrenzy</a>
  </p>
</div>""", unsafe_allow_html=True)
