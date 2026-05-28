import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import numpy as np

BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(page_title="Momentum Frenzy Terminal", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "landing"

if st.session_state.page == "landing":
    st.markdown("""
    <style>
    html,body,.stApp{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;}
    .block-container{padding:0;max-width:100%;}
    header[data-testid="stHeader"]{display:none;}#MainMenu{display:none;}footer{display:none;}
    .hero{min-height:100vh;background:radial-gradient(ellipse at 20% 50%,#0d1f0d 0%,#0a0a0f 60%),linear-gradient(135deg,#0a0a0f 0%,#0f0f1a 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 20px;}
    .badge{display:inline-block;background:#00380a;border:1px solid #00e676;color:#00e676;font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;padding:6px 16px;border-radius:999px;margin-bottom:24px;}
    .hero-title{font-size:clamp(36px,6vw,80px);font-weight:800;line-height:1.1;margin:0 0 16px 0;background:linear-gradient(135deg,#ffffff 0%,#00e676 50%,#00aa55 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
    .hero-sub{font-size:clamp(16px,2.5vw,22px);color:#888;max-width:600px;line-height:1.6;margin:0 auto 40px auto;}
    .features{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;max-width:1100px;margin:80px auto 40px auto;padding:0 20px;}
    .feat-card{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:12px;padding:24px;text-align:left;}.feat-card:hover{border-color:#00e676;}
    .feat-icon{font-size:28px;margin-bottom:12px;}.feat-title{font-size:16px;font-weight:700;color:#e0e0e0;margin-bottom:8px;}.feat-desc{font-size:13px;color:#666;line-height:1.6;}
    .stats-bar{display:flex;gap:40px;flex-wrap:wrap;justify-content:center;padding:40px 20px;border-top:1px solid #1e1e3a;border-bottom:1px solid #1e1e3a;margin:40px 0;background:#0f0f1a;}
    .stat-item{text-align:center;}.stat-num{font-size:36px;font-weight:800;color:#00e676;}.stat-label{font-size:12px;color:#666;text-transform:uppercase;letter-spacing:.1em;}
    .step{display:flex;gap:16px;margin-bottom:24px;align-items:flex-start;}.step-num{min-width:36px;height:36px;border-radius:50%;background:#00e676;color:#000;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px;}
    .step-text h4{margin:0 0 4px 0;color:#e0e0e0;font-size:15px;}.step-text p{margin:0;color:#666;font-size:13px;}
    .disclaimer{max-width:800px;margin:0 auto;padding:20px;background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;font-size:11px;color:#555;line-height:1.6;text-align:center;}
    .footer{text-align:center;padding:30px 20px;border-top:1px solid #1e1e3a;color:#444;font-size:12px;}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <img src="https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png" style="width:180px;height:180px;object-fit:contain;margin-bottom:16px;border-radius:50%;box-shadow:0 0 40px rgba(0,230,118,0.3);" />
      <div class="badge">⚡ Live Indian Markets</div>
      <h1 class="hero-title">Momentum Frenzy<br>Trading Terminal</h1>
      <p class="hero-sub">Professional-grade momentum scanner for Indian markets. Scan Nifty 500, identify breakouts, track sector rotation — all in one powerful terminal.</p>
    </div>""", unsafe_allow_html=True)

    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("🚀 Launch Terminal",use_container_width=True,type="primary"):
            st.session_state.page="terminal"; st.rerun()
        st.markdown("<p style='text-align:center;color:#555;font-size:12px;margin-top:8px'>Free · No login · Real-time data</p>",unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-bar">
      <div class="stat-item"><div class="stat-num">500+</div><div class="stat-label">Stocks Scanned</div></div>
      <div class="stat-item"><div class="stat-num">18</div><div class="stat-label">Sectors Tracked</div></div>
      <div class="stat-item"><div class="stat-num">4hr</div><div class="stat-label">Cache Refresh</div></div>
      <div class="stat-item"><div class="stat-num">100</div><div class="stat-label">Momentum Score</div></div>
      <div class="stat-item"><div class="stat-num">2x</div><div class="stat-label">Daily Alerts</div></div>
    </div>
    <div class="features">
      <div class="feat-card"><div class="feat-icon">🔍</div><div class="feat-title">Nifty 500 Scanner</div><div class="feat-desc">Scan with proprietary Momentum Score (0–100). Find BUY, WATCH & AVOID signals instantly.</div></div>
      <div class="feat-card"><div class="feat-icon">📊</div><div class="feat-title">Sector Intelligence</div><div class="feat-desc">4-Quadrant rotation + Forward Outlook Score + Relative Strength + Trend Grade for all 14 sectors.</div></div>
      <div class="feat-card"><div class="feat-icon">📈</div><div class="feat-title">Professional Charts</div><div class="feat-desc">Candlestick charts with EMA 20/50/200, volume analysis for any Nifty 500 stock.</div></div>
      <div class="feat-card"><div class="feat-icon">💼</div><div class="feat-title">Portfolio Tracker</div><div class="feat-desc">Track holdings with live P&L in ₹ and %. Real-time CMP updates and visual P&L chart.</div></div>
      <div class="feat-card"><div class="feat-icon">📲</div><div class="feat-title">Telegram Alerts</div><div class="feat-desc">Morning & evening alerts at 9:30 AM and 3:30 PM IST with top BUY signals.</div></div>
      <div class="feat-card"><div class="feat-icon">⚡</div><div class="feat-title">Market Pulse Bar</div><div class="feat-desc">Sticky bar showing Nifty, BankNifty, VIX, MA200 and BULL/BEAR regime at all times.</div></div>
    </div>
    <div style="max-width:900px;margin:0 auto;padding:40px 20px;">
      <h2 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:32px;">How It Works</h2>
      <div class="step"><div class="step-num">1</div><div class="step-text"><h4>Scanner Runs Automatically</h4><p>Downloads price + volume data and computes Momentum Score, RSI, Relative Strength, and Stage 2 criteria.</p></div></div>
      <div class="step"><div class="step-num">2</div><div class="step-text"><h4>Stocks Are Ranked & Classified</h4><p>Each stock gets a Score (0–100), Setup Type, Signal (BUY/WATCH/AVOID) and Risk Level.</p></div></div>
      <div class="step"><div class="step-num">3</div><div class="step-text"><h4>You Take Action</h4><p>Filter by signal, view charts, track portfolio and receive Telegram alerts.</p></div></div>
    </div>""", unsafe_allow_html=True)

    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("⚡ Enter Terminal Now",use_container_width=True):
            st.session_state.page="terminal"; st.rerun()

    st.markdown("""
    <div style="max-width:800px;margin:40px auto;padding:0 20px;">
      <div class="disclaimer">⚠️ <b>Disclaimer:</b> Momentum Frenzy is for educational and informational purposes only. Nothing constitutes financial advice. Always consult a SEBI-registered advisor before investing.</div>
    </div>
    <div class="footer">© 2025 Momentum Frenzy · Built for Indian Markets · Data: Yahoo Finance<br><span style="color:#333">momentumfrenzy.online</span></div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html,body,.stApp{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;}
.block-container{padding:0rem 1rem 2rem 1rem;max-width:100%;}
header[data-testid="stHeader"]{display:none;}#MainMenu{display:none;}footer{display:none;}
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
.sector-card{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:10px;padding:14px 16px;margin-bottom:8px;transition:border-color .2s;}
.sector-card:hover{border-color:#00e676;}
.outlook-bar{height:6px;border-radius:3px;background:#1e1e3a;margin-top:6px;}
.outlook-fill{height:6px;border-radius:3px;}
</style>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_telegram(msg):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"HTML"},timeout=10)
    except: pass

def color_val(v): return "pulse-up" if v>=0 else "pulse-down"
def arrow(v): return "▲" if v>=0 else "▼"

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
    for _ in range(2):
        try:
            df=yf.download(ticker,period=period,interval="1d",progress=False,auto_adjust=True)
            r=df['Close'].squeeze().dropna()
            if len(r)>2: return r
        except: pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=14400)
def get_ohlcv(ticker, period="6mo"):
    for _ in range(2):
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
def get_sector_intelligence(sectors_dict, nifty_close):
    """Deep sector analysis with forward outlook score"""
    rows = []
    nifty_ret_1m = float((nifty_close.iloc[-1]/nifty_close.iloc[max(-21,-len(nifty_close))]-1)*100)
    nifty_ret_3m = float((nifty_close.iloc[-1]/nifty_close.iloc[max(-63,-len(nifty_close))]-1)*100)

    for name, ticker in sectors_dict.items():
        try:
            close = get_close(ticker, "1y")
            if len(close) < 50: continue

            # Returns
            ret_1w  = float((close.iloc[-1]/close.iloc[max(-5,-len(close))]-1)*100)
            ret_1m  = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
            ret_3m  = float((close.iloc[-1]/close.iloc[max(-63,-len(close))]-1)*100)
            ret_6m  = float((close.iloc[-1]/close.iloc[max(-126,-len(close))]-1)*100)

            # Relative Strength vs Nifty
            rs_1m = round(ret_1m - nifty_ret_1m, 1)
            rs_3m = round(ret_3m - nifty_ret_3m, 1)

            # Trend indicators
            ema20  = float(close.ewm(span=20).mean().iloc[-1])
            ema50  = float(close.ewm(span=50).mean().iloc[-1])
            ema200 = float(close.ewm(span=200).mean().iloc[-1])
            price  = float(close.iloc[-1])

            # Trend grade
            above_emas = sum([price>ema20, price>ema50, price>ema200, ema20>ema50, ema50>ema200])
            trend_grade = ["D","C","C+","B","B+","A"][above_emas]
            trend_color = ["#ff5252","#ff5252","#ffaa00","#ffaa00","#00e676","#00e676"][above_emas]

            # RSI
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = -delta.clip(upper=0).rolling(14).mean()
            rsi   = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))

            # 52W position
            w52h = float(close.rolling(min(252,len(close))).max().iloc[-1])
            w52l = float(close.rolling(min(252,len(close))).min().iloc[-1])
            pos52 = round((price-w52l)/(w52h-w52l)*100, 1) if w52h!=w52l else 50

            # Momentum acceleration (1W vs 1M trend)
            momentum_acc = round(ret_1w*4 - ret_1m, 1)  # if positive = accelerating

            # Forward Outlook Score (0-100)
            outlook = 0
            outlook += min(max(rs_1m*2, 0), 20)      # RS momentum (max 20)
            outlook += min(max(rs_3m, 0), 15)          # RS trend (max 15)
            outlook += above_emas * 5                   # Trend alignment (max 25)
            outlook += min(max((rsi-40)/40*20, 0), 20) # RSI health (max 20)
            outlook += min(max(pos52/100*20, 0), 20)    # 52W position (max 20)
            outlook = round(min(outlook, 100))

            # Outlook label
            if outlook >= 70: olabel, ocolor = "STRONG BUY", "#00e676"
            elif outlook >= 55: olabel, ocolor = "BULLISH", "#aaff00"
            elif outlook >= 40: olabel, ocolor = "NEUTRAL", "#ffaa00"
            elif outlook >= 25: olabel, ocolor = "WEAK", "#ff8800"
            else: olabel, ocolor = "AVOID", "#ff5252"

            # Key trigger
            if rs_1m > 3 and above_emas >= 4: trigger = "Strong momentum + trend aligned"
            elif momentum_acc > 2: trigger = "Accelerating — picking up pace"
            elif rs_1m < -3: trigger = "Underperforming Nifty — caution"
            elif rsi > 70: trigger = "Overbought — may need rest"
            elif rsi < 40: trigger = "Oversold — watch for reversal"
            elif pos52 > 90: trigger = "Near 52W high — breakout zone"
            elif pos52 < 20: trigger = "Near 52W low — high risk"
            else: trigger = "Consolidating — watch for breakout"

            rows.append({
                "Sector": name, "1W%": round(ret_1w,1), "1M%": round(ret_1m,1),
                "3M%": round(ret_3m,1), "6M%": round(ret_6m,1),
                "RS 1M": rs_1m, "RS 3M": rs_3m,
                "RSI": round(rsi,1), "Trend": trend_grade, "TrendColor": trend_color,
                "52W Pos%": pos52, "Outlook": outlook, "OutlookLabel": olabel,
                "OutlookColor": ocolor, "Trigger": trigger,
                "Score": round(ret_1m*0.6+ret_3m*0.4, 2)
            })
        except: pass
    return pd.DataFrame(rows).sort_values("Outlook", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=7200)
