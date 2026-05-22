import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(page_title="Momentum Frenzy Terminal", layout="wide", initial_sidebar_state="collapsed")

# ── Session State ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ── Landing Page ──────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    st.markdown("""
    <style>
    html,body,.stApp{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;}
    .block-container{padding:0;max-width:100%;}
    header[data-testid="stHeader"]{display:none;}
    #MainMenu{display:none;}footer{display:none;}
    .hero{min-height:100vh;background:radial-gradient(ellipse at 20% 50%,#0d1f0d 0%,#0a0a0f 60%),linear-gradient(135deg,#0a0a0f 0%,#0f0f1a 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 20px;}
    .badge{display:inline-block;background:#00380a;border:1px solid #00e676;color:#00e676;font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;padding:6px 16px;border-radius:999px;margin-bottom:24px;}
    .hero-title{font-size:clamp(36px,6vw,80px);font-weight:800;line-height:1.1;margin:0 0 16px 0;background:linear-gradient(135deg,#ffffff 0%,#00e676 50%,#00aa55 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .hero-sub{font-size:clamp(16px,2.5vw,22px);color:#888;max-width:600px;line-height:1.6;margin:0 auto 40px auto;}
    .features{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;max-width:1100px;margin:80px auto 40px auto;padding:0 20px;}
    .feat-card{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:12px;padding:24px;text-align:left;}
    .feat-card:hover{border-color:#00e676;}
    .feat-icon{font-size:28px;margin-bottom:12px;}
    .feat-title{font-size:16px;font-weight:700;color:#e0e0e0;margin-bottom:8px;}
    .feat-desc{font-size:13px;color:#666;line-height:1.6;}
    .stats-bar{display:flex;gap:40px;flex-wrap:wrap;justify-content:center;padding:40px 20px;border-top:1px solid #1e1e3a;border-bottom:1px solid #1e1e3a;margin:40px 0;background:#0f0f1a;}
    .stat-item{text-align:center;}
    .stat-num{font-size:36px;font-weight:800;color:#00e676;}
    .stat-label{font-size:12px;color:#666;text-transform:uppercase;letter-spacing:.1em;}
    .how-section{max-width:900px;margin:0 auto;padding:40px 20px;}
    .step{display:flex;gap:16px;margin-bottom:24px;align-items:flex-start;}
    .step-num{min-width:36px;height:36px;border-radius:50%;background:#00e676;color:#000;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px;}
    .step-text h4{margin:0 0 4px 0;color:#e0e0e0;font-size:15px;}
    .step-text p{margin:0;color:#666;font-size:13px;}
    .disclaimer{max-width:800px;margin:0 auto;padding:20px;background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;font-size:11px;color:#555;line-height:1.6;text-align:center;}
    .footer{text-align:center;padding:30px 20px;border-top:1px solid #1e1e3a;color:#444;font-size:12px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <img src="https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png" style="width:180px;height:180px;object-fit:contain;margin-bottom:16px;border-radius:50%;box-shadow:0 0 40px rgba(0,230,118,0.3);" />
      <div class="badge">⚡ Live Indian Markets</div>
      <h1 class="hero-title">Momentum Frenzy<br>Trading Terminal</h1>
      <p class="hero-sub">Professional-grade momentum scanner for Indian markets. Scan Nifty 500, identify breakouts, track sector rotation — all in one powerful terminal.</p>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Launch Terminal", use_container_width=True, type="primary"):
            st.session_state.page = "terminal"
            st.rerun()
        st.markdown("<p style='text-align:center;color:#555;font-size:12px;margin-top:8px'>Free · No login · Real-time data</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-bar">
      <div class="stat-item"><div class="stat-num">500+</div><div class="stat-label">Stocks Scanned</div></div>
      <div class="stat-item"><div class="stat-num">18</div><div class="stat-label">Sectors Tracked</div></div>
      <div class="stat-item"><div class="stat-num">4hr</div><div class="stat-label">Cache Refresh</div></div>
      <div class="stat-item"><div class="stat-num">100</div><div class="stat-label">Momentum Score</div></div>
      <div class="stat-item"><div class="stat-num">2x</div><div class="stat-label">Daily Alerts</div></div>
    </div>
    <div class="features">
      <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">Nifty 500 Scanner</div><div class="feat-desc">Scan Nifty 500 with proprietary Momentum Score (0–100). Find BUY, WATCH & AVOID signals instantly.</div></div>
      <div class="feat-card"><div class="feat-icon">📊</div><div class="feat-title">4-Quadrant Sector Rotation</div><div class="feat-desc">Identify Leading, Improving, Weakening & Lagging sectors. Know where smart money is rotating.</div></div>
      <div class="feat-card"><div class="feat-icon">📈</div><div class="feat-title">Professional Charts</div><div class="feat-desc">Candlestick charts with EMA 20/50/200, volume analysis. Full chart viewer for any Nifty 500 stock.</div></div>
      <div class="feat-card"><div class="feat-icon">💼</div><div class="feat-title">Portfolio Tracker</div><div class="feat-desc">Track holdings with live P&L in ₹ and %. Real-time CMP updates and visual P&L chart.</div></div>
      <div class="feat-card"><div class="feat-icon">📲</div><div class="feat-title">Telegram Alerts</div><div class="feat-desc">Morning & evening alerts at 9:30 AM and 3:30 PM IST with top BUY signals and market summary.</div></div>
      <div class="feat-card"><div class="feat-icon">⚡</div><div class="feat-title">Market Pulse Bar</div><div class="feat-desc">Sticky bar showing Nifty, BankNifty, VIX, MA200 and market regime (BULL/BEAR) at all times.</div></div>
    </div>
    <div class="how-section">
      <h2 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:32px;">How It Works</h2>
      <div class="step"><div class="step-num">1</div><div class="step-text"><h4>Scanner Runs Automatically</h4><p>Downloads price + volume data for Nifty 500 stocks and computes Momentum Score, RSI, Relative Strength, and Stage 2 criteria.</p></div></div>
      <div class="step"><div class="step-num">2</div><div class="step-text"><h4>Stocks Are Ranked & Classified</h4><p>Each stock gets a Score (0–100), Setup Type (Breakout, Pullback, Vol Surge), Signal (BUY/WATCH/AVOID) and Risk Level.</p></div></div>
      <div class="step"><div class="step-num">3</div><div class="step-text"><h4>You Take Action</h4><p>Filter by signal, view charts, track your portfolio and receive Telegram alerts — all from one terminal.</p></div></div>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,1,1])
    with col2:
        if st.button("⚡ Enter Terminal Now", use_container_width=True):
            st.session_state.page = "terminal"
            st.rerun()

    st.markdown("""
    <div style="max-width:800px;margin:40px auto;padding:0 20px;">
      <div class="disclaimer">⚠️ <b>Disclaimer:</b> Momentum Frenzy is for educational and informational purposes only. Nothing constitutes financial advice. Always do your own research and consult a SEBI-registered advisor. Past performance is not indicative of future results.</div>
    </div>
    <div class="footer">© 2025 Momentum Frenzy · Built for Indian Markets · Data: Yahoo Finance<br><span style="color:#333">momentumfrenzy.online</span></div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Terminal Styles ───────────────────────────────────────────────────────────
st.markdown("""
<style>
html,body,.stApp{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;}
.block-container{padding:0rem 1rem 2rem 1rem;max-width:100%;}
header[data-testid="stHeader"]{display:none;}
#MainMenu{display:none;}footer{display:none;}
.pulse-bar{display:flex;gap:12px;flex-wrap:wrap;background:linear-gradient(90deg,#0f0f1a,#111128);border-bottom:1px solid #1e1e3a;padding:8px 16px;margin-bottom:12px;position:sticky;top:0;z-index:999;}
.pulse-item{display:flex;flex-direction:column;align-items:center;min-width:90px;}
.pulse-label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.08em;}
.pulse-value{font-size:14px;font-weight:700;color:#e0e0e0;}
.pulse-up{color:#00e676!important;}.pulse-down{color:#ff5252!important;}
.stDataFrame{border-radius:8px;overflow:hidden;}
div[data-testid="metric-container"]{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:10px 14px;}
div[data-testid="metric-container"] label{color:#888;font-size:11px;}
.quad-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.quad{border-radius:8px;padding:12px;min-height:110px;}
.quad-leading{background:#00380a22;border:1px solid #00e67655;}
.quad-improving{background:#1a2a0022;border:1px solid #aaff0055;}
.quad-weakening{background:#2a1a0022;border:1px solid #ffaa0055;}
.quad-lagging{background:#2a000022;border:1px solid #ff525255;}
.quad-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;}
.quad-leading .quad-title{color:#00e676;}.quad-improving .quad-title{color:#aaff00;}
.quad-weakening .quad-title{color:#ffaa00;}.quad-lagging .quad-title{color:#ff5252;}
.quad-stock{font-size:12px;padding:2px 6px;border-radius:3px;display:inline-block;margin:2px;background:#ffffff10;}
.section-header{font-size:12px;text-transform:uppercase;letter-spacing:.15em;color:#555;border-bottom:1px solid #1e1e3a;padding-bottom:6px;margin:16px 0 10px 0;}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_telegram(msg):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"HTML"},timeout=10)
    except: pass

def color_val(v): return "pulse-up" if v>=0 else "pulse-down"
def arrow(v): return "▲" if v>=0 else "▼"

def setup_type(stage2,rsi,vs,pfh):
    if stage2 and pfh>-3 and vs>=1.5: return "Breakout"
    if stage2 and 40<=rsi<=55: return "Pullback"
    if rsi<35: return "Oversold"
    if stage2 and vs>=2: return "Vol Surge"
    if stage2: return "Trend"
    return "Base"

def signal_label(sc,stage2):
    if sc>=65 and stage2: return "BUY"
    if sc>=45: return "WATCH"
    return "AVOID"

def risk_level(vs,pfh,rsi):
    return ["Low","Medium","High"][min(sum([vs>3,pfh<-20,rsi>75]),2)]

def style_signal(val):
    if val=="BUY": return "background-color:#00380a;color:#00e676;font-weight:700"
    if val=="WATCH": return "background-color:#2a2200;color:#ffaa00;font-weight:700"
    if val=="AVOID": return "background-color:#2a0000;color:#ff5252;font-weight:700"
    return ""

def style_score(val):
    if val>=65: return "color:#00e676;font-weight:700"
    if val>=45: return "color:#ffaa00"
    return "color:#ff5252"

def style_pnl(val):
    if isinstance(val,str) and "%" in val:
        return "color:#00e676;font-weight:700" if not val.startswith("-") else "color:#ff5252;font-weight:700"
    return ""

@st.cache_data(ttl=14400)
def get_close(ticker, period="6mo"):
    for _ in range(3):
        try:
            df=yf.download(ticker,period=period,interval="1d",progress=False,auto_adjust=True)
            r=df['Close'].squeeze().dropna()
            if len(r)>2: return r
        except: pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=14400)
def get_ohlcv(ticker, period="6mo"):
    for _ in range(3):
        try:
            df=yf.download(ticker,period=period,interval="1d",progress=False,auto_adjust=True)
            if len(df)>2: return df
        except: pass
    return pd.DataFrame()

@st.cache_data(ttl=14400)
def get_price(ticker):
    try:
        df=yf.download(ticker,period="2d",interval="1d",progress=False,auto_adjust=True)
        return float(df['Close'].squeeze().dropna().iloc[-1])
    except: return None

@st.cache_data(ttl=14400)
def batch_scan(tickers_tuple, nifty_1m):
    """Single batch download — fastest possible"""
    tickers = list(tickers_tuple)
    all_rows = []
    CHUNK = 50  # bigger chunks = fewer API calls
    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i+CHUNK]
        try:
            if len(chunk)==1:
                raw=yf.download(chunk[0],period="6mo",interval="1d",progress=False,auto_adjust=True)
                c=raw['Close'].squeeze().dropna(); v=raw['Volume'].squeeze().dropna()
                stocks=[(chunk[0],c,v)]
            else:
                raw=yf.download(chunk,period="6mo",interval="1d",progress=False,auto_adjust=True,group_by="ticker")
                stocks=[]
                for t in chunk:
                    try:
                        c=raw[t]['Close'].squeeze().dropna(); v=raw[t]['Volume'].squeeze().dropna()
                        if len(c)>50: stocks.append((t,c,v))
                    except: pass

            for t,close,volume in stocks:
                try:
                    ema20=float(close.ewm(span=20).mean().iloc[-1])
                    ema50=float(close.ewm(span=50).mean().iloc[-1])
                    ema200=float(close.ewm(span=200).mean().iloc[-1])
                    price=float(close.iloc[-1])
                    delta=close.diff()
                    gain=delta.clip(lower=0).rolling(14).mean()
                    loss=-delta.clip(upper=0).rolling(14).mean()
                    rsi=float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
                    w52h=float(close.rolling(min(252,len(close))).max().iloc[-1])
                    pfh=round((price/w52h-1)*100,1)
                    va=float(volume.rolling(20).mean().iloc[-1])
                    vs=round(float(volume.iloc[-1])/va,1) if va>0 else 0
                    s1m=float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                    rs=round(s1m-nifty_1m,1)
                    stage2=price>ema20>ema50>ema200
                    vcp=sum([stage2,pfh>-10,vs>=1.5,rs>0])
                    sc=round(min(
                        min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                        min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))
                    all_rows.append({"Stock":t.replace(".NS",""),"Price":round(price,1),
                        "Setup":setup_type(stage2,rsi,vs,pfh),"Score":sc,
                        "Signal":signal_label(sc,stage2),"RSI":round(rsi,1),
                        "RS":rs,"VolSurge":vs,"52W%":pfh,
                        "Risk":risk_level(vs,pfh,rsi),"VCP":f"{vcp}/4",
                        "Stage2":"✅" if stage2 else "❌"})
                except: pass
        except: pass
    if not all_rows: return pd.DataFrame()
    return pd.DataFrame(all_rows).sort_values("Score",ascending=False).reset_index(drop=True)


# ── Nifty 500 ─────────────────────────────────────────────────────────────────
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
    "ABB.NS","ABCAPITAL.NS","ACC.NS","APLAPOLLO.NS","AUBANK.NS","AUROPHARMA.NS",
    "BALKRISIND.NS","BANDHANBNK.NS","BERGEPAINT.NS","BIOCON.NS","BOSCHLTD.NS",
    "COFORGE.NS","CROMPTON.NS","CUMMINSIND.NS","DALBHARAT.NS","DEEPAKNTR.NS",
    "ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","FORTIS.NS","GLENMARK.NS",
    "GMRINFRA.NS","HAL.NS","HDFCAMC.NS","HDFCLIFE.NS","IDFCFIRSTB.NS",
    "IEX.NS","INDIANB.NS","INDHOTEL.NS","INDUSTOWER.NS","IRFC.NS","JKCEMENT.NS",
    "JSWENERGY.NS","JUBLFOOD.NS","KEI.NS","LALPATHLAB.NS","LICHSGFIN.NS",
    "LICI.NS","MANAPPURAM.NS","MARICO.NS","MAXHEALTH.NS","MCX.NS","MPHASIS.NS",
    "MRF.NS","NMDC.NS","OBEROIRLTY.NS","OIL.NS","PAGEIND.NS","PERSISTENT.NS",
    "PETRONET.NS","PHOENIX.NS","POLYCAB.NS","PRESTIGE.NS","PVRINOX.NS",
    "RAMCOCEM.NS","RVNL.NS","RECLTD.NS","SBICARD.NS","SBILIFE.NS","SOBHA.NS",
    "SONACOMS.NS","SUPREMEIND.NS","SYNGENE.NS","TATACOMM.NS","TATACHEM.NS",
    "TATACONSUM.NS","TATAELXSI.NS","TATAMOTORS.NS","TATATECH.NS","TIINDIA.NS",
    "TORNTPOWER.NS","TRIDENT.NS","UPL.NS","UTIAMC.NS","VGUARD.NS","ZYDUSLIFE.NS"
]


# ── Market Data ───────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    nifty_close=get_close("^NSEI"); bank_close=get_close("^NSEBANK")
    vix_close=get_close("^INDIAVIX","1mo")

if len(nifty_close)<2 or len(bank_close)<2:
    st.error("⚠️ Market data unavailable. Please refresh in 1-2 minutes.")
    st.stop()

nifty_last=float(nifty_close.iloc[-1]); nifty_prev=float(nifty_close.iloc[-2])
nifty_chg=(nifty_last/nifty_prev-1)*100
bank_last=float(bank_close.iloc[-1]); bank_prev=float(bank_close.iloc[-2])
bank_chg=(bank_last/bank_prev-1)*100
vix_last=float(vix_close.iloc[-1]) if len(vix_close)>1 else 0
vix_prev=float(vix_close.iloc[-2]) if len(vix_close)>1 else 0
vix_chg=(vix_last/vix_prev-1)*100 if vix_prev>0 else 0
ma200=float(nifty_close.rolling(min(200,len(nifty_close))).mean().iloc[-1])
state="BULL" if nifty_last>ma200 else "BEAR"
state_color="#00e676" if state=="BULL" else "#ff5252"
nifty_1m=float((nifty_close.iloc[-1]/nifty_close.iloc[max(-21,-len(nifty_close))]-1)*100)


# ── Pulse Bar ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pulse-bar">
  <div class="pulse-item"><span class="pulse-label">Nifty 50</span>
    <span class="pulse-value {color_val(nifty_chg)}">{nifty_last:,.0f} {arrow(nifty_chg)} {abs(nifty_chg):.2f}%</span></div>
  <div class="pulse-item"><span class="pulse-label">BankNifty</span>
    <span class="pulse-value {color_val(bank_chg)}">{bank_last:,.0f} {arrow(bank_chg)} {abs(bank_chg):.2f}%</span></div>
  <div class="pulse-item"><span class="pulse-label">India VIX</span>
    <span class="pulse-value {color_val(-vix_chg)}">{vix_last:.1f} {arrow(vix_chg)} {abs(vix_chg):.1f}%</span></div>
  <div class="pulse-item"><span class="pulse-label">MA200</span>
    <span class="pulse-value">{ma200:,.0f}</span></div>
  <div class="pulse-item"><span class="pulse-label">Market</span>
    <span class="pulse-value" style="color:{state_color}">{state}</span></div>
  <div class="pulse-item"><span class="pulse-label">Nifty 1M</span>
    <span class="pulse-value {color_val(nifty_1m)}">{arrow(nifty_1m)} {abs(nifty_1m):.1f}%</span></div>
  <div class="pulse-item" style="margin-left:auto"><span class="pulse-label">Updated</span>
    <span class="pulse-value" style="font-size:11px;color:#666">{datetime.now().strftime('%d %b %H:%M')}</span></div>
</div>
""", unsafe_allow_html=True)

hc1,hc2=st.columns([1,10])
with hc1: st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png",width=60)
with hc2:
    st.markdown("<h2 style='color:#00e676;margin:0 0 4px 0;font-size:20px;letter-spacing:.05em'>⚡ MOMENTUM FRENZY TRADING TERMINAL</h2>",unsafe_allow_html=True)
    st.markdown("<p style='color:#555;font-size:12px;margin:0'>Indian Markets · Nifty 500 Momentum Scanner</p>",unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4=st.tabs(["📊 Market & Scanner","📈 Charts","💼 Portfolio","📲 Alerts"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Market & Scanner
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>📊 Sector Rotation — 4 Quadrant</div>",unsafe_allow_html=True)
    sectors={
        "IT":"^CNXIT","Pvt Bank":"^CNXPVTBANK","PSU Bank":"^CNXPSUBANK",
        "Auto":"^CNXAUTO","Pharma":"^CNXPHARMA","FMCG":"^CNXFMCG",
        "Metal":"^CNXMETAL","Energy":"^CNXENERGY","Realty":"^CNXREALTY",
        "Infra":"^CNXINFRA","Cons Dur":"^CNXCONSUM","PSE":"^CNXPSE","MNC":"^CNXMNC","Media":"^CNXMEDIA",
    }
    with st.spinner("Loading sectors…"):
        rows=[]
        for name,ticker in sectors.items():
            try:
                close=get_close(ticker,"3mo")
                if len(close)<20: continue
                ret_1m=float((close.iloc[-1]/close.iloc[-21]-1)*100)
                ret_3m=float((close.iloc[-1]/close.iloc[0]-1)*100)
                rows.append({"Sector":name,"1M%":round(ret_1m,2),"3M%":round(ret_3m,2),"Score":round(ret_1m*0.6+ret_3m*0.4,2)})
            except: pass

    sector_df=pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)
    if len(sector_df)>0:
        med_1m=sector_df["1M%"].median(); med_3m=sector_df["3M%"].median()
        leading=sector_df[(sector_df["1M%"]>=med_1m)&(sector_df["3M%"]>=med_3m)]["Sector"].tolist()
        improving=sector_df[(sector_df["1M%"]>=med_1m)&(sector_df["3M%"]<med_3m)]["Sector"].tolist()
        weakening=sector_df[(sector_df["1M%"]<med_1m)&(sector_df["3M%"]>=med_3m)]["Sector"].tolist()
        lagging=sector_df[(sector_df["1M%"]<med_1m)&(sector_df["3M%"]<med_3m)]["Sector"].tolist()

        def qs(lst):
            out=""
            for s in lst:
                r=sector_df[sector_df["Sector"]==s].iloc[0]
                out+=f'<span class="quad-stock">{s} <b>{r["1M%"]:+.1f}%</b></span>'
            return out or "<span style='color:#444'>—</span>"

        ql,qr=st.columns([1.2,1])
        with ql:
            st.markdown(f"""<div class="quad-grid">
              <div class="quad quad-leading"><div class="quad-title">🚀 Leading</div>{qs(leading)}</div>
              <div class="quad quad-improving"><div class="quad-title">📈 Improving</div>{qs(improving)}</div>
              <div class="quad quad-weakening"><div class="quad-title">⚠️ Weakening</div>{qs(weakening)}</div>
              <div class="quad quad-lagging"><div class="quad-title">📉 Lagging</div>{qs(lagging)}</div>
            </div>""",unsafe_allow_html=True)
        with qr:
            fig_s=go.Figure(go.Bar(x=sector_df["Sector"],y=sector_df["Score"],
                marker_color=["#00e676" if s>0 else "#ff5252" for s in sector_df["Score"]],
                text=[f"{s:+.1f}" for s in sector_df["Score"]],textposition="outside"))
            fig_s.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
                height=240,margin=dict(l=0,r=0,t=10,b=0),
                yaxis=dict(gridcolor="#1a1a2e"),xaxis=dict(gridcolor="#1a1a2e"))
            st.plotly_chart(fig_s,use_container_width=True)

    st.markdown("<div class='section-header'>🔍 Nifty 500 Momentum Scanner</div>",unsafe_allow_html=True)
    sc1,sc2,sc3,sc4=st.columns(4)
    with sc1: sig_f=st.selectbox("Signal",["All","BUY","WATCH","AVOID"])
    with sc2: risk_f=st.selectbox("Risk",["All","Low","Medium","High"])
    with sc3: setup_f=st.selectbox("Setup",["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with sc4: top_n=st.selectbox("Stocks",["Top 50","Top 100","Top 150","All"],index=0)

    top_map={"Top 50":50,"Top 100":100,"Top 150":150,"All":len(NIFTY500)}
    scan_tickers=tuple(NIFTY500[:top_map[top_n]])

    with st.spinner(f"⚡ Scanning {len(scan_tickers)} stocks… (4hr cache — instant on revisit)"):
        scan_df=batch_scan(scan_tickers,nifty_1m)

    if len(scan_df)==0:
        st.warning("Scanner returned no data. Try refreshing.")
    else:
        filtered=scan_df.copy()
        if sig_f!="All": filtered=filtered[filtered["Signal"]==sig_f]
        if risk_f!="All": filtered=filtered[filtered["Risk"]==risk_f]
        if setup_f!="All": filtered=filtered[filtered["Setup"]==setup_f]
        styled=filtered.style\
            .map(style_signal,subset=["Signal"])\
            .map(style_score,subset=["Score"])\
            .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"})
        st.dataframe(styled,use_container_width=True,height=380)
        st.caption(f"Showing {len(filtered)} of {len(scan_df)} stocks · Top {top_n} scanned")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Charts
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>📈 Stock Chart Viewer</div>",unsafe_allow_html=True)
    cc1,cc2,cc3=st.columns([2,1,1])
    with cc1: sel=st.selectbox("Select Stock",[t.replace(".NS","") for t in NIFTY500])
    with cc2: per=st.selectbox("Period",["3mo","6mo","1y"])
    with cc3: ctype=st.selectbox("Chart",["Candles","Line"])

    sdf=get_ohlcv(sel+".NS",per)
    if len(sdf)>0:
        sc_=sdf['Close'].squeeze(); sv_=sdf['Volume'].squeeze()
        fig2=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.75,0.25],vertical_spacing=0.03)
        if ctype=="Candles":
            fig2.add_trace(go.Candlestick(x=sdf.index,open=sdf['Open'].squeeze(),
                high=sdf['High'].squeeze(),low=sdf['Low'].squeeze(),close=sc_,name=sel,
                increasing_line_color="#00e676",decreasing_line_color="#ff5252"),row=1,col=1)
        else:
            fig2.add_trace(go.Scatter(x=sdf.index,y=sc_,name=sel,line=dict(color="#00e676",width=1.5)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc_.ewm(span=20).mean(),name="EMA20",line=dict(color="#00e676",width=1.2)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc_.ewm(span=50).mean(),name="EMA50",line=dict(color="#ffaa00",width=1.2)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc_.ewm(span=200).mean(),name="EMA200",line=dict(color="#ff5252",width=1.2)),row=1,col=1)
        vc=["rgba(0,230,118,0.4)" if c>=o else "rgba(255,82,82,0.4)"
            for c,o in zip(sdf['Close'].squeeze(),sdf['Open'].squeeze())]
        fig2.add_trace(go.Bar(x=sdf.index,y=sv_,marker_color=vc,showlegend=False),row=2,col=1)
        fig2.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",height=520,
            margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#1a1a2e",rangeslider=dict(visible=False)),
            xaxis2=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"),yaxis2=dict(gridcolor="#1a1a2e"),
            legend=dict(bgcolor="#0f0f1a",bordercolor="#1e1e3a",font=dict(size=11)))
        st.plotly_chart(fig2,use_container_width=True)
        if len(scan_df)>0 and sel in scan_df["Stock"].values:
            row_=scan_df[scan_df["Stock"]==sel].iloc[0]
            m1,m2,m3,m4,m5=st.columns(5)
            m1.metric("Score",f"{row_['Score']}/100"); m2.metric("Signal",row_["Signal"])
            m3.metric("RSI",f"{row_['RSI']}"); m4.metric("VolSurge",f"{row_['VolSurge']}x")
            m5.metric("52W High",f"{row_['52W%']}%")

    st.markdown("<div class='section-header'>🇮🇳 Nifty 50 Overview</div>",unsafe_allow_html=True)
    ndf=get_ohlcv("^NSEI","1y")
    if len(ndf)>0:
        nc_=ndf['Close'].squeeze()
        fig3=go.Figure()
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_,name="Nifty",
            line=dict(color="#00e676",width=1.5),fill="tozeroy",fillcolor="rgba(0,230,118,0.07)"))
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_.rolling(200).mean(),name="MA200",line=dict(color="#ff5252",dash="dash",width=1)))
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_.rolling(50).mean(),name="MA50",line=dict(color="#ffaa00",dash="dot",width=1)))
        fig3.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",height=320,
            margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"),
            legend=dict(bgcolor="#0f0f1a",bordercolor="#1e1e3a",font=dict(size=11)))
        st.plotly_chart(fig3,use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Portfolio
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>💼 Portfolio Tracker</div>",unsafe_allow_html=True)
    if "portfolio" not in st.session_state: st.session_state.portfolio=[]

    with st.expander("➕ Add Stock",expanded=len(st.session_state.portfolio)==0):
        pa,pb,pc,pd_=st.columns([2,1,1,1])
        with pa: pstock=st.selectbox("Stock",[t.replace(".NS","") for t in NIFTY500],key="pstock")
        with pb: pbuy=st.number_input("Buy Price ₹",min_value=0.0,step=0.5,key="pbuy")
        with pc: pqty=st.number_input("Quantity",min_value=1,step=1,key="pqty")
        with pd_:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Add ➕"):
                st.session_state.portfolio.append({"Stock":pstock,"Buy":pbuy,"Qty":pqty})
                st.rerun()

    if st.session_state.portfolio:
        pf_rows=[]; ti=0; tc=0
        for item in st.session_state.portfolio:
            price=get_price(item["Stock"]+".NS") or item["Buy"]
            inv=item["Buy"]*item["Qty"]; cur=price*item["Qty"]
            pnl=cur-inv; pct=(pnl/inv*100) if inv>0 else 0
            ti+=inv; tc+=cur
            pf_rows.append({"Stock":item["Stock"],"Buy ₹":item["Buy"],"CMP ₹":round(price,1),
                "Qty":item["Qty"],"Invested ₹":round(inv),"Current ₹":round(cur),
                "P&L ₹":round(pnl),"P&L %":f"{pct:+.1f}%"})
        tp=tc-ti; tpct=(tp/ti*100) if ti>0 else 0
        pm1,pm2,pm3,pm4=st.columns(4)
        pm1.metric("Invested",f"₹{ti:,.0f}"); pm2.metric("Current",f"₹{tc:,.0f}")
        pm3.metric("P&L",f"₹{tp:,.0f}",f"{tpct:+.1f}%"); pm4.metric("Holdings",len(st.session_state.portfolio))
        pf_df=pd.DataFrame(pf_rows)
        st.dataframe(pf_df.style.map(style_pnl,subset=["P&L %"]),use_container_width=True,height=300)
        fig_pf=go.Figure(go.Bar(x=pf_df["Stock"],
            y=[float(p.replace("%","")) for p in pf_df["P&L %"]],
            marker_color=["#00e676" if float(p.replace("%",""))>=0 else "#ff5252" for p in pf_df["P&L %"]],
            text=pf_df["P&L %"],textposition="outside"))
        fig_pf.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
            height=260,margin=dict(l=0,r=0,t=20,b=0),yaxis=dict(gridcolor="#1a1a2e",ticksuffix="%"))
        st.plotly_chart(fig_pf,use_container_width=True)
        rem=st.selectbox("Remove",["—"]+[r["Stock"] for r in st.session_state.portfolio])
        if rem!="—" and st.button(f"Remove {rem} ❌"):
            st.session_state.portfolio=[p for p in st.session_state.portfolio if p["Stock"]!=rem]
            st.rerun()
    else:
        st.info("Add stocks above to track your portfolio!")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Alerts
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>📲 Telegram Alerts</div>",unsafe_allow_html=True)

    def build_msg(label):
        buys=scan_df[scan_df["Signal"]=="BUY"]["Stock"].tolist()[:5] if len(scan_df)>0 else []
        watch=scan_df[scan_df["Signal"]=="WATCH"]["Stock"].tolist()[:5] if len(scan_df)>0 else []
        top5=scan_df.head(5)["Stock"].tolist() if len(scan_df)>0 else []
        top_sec=sector_df.iloc[0] if len(sector_df)>0 else None
        return (
            f"<b>⚡ MOMENTUM FRENZY — {label}</b>\n"
            f"{datetime.now().strftime('%d %b %Y %H:%M IST')}\n\n"
            f"<b>Nifty:</b> {nifty_last:,.0f} ({nifty_chg:+.2f}%) | {state}\n"
            f"<b>BankNifty:</b> {bank_last:,.0f} ({bank_chg:+.2f}%)\n"
            f"<b>VIX:</b> {vix_last:.1f}\n\n"
            f"<b>Top Sector:</b> {top_sec['Sector'] if top_sec is not None else 'N/A'}\n\n"
            f"<b>🟢 BUY:</b> {', '.join(buys) or 'None'}\n"
            f"<b>🟡 WATCH:</b> {', '.join(watch) or 'None'}\n"
            f"<b>🏆 Top 5:</b> {', '.join(top5)}"
        )

    al1,al2=st.columns(2)
    with al1:
        st.markdown("### 🌅 Morning Alert (9:30 AM)")
        if st.button("Send Morning Alert 🌅"):
            send_telegram(build_msg("MORNING ALERT 9:30 AM")); st.success("✅ Sent!")
    with al2:
        st.markdown("### 🌆 Evening Alert (3:30 PM)")
        if st.button("Send Evening Alert 🌆"):
            send_telegram(build_msg("EVENING ALERT 3:30 PM")); st.success("✅ Sent!")

    st.divider()
    custom=st.text_area("Custom Message",placeholder="Type your message…")
    if st.button("Send Custom Alert") and custom:
        send_telegram(custom); st.success("✅ Sent!")

st.caption(f"Momentum Frenzy Terminal · {datetime.now().strftime('%d %b %Y %H:%M')} IST · Data: Yahoo Finance")
