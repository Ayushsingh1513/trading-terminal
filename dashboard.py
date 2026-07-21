import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import requests
import json
import os

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
# DATA LOADING ENGINE (INSTANT LOAD)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60) # Only caches for 60 seconds to ensure fresh file reads
def load_backend_data():
    if not os.path.exists("market_data.json") or not os.path.exists("scanner_data.csv") or not os.path.exists("sector_data.csv"):
        return None, None, None
    try:
        with open("market_data.json", "r") as f:
            market_data = json.load(f)
        scanner_df = pd.read_csv("scanner_data.csv")
        sector_df = pd.read_csv("sector_data.csv")
        return market_data, scanner_df, sector_df
    except Exception:
        return None, None, None

market_data, scanner_df, sector_df = load_backend_data()

# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM DISPATCH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def send_tg_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

def format_opening_message(picks, mood, mood_score, nl, nchg, ma200, ma50, vl):
    now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | 09:45 AM IST")
    text = f"⚡ <b>MOMENTUM FRENZY — MORNING BREAKOUT RADAR</b> ⚡\n"
    text += f"📅 <i>{now_ist}</i>\n\n"
    text += f"📊 <b>MARKET REGIME ANALYSIS:</b>\n"
    text += f"• Nifty 50: <b>{nl:,.0f}</b> ({'+' if nchg>=0 else ''}{nchg:.2f}%)\n"
    text += f"• Mood Score: <b>{mood} ({mood_score}/100)</b>\n"
    text += f"• Trend Status: <b>{'Above MA200 ✓' if nl>ma200 else 'Below MA200 ✗'}</b> | <b>{'Above MA50 ✓' if nl>ma50 else 'Below MA50 ✗'}</b>\n"
    text += f"• India VIX: <b>{vl:.2f}</b> ({'Risk Low' if vl<15 else 'Elevated Risk' if vl<20 else 'High Volatility'})\n"
    text += "───────────────────────────\n\n"
    text += "🔥 <b>TOP HIGH-PROBABILITY SWING SETUPS:</b>\n\n"
    
    for idx, p in enumerate(picks[:5], 1):
        text += f"🎯 <b>PICK #{idx}: {p['Stock']}</b> [{p['Setup']}]\n"
        text += f"• Entry: <b>₹{p['Entry']}</b> | Current Price: <b>₹{p['Price']}</b>\n"
        text += f"• Stop Loss: <b>₹{p['SL']}</b> (Risk Management)\n"
        text += f"• Target 1: <b>₹{p['Target1']}</b> | Target 2: <b>₹{p['Target2']}</b>\n"
        text += f"• Metrics: R:R <b>1:{p['RR']}</b> | Score <b>{p['Score']}/100</b> | RSI <b>{p['RSI']}</b> | Vol <b>{p['VolSurge']}x</b>\n\n"
        
    text += "⚠️ <i>Educational purpose only. Not SEBI registered advice.</i>\n"
    text += "🔗 <b>Live Terminal:</b> <a href='https://momentumfrenzy.online'>momentumfrenzy.online</a>"
    return text