def get_sector_volume_punch(sectors_dict):
    """Get volume punch ratio for each sector index"""
    rows = []
    for name, ticker in sectors_dict.items():
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
            if len(df) < 20: continue
            vol   = df['Volume'].squeeze().dropna()
            close = df['Close'].squeeze().dropna()
            if len(vol) < 20: continue

            avg20   = float(vol.rolling(20).mean().iloc[-1])
            avg5    = float(vol.rolling(5).mean().iloc[-1])
            today   = float(vol.iloc[-1])
            punch   = round(today / avg20, 2) if avg20 > 0 else 1.0
            punch5  = round(avg5 / avg20, 2) if avg20 > 0 else 1.0

            # Last 30 days volume ratio for bar chart
            recent_vol  = vol.iloc[-30:]
            recent_avg  = float(vol.iloc[-50:-30].mean()) if len(vol) >= 50 else avg20
            vol_ratios  = (recent_vol / recent_avg).round(2).tolist()
            dates       = [str(d.date()) for d in recent_vol.index]

            # Price change today
            pct_today = float((close.iloc[-1]/close.iloc[-2]-1)*100) if len(close)>=2 else 0

            # Punch signal
            if punch >= 3.0:   psig, pcol = "🔥 EXTREME", "#ff5252"
            elif punch >= 2.0: psig, pcol = "⚡ HIGH",    "#ffaa00"
            elif punch >= 1.5: psig, pcol = "📈 ELEVATED","#aaff00"
            elif punch >= 0.8: psig, pcol = "➡️ NORMAL",  "#888888"
            else:              psig, pcol = "📉 LOW",     "#555555"

            rows.append({
                "Sector": name, "Today Vol Ratio": punch,
                "5D Avg Ratio": punch5, "Signal": psig,
                "SigColor": pcol, "PctToday": round(pct_today,2),
                "Dates": dates, "VolRatios": vol_ratios
            })
        except: pass
    return sorted(rows, key=lambda x: x["Today Vol Ratio"], reverse=True)

@st.cache_data(ttl=14400)
def batch_scan(tickers_tuple, nifty_1m):
    tickers=list(tickers_tuple); all_rows=[]; CHUNK=50
    for i in range(0,len(tickers),CHUNK):
        chunk=tickers[i:i+CHUNK]
        try:
            if len(chunk)==1:
                raw=yf.download(chunk[0],period="6mo",interval="1d",progress=False,auto_adjust=True)
                stocks=[(chunk[0],raw['Close'].squeeze().dropna(),raw['Volume'].squeeze().dropna())]
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
                    sig="BUY" if sc>=65 and stage2 else ("WATCH" if sc>=45 else "AVOID")
                    setup=("Breakout" if stage2 and pfh>-3 and vs>=1.5 else
                           "Pullback" if stage2 and 40<=rsi<=55 else
                           "Oversold" if rsi<35 else
                           "Vol Surge" if stage2 and vs>=2 else
                           "Trend" if stage2 else "Base")
                    risk=["Low","Medium","High"][min(sum([vs>3,pfh<-20,rsi>75]),2)]
                    all_rows.append({"Stock":t.replace(".NS",""),"Price":round(price,1),
                        "Setup":setup,"Score":sc,"Signal":sig,"RSI":round(rsi,1),
                        "RS":rs,"VolSurge":vs,"52W%":pfh,"Risk":risk,
                        "VCP":f"{vcp}/4","Stage2":"✅" if stage2 else "❌"})
                except: pass
        except: pass
    if not all_rows: return pd.DataFrame()
    return pd.DataFrame(all_rows).sort_values("Score",ascending=False).reset_index(drop=True)