def format_closing_message(picks, mood, mood_score, nl, nchg, bl, bchg, vl):
    now_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | 03:30 PM IST")
    text = f"🔔 <b>MARKET CLOSING BELL & EVENING INTELLIGENCE</b> 🔔\n"
    text += f"📅 <i>{now_ist}</i>\n\n"
    text += f"📈 <b>BENCHMARK INDICES:</b>\n"
    text += f"• Nifty 50: <b>{nl:,.0f}</b> ({'+' if nchg>=0 else ''}{nchg:.2f}%)\n"
    text += f"• Bank Nifty: <b>{bl:,.0f}</b> ({'+' if bchg>=0 else ''}{bchg:.2f}%)\n"
    text += f"• India VIX: <b>{vl:.2f}</b>\n"
    text += f"• End-of-Day Mood: <b>{mood} ({mood_score}/100)</b>\n"
    text += "───────────────────────────\n\n"
    
    if picks:
        text += "🚀 <b>TOP BREAKOUT GAINERS TO WATCH FOR TOMORROW:</b>\n\n"
        for idx, p in enumerate(picks[:5], 1):
            text += f"{idx}. <b>{p['Stock']}</b> — CMP: ₹{p['Price']} | Setup: {p['Setup']} | Momentum Score: {p['Score']}/100 | RS vs Nifty: {p['RS']:+.1f}%\n"
        text += "\n"
        
    text += "⚠️ <i>Educational purpose only. Consult a SEBI-registered advisor.</i>\n"
    text += "🔗 <b>Full Terminal:</b> <a href='https://momentumfrenzy.online'>momentumfrenzy.online</a>"
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

    .lp-nav { display:flex; align-items:center; justify-content:space-between; padding:16px 40px; border-bottom:1px solid #0F1A35; background:rgba(7, 9, 26, 0.85); backdrop-filter:blur(10px); position:sticky; top:0; z-index:99; }
    .lp-logo { display:flex; align-items:center; gap:10px; font-family:'JetBrains Mono',monospace !important; font-size:15px; font-weight:700; color:#F1F5F9; letter-spacing:-.01em; }
    .lp-logo-dot { width:8px; height:8px; border-radius:50%; background:#3B7DFB; box-shadow:0 0 10px #3B7DFB; }
    .lp-nav-tag { font-size:11px; color:#64748B; border:1px solid #0F1A35; border-radius:4px; padding:4px 10px; text-transform:uppercase; font-weight:600; }
    .lp-hero { min-height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:60px 24px 40px; }
    .lp-eyebrow { display:inline-flex; align-items:center; gap:6px; background:#0D1634; border:1px solid #1E3057; border-radius:4px; padding:6px 14px; font-family:'JetBrains Mono',monospace !important; font-size:11px; color:#3B7DFB; font-weight:600; letter-spacing:.1em; text-transform:uppercase; margin-bottom:28px; }
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
        <div class="lp-nav-tag">Free · NSE Terminal · Pro</div>
    </div>

    <div class="lp-hero">
        <div class="lp-eyebrow"><div class="lp-eyebrow-dot"></div>Indian Markets · High-Probability Swing Scanner</div>
        <h1 class="lp-h1">Find the trade.<br><span>Before the move.</span></h1>
        <p class="lp-sub">Institutional momentum scanner for NSE. Entry, Stop Loss, Targets, and Sector Rotation auto-calculated in real time.</p>
        <div class="lp-stats">
            <div class="lp-stat"><div class="lp-stat-n">500+</div><div class="lp-stat-l">Stocks Scanned</div></div>
            <div class="lp-stat"><div class="lp-stat-n">18</div><div class="lp-stat-l">Sectors Tracked</div></div>
            <div class="lp-stat"><div class="lp-stat-n">15 min</div><div class="lp-stat-l">Live Refresh</div></div>
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
# TERMINAL UI INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
if market_data is None:
    st.markdown("""
    <div style='text-align:center; padding:100px; color:#3B7DFB; font-family:"JetBrains Mono",monospace;'>
        <h2>⚙️ Initializing Data Engine...</h2>
        <p style='color:#64748B;'>Please wait about 30 seconds for the backend to sync live market data.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

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

@keyframes fadeSlideUp { 0% { opacity: 0; transform: translateY(16px); } 100% { opacity: 1; transform: translateY(0); } }
.animated-entry { animation: fadeSlideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

.ticker-bar { background:#0A0E1E; border-bottom:1px solid #0F1A35; padding:0 20px; display:flex; align-items:center; position:sticky; top:0; z-index:999; height:42px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
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

.stTabs [data-baseweb="tab-list"] { background:#07091A; border-bottom:1px solid #0F1A35; padding:0 20px; gap:8px; }
.stTabs [data-baseweb="tab"] { background:transparent; color:#64748B; font-size:13px; font-weight:600; padding:12px 20px; border-bottom:2px solid transparent; }
.stTabs [aria-selected="true"] { color:#3B7DFB !important; border-bottom-color:#3B7DFB !important; background:transparent !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 16px 20px; }

.sec-hdr { display:flex; align-items:center; gap:10px; padding:18px 0 12px 0; border-bottom:1px solid #0A1020; margin-bottom:16px; }
.sec-hdr-line { width:4px; height:18px; background:linear-gradient(180deg, #3B7DFB, #06B6D4); border-radius:2px; }
.sec-hdr-text { font-size:12px; font-weight:700; color:#E2E8F0; text-transform:uppercase; letter-spacing:.12em; }

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

.pick-card { background:#0D1120; border:1px solid #1E2D47; border-radius:12px; overflow:hidden; margin-bottom:16px; transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease; box-shadow: 0 4px 16px rgba(0,0,0,0.25); }
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

.stDataFrame { border:1px solid #0F1A35; border-radius:8px; overflow:hidden; }

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

.sec-stat-box { background:#0A0E1E; border:1px solid #0F1A35; border-radius:8px; padding:12px 16px; text-align:center; }
.sec-stat-lbl { font-size:9px; color:#475569; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.sec-stat-val { font-size:18px; font-weight:700; color:#F1F5F9; }

.ig-cta { background:#0D1120; border:1px solid #0F1A35; border-radius:10px; padding:24px; text-align:center; margin:20px 0; }
.ig-cta-title { font-size:15px; font-weight:700; color:#E2E8F0; margin-bottom:4px; }
.ig-cta-sub { font-size:12px; color:#475569; margin-bottom:14px; }
.ig-btn { display:inline-block; background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); color:#fff !important; padding:8px 24px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

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


nl = market_data['nifty']
nchg = market_data['nifty_chg']
bl = market_data['bank']
bchg = market_data['bank_chg']
vl = market_data['vix']
vchg = market_data['vix_chg']
ma200 = market_data['ma200']
ma50 = market_data['ma50']
mood = market_data['mood']
mood_score = market_data['mood_score']
state_c = "#00D68F" if nl > ma200 else "#FF4C4C"
mood_c = "#00D68F" if mood == "BULLISH" else "#FFB020" if mood == "NEUTRAL" else "#FF4C4C"

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
    <span class="ticker-val" style="color:{state_c};">{'BULL' if nl > ma200 else 'BEAR'}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">Mood</span>
    <span class="ticker-val" style="color:{mood_c};">{mood} {mood_score}/100</span>
  </div>
  <div class="ticker-spacer"></div>
  <span class="ticker-time">Data Updated: {market_data['timestamp']}</span>
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
        INDIAN MARKETS &nbsp;·&nbsp; SWING TRADING TERMINAL &nbsp;·&nbsp; PRO (500+ STOCKS)
      </div>
    </div>""", unsafe_allow_html=True)

top_picks = scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records')

with hc3:
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    if st.button("📢 Send Alert to Telegram Now", use_container_width=True):
        with st.spinner("Dispatching detailed Telegram notification..."):
            if top_picks:
                msg_body = format_opening_message(top_picks, mood, mood_score, nl, nchg, ma200, ma50, vl)
                if send_tg_message(msg_body):
                    st.success("✅ Alert sent to Telegram!")
                else:
                    st.error("❌ Failed to send Telegram message.")


# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  🎯  Picks & Scanner  ", "  📊  Sector Intelligence  "])

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

    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    
    if now_ist.hour == 9 and now_ist.minute >= 45 and not st.session_state.tg_open_sent and top_picks:
        msg_body = format_opening_message(top_picks, mood, mood_score, nl, nchg, ma200, ma50, vl)
        if send_tg_message(msg_body):
            st.session_state.tg_open_sent = True

    if ((now_ist.hour == 15 and now_ist.minute >= 30) or (now_ist.hour >= 16)) and not st.session_state.tg_close_sent:
        msg_body = format_closing_message(top_picks, mood, mood_score, nl, nchg, bl, bchg, vl)
        if send_tg_message(msg_body):
            st.session_state.tg_close_sent = True

    if top_picks:
        pc1, pc2, pc3 = st.columns(3)
        for col, pk in zip([pc1, pc2, pc3], top_picks[:3]):
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

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Full Momentum Scanner</div></div>", unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1: sf     = st.selectbox("Signal", ["All","BUY","WATCH","AVOID"])
    with fc2: rf     = st.selectbox("Risk",   ["All","Low","Medium","High"])
    with fc3: setupf = st.selectbox("Setup",  ["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with fc4: tn     = st.selectbox("Universe",["Top 100","Top 250","All 500+ Stocks"], index=2)

    filt = scanner_df.copy()
    if tn == "Top 100": filt = filt.head(100)
    elif tn == "Top 250": filt = filt.head(250)
    
    if sf != "All":     filt = filt[filt["Signal"] == sf]
    if rf != "All":     filt = filt[filt["Risk"]   == rf]
    if setupf != "All": filt = filt[filt["Setup"]  == setupf]
    
    st.dataframe(
        filt.style.map(style_sig, subset=["Signal"]).map(style_sc, subset=["Score"])
        .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"}),
        use_container_width=True, height=360)

    st.markdown("""
    <div class="ig-cta animated-entry">
      <div class="ig-cta-title">Follow @momentumfrenzy on Instagram</div>
      <div class="ig-cta-sub">Daily breakout ideas, trade setups and market analysis</div>
      <a class="ig-btn" href="https://instagram.com/momentumfrenzy" target="_blank">Follow Now</a>
    </div>""", unsafe_allow_html=True)


with tab2:

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Rotation & Performance Engine (18 Major NSE Indices)</div></div>", unsafe_allow_html=True)

    med1 = sector_df["1M%"].median()
    med3 = sector_df["3M%"].median()
    
    leading   = sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]>=med3)]
    improving = sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]<med3)]
    weakening = sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]>=med3)]
    lagging   = sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]<med3)]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Leading Sectors</div><div class='sec-stat-val' style='color:#00D68F;'>{len(leading)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Improving Sectors</div><div class='sec-stat-val' style='color:#06B6D4;'>{len(improving)}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Weakening</div><div class='sec-stat-val' style='color:#FFB020;'>{len(weakening)}</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Lagging</div><div class='sec-stat-val' style='color:#FF4C4C;'>{len(lagging)}</div></div>", unsafe_allow_html=True)
    top_vol = sector_df.sort_values("VolPunch", ascending=False).iloc[0]
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
            x=sector_df["Sector"], y=sector_df["Score"],
            marker_color=["#00D68F" if s>50 else "#06B6D4" if s>30 else "#FFB020" if s>10 else "#FF4C4C" for s in sector_df["Score"]],
            text=[f"{s:.0f}" for s in sector_df["Score"]], textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10)
        ))
        fig_s.update_layout(
            title=dict(text="18 Sectors Momentum Score", font=dict(size=12, color="#E2E8F0")),
            plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
            height=290, margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(gridcolor="#0A1020"), xaxis=dict(gridcolor="#0A1020", tickangle=-45)
        )
        st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Comprehensive Sector Metrics Table</div></div>", unsafe_allow_html=True)
    disp_sec = sector_df[["Sector", "Today%", "1M%", "3M%", "RSI", "52W%", "VolPunch", "Score"]].rename(
        columns={"Today%":"Today %", "52W%":"From 52W High %", "VolPunch":"Vol Multiplier"}
    )
    st.dataframe(
        disp_sec.style.map(style_sc, subset=["Score"])
        .format({"Today %":"{:+.2f}%", "1M%":"{:+.2f}%", "3M%":"{:+.2f}%", "RSI":"{:.1f}", "From 52W High %":"{:.1f}%", "Vol Multiplier":"{:.2f}x", "Score":"{:.1f}"}),
        use_container_width=True, height=280
    )


st.markdown(f"""
<div style='text-align:center;padding:24px 20px;border-top:1px solid #0A1020;margin-top:24px;'>
  <p style='color:#1E2D47;font-size:10px;margin:0;font-family:"JetBrains Mono",monospace !important;letter-spacing:.04em;'>
    Educational purposes only. Not financial advice. Always DYOR. Consult a SEBI-registered advisor.<br><br>
    © 2026 Momentum Frenzy &nbsp;·&nbsp;
    <a href='https://instagram.com/momentumfrenzy' style='color:#1E3A8A;text-decoration:none;'>@momentumfrenzy</a>
  </p>
</div>""", unsafe_allow_html=True)