# ── Sectors ───────────────────────────────────────────────────────────────────
SECTORS = {
    "IT":"^CNXIT","Pvt Bank":"^CNXPVTBANK","PSU Bank":"^CNXPSUBANK",
    "Auto":"^CNXAUTO","Pharma":"^CNXPHARMA","FMCG":"^CNXFMCG",
    "Metal":"^CNXMETAL","Energy":"^CNXENERGY","Realty":"^CNXREALTY",
    "Infra":"^CNXINFRA","Cons Dur":"^CNXCONSUM","PSE":"^CNXPSE",
    "MNC":"^CNXMNC","Media":"^CNXMEDIA"
}

SECTOR_MACRO = {
    "IT":       {"drivers":"USD/INR, US Tech demand, Deal wins","risk":"Recession, Rupee appreciation","season":"Q4 strong"},
    "Pvt Bank": {"drivers":"Credit growth, NIM expansion, RBI rate cuts","risk":"NPA rise, Rate hike","season":"Q1 Q3 strong"},
    "PSU Bank": {"drivers":"Govt capex, Credit offtake, Divestment","risk":"NPA, Govt policy change","season":"Budget season"},
    "Auto":     {"drivers":"Rural demand, EV adoption, Festival season","risk":"Input cost, Fuel price","season":"Oct-Dec peak"},
    "Pharma":   {"drivers":"US FDA approvals, Generic exports, Domestic demand","risk":"US pricing pressure, Inspections","season":"Defensive"},
    "FMCG":     {"drivers":"Rural recovery, Inflation cooling, Volume growth","risk":"Input cost spike, Competition","season":"Q2 Q3 strong"},
    "Metal":    {"drivers":"China demand, Global commodity cycle, Infra spend","risk":"China slowdown, Oversupply","season":"H1 strong"},
    "Energy":   {"drivers":"Oil prices, Refining margins, Govt support","risk":"Crude volatility, Policy","season":"Winter strong"},
    "Realty":   {"drivers":"Low rates, Urbanisation, Govt housing push","risk":"Rate hike, Regulatory","season":"H2 strong"},
    "Infra":    {"drivers":"Govt capex, Budget allocation, Order inflow","risk":"Execution delays, Cost overrun","season":"Budget season"},
    "Cons Dur": {"drivers":"Premiumisation, Urban spending, Credit growth","risk":"Inflation, Rural slowdown","season":"Festival season"},
    "PSE":      {"drivers":"Govt capex, PSU reform, Divestment","risk":"Policy change, Bureaucracy","season":"Budget season"},
    "MNC":      {"drivers":"Global demand, Royalty income, Premium pricing","risk":"Currency, Global slowdown","season":"Consistent"},
    "Media":    {"drivers":"Ad spend recovery, OTT growth, Sports events","risk":"Cord cutting, Competition","season":"IPL, Festival"}
}

# ── Stocks ────────────────────────────────────────────────────────────────────
NIFTY500=[
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
    nifty_close=get_close("^NSEI","1y")
    bank_close=get_close("^NSEBANK")
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
</div>""", unsafe_allow_html=True)

hc1,hc2=st.columns([1,10])
with hc1: st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png",width=60)
with hc2:
    st.markdown("<h2 style='color:#00e676;margin:0 0 4px 0;font-size:20px;letter-spacing:.05em'>⚡ MOMENTUM FRENZY TRADING TERMINAL</h2>",unsafe_allow_html=True)
    st.markdown("<p style='color:#555;font-size:12px;margin:0'>Indian Markets · Nifty 500 · Sector Intelligence</p>",unsafe_allow_html=True)

tab1,tab2,tab3,tab4=st.tabs(["📊 Market & Scanner","📈 Charts","💼 Portfolio","📲 Alerts"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Sector Intelligence ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🧠 Sector Intelligence — Forward Outlook</div>",unsafe_allow_html=True)

    with st.spinner("Analyzing 14 sectors…"):
        si_df = get_sector_intelligence(SECTORS, nifty_close)

    if len(si_df) > 0:
        # Top 3 sectors highlight
        top3 = si_df.head(3)
        t1,t2,t3 = st.columns(3)
        for col, (_, row) in zip([t1,t2,t3], top3.iterrows()):
            with col:
                macro = SECTOR_MACRO.get(row["Sector"], {})
                st.markdown(f"""
                <div style='background:#0f0f1a;border:1px solid {row["OutlookColor"]}44;border-radius:10px;padding:14px;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                    <div style='font-size:15px;font-weight:700;color:#e0e0e0;'>{row["Sector"]}</div>
                    <div style='background:{row["OutlookColor"]}22;color:{row["OutlookColor"]};font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;border:1px solid {row["OutlookColor"]}55;'>{row["OutlookLabel"]}</div>
                  </div>
                  <div style='font-size:22px;font-weight:800;color:{row["OutlookColor"]};margin-bottom:4px;'>{row["Outlook"]}<span style='font-size:12px;color:#555;font-weight:400;'>/100</span></div>
                  <div style='background:#1e1e3a;height:6px;border-radius:3px;margin-bottom:10px;'>
                    <div style='background:{row["OutlookColor"]};height:6px;border-radius:3px;width:{row["Outlook"]}%;'></div>
                  </div>
                  <div style='font-size:11px;color:#888;margin-bottom:6px;'>Trend: <span style='color:{row["TrendColor"]};font-weight:700;'>{row["Trend"]}</span> &nbsp;|&nbsp; RSI: <span style='color:#e0e0e0;'>{row["RSI"]:.0f}</span> &nbsp;|&nbsp; 52W: <span style='color:#e0e0e0;'>{row["52W Pos%"]:.0f}%</span></div>
                  <div style='font-size:11px;color:#666;'>RS vs Nifty: <span style='color:{"#00e676" if row["RS 1M"]>=0 else "#ff5252"};font-weight:600;'>{row["RS 1M"]:+.1f}% (1M)</span></div>
                  <div style='font-size:11px;color:#555;margin-top:6px;border-top:1px solid #1e1e3a;padding-top:6px;'>💡 {row["Trigger"]}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Full sector table with all data
        st.markdown("<div class='section-header'>📋 All Sectors — Deep Analysis</div>",unsafe_allow_html=True)

        view_cols = ["Sector","1W%","1M%","3M%","6M%","RS 1M","RS 3M","RSI","Trend","52W Pos%","Outlook","OutlookLabel","Trigger"]
        display_df = si_df[view_cols].copy()

        def style_outlook(val):
            if isinstance(val, (int, float)):
                if val >= 70: return "color:#00e676;font-weight:700"
                if val >= 55: return "color:#aaff00;font-weight:700"
                if val >= 40: return "color:#ffaa00"
                return "color:#ff5252"
            return ""

        def style_rs(val):
            if isinstance(val, (int, float)):
                return "color:#00e676" if val > 0 else "color:#ff5252"
            return ""

        def style_ret(val):
            if isinstance(val, (int, float)):
                return "color:#00e676" if val > 0 else "color:#ff5252"
            return ""

        styled_si = display_df.style\
            .map(style_outlook, subset=["Outlook"])\
            .map(style_rs, subset=["RS 1M","RS 3M"])\
            .map(style_ret, subset=["1W%","1M%","3M%","6M%"])\
            .format({"1W%":"{:+.1f}%","1M%":"{:+.1f}%","3M%":"{:+.1f}%","6M%":"{:+.1f}%",
                     "RS 1M":"{:+.1f}","RS 3M":"{:+.1f}","RSI":"{:.0f}","52W Pos%":"{:.0f}%","Outlook":"{:.0f}"})
        st.dataframe(styled_si, use_container_width=True, height=420)

        # Macro fundamentals expander
        with st.expander("📌 Sector Macro Drivers & Risks"):
            mc1,mc2=st.columns(2)
            items=list(SECTOR_MACRO.items())
            for i,(sec,macro) in enumerate(items):
                col=mc1 if i%2==0 else mc2
                with col:
                    row_data=si_df[si_df["Sector"]==sec]
                    oc="#888"
                    if len(row_data)>0: oc=row_data.iloc[0]["OutlookColor"]
                    st.markdown(f"""
                    <div style='background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid {oc};'>
                      <div style='font-size:13px;font-weight:700;color:#e0e0e0;margin-bottom:6px;'>{sec}</div>
                      <div style='font-size:11px;color:#00e676;margin-bottom:2px;'>✅ Drivers: {macro["drivers"]}</div>
                      <div style='font-size:11px;color:#ff5252;margin-bottom:2px;'>⚠️ Risks: {macro["risk"]}</div>
                      <div style='font-size:11px;color:#888;'>📅 Season: {macro["season"]}</div>
                    </div>""", unsafe_allow_html=True)

        # Sector comparison chart
        st.markdown("<div class='section-header'>📊 Sector Returns Comparison</div>",unsafe_allow_html=True)
        chart_period=st.radio("Period",["1W%","1M%","3M%","6M%"],horizontal=True,index=1)
        fig_sc=go.Figure()
        sorted_df=si_df.sort_values(chart_period,ascending=True)
        fig_sc.add_trace(go.Bar(
            x=sorted_df[chart_period], y=sorted_df["Sector"],
            orientation='h',
            marker_color=["#00e676" if v>0 else "#ff5252" for v in sorted_df[chart_period]],
            text=[f"{v:+.1f}%" for v in sorted_df[chart_period]],
            textposition="outside"
        ))
        fig_sc.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
            height=420,margin=dict(l=0,r=60,t=10,b=0),
            xaxis=dict(gridcolor="#1a1a2e",ticksuffix="%"),yaxis=dict(gridcolor="#1a1a2e"))
        st.plotly_chart(fig_sc,use_container_width=True)

        # 4 Quadrant
        st.markdown("<div class='section-header'>📊 4-Quadrant Rotation</div>",unsafe_allow_html=True)
        sector_df=si_df.copy()
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

        st.markdown(f"""<div class="quad-grid">
          <div class="quad quad-leading"><div class="quad-title">🚀 Leading (Strong 1M+3M)</div>{qs(leading)}</div>
          <div class="quad quad-improving"><div class="quad-title">📈 Improving (1M up, 3M lag)</div>{qs(improving)}</div>
          <div class="quad quad-weakening"><div class="quad-title">⚠️ Weakening (3M ok, 1M slow)</div>{qs(weakening)}</div>
          <div class="quad quad-lagging"><div class="quad-title">📉 Lagging (Weak 1M+3M)</div>{qs(lagging)}</div>
        </div>""",unsafe_allow_html=True)
    else:
        st.warning("Sector data unavailable. Try refreshing.")
        sector_df=pd.DataFrame()

    # ── Volume Punch ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>💥 Sector Volume Punch — Unusual Activity Detector</div>",unsafe_allow_html=True)

    with st.spinner("Analyzing sector volume punches…"):
        vol_data = get_sector_volume_punch(SECTORS)

    if vol_data:
        # Top punch cards
        vp1,vp2,vp3 = st.columns(3)
        for col, item in zip([vp1,vp2,vp3], vol_data[:3]):
            with col:
                bar_color = item["SigColor"]
                price_color = "#00e676" if item["PctToday"] >= 0 else "#ff5252"
                st.markdown(f"""
                <div style='background:#0f0f1a;border:1px solid {bar_color}44;border-radius:10px;padding:14px;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                    <div style='font-size:15px;font-weight:700;color:#e0e0e0;'>{item["Sector"]}</div>
                    <div style='font-size:11px;font-weight:700;color:{bar_color};'>{item["Signal"]}</div>
                  </div>
                  <div style='font-size:28px;font-weight:800;color:{bar_color};'>{item["Today Vol Ratio"]}x
                    <span style='font-size:12px;color:#555;font-weight:400;'>vs 20D avg</span></div>
                  <div style='font-size:12px;color:#888;margin-top:4px;'>
                    5D avg: <b style='color:#e0e0e0;'>{item["5D Avg Ratio"]}x</b> &nbsp;|&nbsp;
                    Today: <b style='color:{price_color};'>{item["PctToday"]:+.2f}%</b>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Volume punch bar chart — all sectors
        fig_vp = go.Figure()
        sec_names  = [d["Sector"] for d in vol_data]
        vol_ratios = [d["Today Vol Ratio"] for d in vol_data]
        colors_vp  = [d["SigColor"] for d in vol_data]
        pct_today  = [d["PctToday"] for d in vol_data]

        fig_vp.add_trace(go.Bar(
            x=sec_names, y=vol_ratios,
            marker_color=colors_vp,
            name="Vol Ratio",
            text=[f"{v:.1f}x" for v in vol_ratios],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Vol Ratio: %{y:.2f}x<extra></extra>"
        ))
        fig_vp.add_hline(y=1.0, line_color="#555", line_dash="dot",
                         annotation_text="Normal", annotation_font_color="#555")
        fig_vp.add_hline(y=2.0, line_color="rgba(255,170,0,0.4)", line_dash="dash",
                         annotation_text="High", annotation_font_color="#ffaa00")
        fig_vp.update_layout(
            plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
            font_color="#888", height=320,
            margin=dict(l=0,r=0,t=30,b=0),
            xaxis=dict(gridcolor="#1a1a2e"),
            yaxis=dict(gridcolor="#1a1a2e", title="Volume Ratio vs 20D Avg"),
            title=dict(text="Today's Volume Punch by Sector", font=dict(color="#888",size=13))
        )
        st.plotly_chart(fig_vp, use_container_width=True)

        # 30-day volume punch timeline for selected sector
        st.markdown("<div class='section-header'>📅 30-Day Volume History — Select Sector</div>", unsafe_allow_html=True)
        selected_sec = st.selectbox("Sector", [d["Sector"] for d in vol_data], key="vol_sec")
        sel_data = next((d for d in vol_data if d["Sector"]==selected_sec), None)
        if sel_data and sel_data["VolRatios"]:
            fig_hist = go.Figure()
            bar_colors = []
            for v in sel_data["VolRatios"]:
                if v >= 3.0:   bar_colors.append("#ff5252")
                elif v >= 2.0: bar_colors.append("#ffaa00")
                elif v >= 1.5: bar_colors.append("#aaff00")
                elif v >= 0.8: bar_colors.append("#00e676")
                else:          bar_colors.append("#333333")

            fig_hist.add_trace(go.Bar(
                x=sel_data["Dates"], y=sel_data["VolRatios"],
                marker_color=bar_colors, name="Vol Ratio",
                text=[f"{v:.1f}x" if v>=1.5 else "" for v in sel_data["VolRatios"]],
                textposition="outside"
            ))
            fig_hist.add_hline(y=1.0, line_color="#555", line_dash="dot")
            fig_hist.add_hline(y=2.0, line_color="rgba(255,170,0,0.4)", line_dash="dash")
            fig_hist.update_layout(
                plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
                font_color="#888", height=280,
                margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="#1a1a2e", tickangle=-45),
                yaxis=dict(gridcolor="#1a1a2e", title="Vol Ratio"),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            # Interpretation
            today_punch = sel_data["Today Vol Ratio"]
            if today_punch >= 2.0:
                st.markdown(f"""
                <div style='background:#2a1a0022;border:1px solid #ffaa0055;border-radius:8px;padding:12px;font-size:13px;'>
                  ⚡ <b style='color:#ffaa00;'>{selected_sec}</b> is showing <b>{today_punch}x</b> volume today.
                  High volume punches often signal institutional activity — a potential move is brewing.
                  Watch for breakout or reversal in next 1–3 days.
                </div>""", unsafe_allow_html=True)
            elif today_punch >= 1.5:
                st.markdown(f"""
                <div style='background:#1a2a0022;border:1px solid #aaff0055;border-radius:8px;padding:12px;font-size:13px;'>
                  📈 <b style='color:#aaff00;'>{selected_sec}</b> showing elevated volume ({today_punch}x).
                  Decent participation — monitor for continuation or accumulation signal.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:12px;font-size:13px;color:#666;'>
                  ➡️ {selected_sec} volume is normal ({today_punch}x). No unusual activity today.
                </div>""", unsafe_allow_html=True)

    # ── Scanner ───────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🔍 Nifty 500 Momentum Scanner</div>",unsafe_allow_html=True)
    sc1,sc2,sc3,sc4=st.columns(4)
    with sc1: sig_f=st.selectbox("Signal",["All","BUY","WATCH","AVOID"])
    with sc2: risk_f=st.selectbox("Risk",["All","Low","Medium","High"])
    with sc3: setup_f=st.selectbox("Setup",["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with sc4: top_n=st.selectbox("Stocks",["Top 50","Top 100","Top 150","All"],index=0)

    top_map={"Top 50":50,"Top 100":100,"Top 150":150,"All":len(NIFTY500)}
    scan_tickers=tuple(NIFTY500[:top_map[top_n]])

    with st.spinner(f"⚡ Scanning {len(scan_tickers)} stocks…"):
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
        st.caption(f"Showing {len(filtered)} of {len(scan_df)} stocks · 4hr cache")


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
                st.session_state.portfolio.append({"Stock":pstock,"Buy":pbuy,"Qty":pqty}); st.rerun()
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
            st.session_state.portfolio=[p for p in st.session_state.portfolio if p["Stock"]!=rem]; st.rerun()
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
        top_sec=si_df.iloc[0] if len(si_df)>0 else None
        return (
            f"<b>⚡ MOMENTUM FRENZY — {label}</b>\n"
            f"{datetime.now().strftime('%d %b %Y %H:%M IST')}\n\n"
            f"<b>Nifty:</b> {nifty_last:,.0f} ({nifty_chg:+.2f}%) | {state}\n"
            f"<b>BankNifty:</b> {bank_last:,.0f} ({bank_chg:+.2f}%)\n"
            f"<b>VIX:</b> {vix_last:.1f}\n\n"
            + (f"<b>🏆 Top Sector:</b> {top_sec['Sector']} — {top_sec['OutlookLabel']} ({top_sec['Outlook']}/100)\n\n" if top_sec is not None else "")
            + f"<b>🟢 BUY:</b> {', '.join(buys) or 'None'}\n"
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
