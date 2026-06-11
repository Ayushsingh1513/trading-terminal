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

st.set_page_config(
    page_title="Momentum Frenzy — Indian Stock Scanner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state.page = "landing"

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html,body,.stApp{
        background:#07091A;
        color:#CBD5E1;
        font-family:'Inter',sans-serif;
    }
    .block-container{padding:0;max-width:100%;}
    header[data-testid="stHeader"]{display:none;}
    #MainMenu{display:none;}
    footer{display:none;}

    /* ── NAV ── */
    .lp-nav{
        display:flex;align-items:center;justify-content:space-between;
        padding:16px 40px;border-bottom:1px solid #0F1A35;
        background:#07091A;position:sticky;top:0;z-index:99;
    }
    .lp-logo{
        display:flex;align-items:center;gap:10px;
        font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;
        color:#F1F5F9;letter-spacing:-.01em;
    }
    .lp-logo-dot{
        width:8px;height:8px;border-radius:50%;
        background:#3B7DFB;box-shadow:0 0 6px #3B7DFB88;
    }
    .lp-nav-links{display:flex;align-items:center;gap:8px;}
    .lp-nav-tag{
        font-size:11px;color:#475569;
        border:1px solid #0F1A35;border-radius:4px;
        padding:4px 10px;letter-spacing:.06em;text-transform:uppercase;
        font-weight:500;
    }

    /* ── HERO ── */
    .lp-hero{
        min-height:88vh;
        display:flex;flex-direction:column;
        align-items:center;justify-content:center;
        text-align:center;padding:60px 24px 40px;
        position:relative;overflow:hidden;
    }
    .lp-hero::before{
        content:'';position:absolute;
        top:-200px;left:50%;transform:translateX(-50%);
        width:700px;height:700px;border-radius:50%;
        background:radial-gradient(circle,#1a2d6622 0%,transparent 70%);
        pointer-events:none;
    }
    .lp-eyebrow{
        display:inline-flex;align-items:center;gap:6px;
        background:#0D1634;border:1px solid #1E3057;
        border-radius:4px;padding:5px 14px;
        font-family:'JetBrains Mono',monospace;
        font-size:11px;color:#3B7DFB;font-weight:600;
        letter-spacing:.1em;text-transform:uppercase;
        margin-bottom:28px;
    }
    .lp-eyebrow-dot{
        width:5px;height:5px;border-radius:50%;
        background:#3B7DFB;animation:blink 1.4s infinite;
    }
    @keyframes blink{0%,100%{opacity:1;}50%{opacity:.3;}}
    .lp-h1{
        font-size:clamp(42px,6.5vw,84px);font-weight:800;
        line-height:1.05;letter-spacing:-.03em;
        color:#F1F5F9;margin:0 0 10px 0;
        max-width:820px;
    }
    .lp-h1 span{
        color:transparent;
        background:linear-gradient(135deg,#3B7DFB,#06B6D4);
        -webkit-background-clip:text;background-clip:text;
    }
    .lp-sub{
        font-size:clamp(15px,1.8vw,19px);color:#64748B;
        max-width:520px;line-height:1.75;margin:16px auto 44px;
        font-weight:400;
    }
    .lp-cta-row{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;}

    /* ── STAT STRIP ── */
    .lp-stats{
        display:flex;gap:0;
        border:1px solid #0F1A35;border-radius:10px;
        background:#0D1120;overflow:hidden;
        max-width:640px;margin:56px auto 0;
    }
    .lp-stat{
        flex:1;padding:20px 24px;text-align:center;
        border-right:1px solid #0F1A35;
    }
    .lp-stat:last-child{border-right:none;}
    .lp-stat-n{
        font-family:'JetBrains Mono',monospace;
        font-size:26px;font-weight:700;color:#3B7DFB;
        line-height:1;
    }
    .lp-stat-l{font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:.1em;margin-top:5px;}

    /* ── FEATURES ── */
    .lp-section{max-width:1080px;margin:80px auto;padding:0 24px;}
    .lp-section-label{
        font-family:'JetBrains Mono',monospace;
        font-size:10px;color:#3B7DFB;letter-spacing:.15em;
        text-transform:uppercase;font-weight:600;margin-bottom:14px;
    }
    .lp-section-h{
        font-size:28px;font-weight:700;color:#E2E8F0;
        letter-spacing:-.02em;margin-bottom:36px;line-height:1.3;
    }
    .feat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1px;background:#0F1A35;border:1px solid #0F1A35;border-radius:10px;overflow:hidden;}
    .feat-item{background:#0D1120;padding:28px;transition:background .2s;}
    .feat-item:hover{background:#101828;}
    .feat-icon-wrap{
        width:36px;height:36px;border-radius:8px;
        background:#0D1634;border:1px solid #1E3057;
        display:flex;align-items:center;justify-content:center;
        font-size:17px;margin-bottom:14px;
    }
    .feat-title{font-size:14px;font-weight:600;color:#E2E8F0;margin-bottom:7px;}
    .feat-desc{font-size:12px;color:#475569;line-height:1.7;}

    /* ── DISCLAIMER ── */
    .lp-disc{
        max-width:680px;margin:40px auto 0;
        padding:14px 20px;
        background:#0D1120;border:1px solid #0F1A35;border-radius:6px;
        font-size:11px;color:#334155;text-align:center;line-height:1.7;
    }
    .lp-footer{
        text-align:center;padding:28px;
        border-top:1px solid #0A1020;
        color:#1E2D47;font-size:11px;margin-top:60px;
    }
    .lp-footer a{color:#1E3A7A;text-decoration:none;}
    </style>

    <div class="lp-nav">
        <div class="lp-logo">
            <div class="lp-logo-dot"></div>
            MomentumFrenzy
        </div>
        <div class="lp-nav-links">
            <div class="lp-nav-tag">Free · No Login · NSE</div>
        </div>
    </div>

    <div class="lp-hero">
        <div class="lp-eyebrow"><div class="lp-eyebrow-dot"></div>Indian Markets · Swing Trading Terminal</div>
        <h1 class="lp-h1">Find the trade.<br><span>Before the move.</span></h1>
        <p class="lp-sub">Professional momentum scanner for Nifty 500. Entry, Stop Loss, and Targets auto-calculated every morning — free, always.</p>
        <div class="lp-stats">
            <div class="lp-stat"><div class="lp-stat-n">500+</div><div class="lp-stat-l">Stocks Scanned</div></div>
            <div class="lp-stat"><div class="lp-stat-n">14</div><div class="lp-stat-l">Sectors Tracked</div></div>
            <div class="lp-stat"><div class="lp-stat-n">4hrs</div><div class="lp-stat-l">Cache Refresh</div></div>
            <div class="lp-stat"><div class="lp-stat-n">Free</div><div class="lp-stat-l">Always</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3=st.columns([1,1,1])
    with c2:
        if st.button("⚡  Open Terminal — Free", use_container_width=True, type="primary"):
            st.session_state.page = "terminal"; st.rerun()
        st.markdown("<p style='text-align:center;color:#1E3057;font-size:11px;margin-top:6px;font-family:\"JetBrains Mono\",monospace;'>No account · No download · Updated 4hrs</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="lp-section">
        <div class="lp-section-label">What's inside</div>
        <div class="lp-section-h">Everything you need.<br>Nothing you don't.</div>
        <div class="feat-grid">
            <div class="feat-item">
                <div class="feat-icon-wrap">🎯</div>
                <div class="feat-title">Daily Trade Picks</div>
                <div class="feat-desc">Entry, Stop Loss, Target 1 &amp; Target 2 with Risk:Reward — auto-calculated every morning from the Nifty 500 universe.</div>
            </div>
            <div class="feat-item">
                <div class="feat-icon-wrap">🧭</div>
                <div class="feat-title">Market Mood Score</div>
                <div class="feat-desc">BULLISH / NEUTRAL / BEARISH reading built from Nifty vs MA200, MA50, and India VIX. Know the regime before you trade.</div>
            </div>
            <div class="feat-item">
                <div class="feat-icon-wrap">💥</div>
                <div class="feat-title">Breakout Radar</div>
                <div class="feat-desc">Stocks crossing key levels with volume surge vs 20-day average. Ranked by momentum score before the crowd arrives.</div>
            </div>
            <div class="feat-item">
                <div class="feat-icon-wrap">🔄</div>
                <div class="feat-title">Sector Rotation</div>
                <div class="feat-desc">4-quadrant view of all 14 NSE sectors — Leading, Improving, Weakening, Lagging — plus volume punch intensity.</div>
            </div>
            <div class="feat-item">
                <div class="feat-icon-wrap">📈</div>
                <div class="feat-title">Pro Charts</div>
                <div class="feat-desc">Candlestick charts with EMA 20/50/200 overlays and volume bars for any Nifty 500 stock across multiple timeframes.</div>
            </div>
            <div class="feat-item">
                <div class="feat-icon-wrap">📲</div>
                <div class="feat-title">Telegram Alerts</div>
                <div class="feat-desc">Morning and evening picks delivered directly to your Telegram before the bell — so you're always prepared.</div>
            </div>
        </div>
    </div>
    <div class="lp-disc">
        ⚠️ <strong style="color:#475569;">Disclaimer:</strong> Momentum Frenzy is for educational purposes only.
        Nothing on this platform constitutes financial advice. Always do your own research.
        Consult a SEBI-registered investment advisor before making any investment decisions.
    </div>
    <div class="lp-footer">
        © 2025 Momentum Frenzy &nbsp;·&nbsp; Indian Markets &nbsp;·&nbsp; Data: Yahoo Finance &nbsp;·&nbsp;
        <a href="https://instagram.com/momentumfrenzy">@momentumfrenzy</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL — GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── BASE ── */
html,body,.stApp{
    background:#07091A;
    color:#CBD5E1;
    font-family:'Inter',sans-serif;
}
.block-container{padding:0 0 4rem 0;max-width:100%;}
header[data-testid="stHeader"]{display:none;}
#MainMenu{display:none;}
footer{display:none;}

/* ── TOP TICKER BAR ── */
.ticker-bar{
    background:#0A0E1E;
    border-bottom:1px solid #0F1A35;
    padding:0 20px;
    display:flex;align-items:center;
    gap:0;
    position:sticky;top:0;z-index:999;
    height:40px;overflow:hidden;
}
.ticker-item{
    display:flex;align-items:center;gap:8px;
    padding:0 18px;border-right:1px solid #0F1A35;
    height:100%;
}
.ticker-item:last-child{border-right:none;}
.ticker-label{
    font-family:'JetBrains Mono',monospace;
    font-size:9px;color:#334155;
    text-transform:uppercase;letter-spacing:.1em;font-weight:500;
}
.ticker-val{
    font-family:'JetBrains Mono',monospace;
    font-size:13px;font-weight:600;color:#94A3B8;
}
.tv-up{color:#00D68F!important;}
.tv-down{color:#FF4C4C!important;}
.tv-blue{color:#3B7DFB!important;}
.ticker-spacer{flex:1;}
.ticker-time{
    font-family:'JetBrains Mono',monospace;
    font-size:10px;color:#1E2D47;
    padding-left:16px;
}

/* ── HEADER STRIP ── */
.hdr-strip{
    display:flex;align-items:center;justify-content:space-between;
    padding:10px 20px;border-bottom:1px solid #0A1020;
    background:#07091A;
}
.hdr-logo{
    display:flex;align-items:center;gap:10px;
}
.hdr-logo-mark{
    width:32px;height:32px;border-radius:8px;
    background:linear-gradient(135deg,#1E3A8A,#1D4ED8);
    display:flex;align-items:center;justify-content:center;
    font-size:16px;
}
.hdr-title{
    font-family:'JetBrains Mono',monospace;
    font-size:14px;font-weight:700;color:#F1F5F9;
    letter-spacing:-.01em;
}
.hdr-sub{font-size:10px;color:#1E3A8A;margin-top:1px;letter-spacing:.04em;}
.hdr-tag{
    display:flex;align-items:center;gap:6px;
    font-size:11px;color:#334155;
    border:1px solid #0F1A35;border-radius:4px;
    padding:4px 10px;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
    background:#07091A;
    border-bottom:1px solid #0F1A35;
    padding:0 20px;gap:0;
}
.stTabs [data-baseweb="tab"]{
    background:transparent;
    color:#475569;
    font-size:12px;font-weight:500;
    padding:10px 18px;
    border-bottom:2px solid transparent;
    border-radius:0;
}
.stTabs [aria-selected="true"]{
    color:#3B7DFB!important;
    border-bottom-color:#3B7DFB!important;
    background:transparent!important;
}
.stTabs [data-baseweb="tab-panel"]{padding:0 20px;}

/* ── SECTION HEADER ── */
.sec-hdr{
    display:flex;align-items:center;gap:10px;
    padding:18px 0 10px 0;
    border-bottom:1px solid #0A1020;
    margin-bottom:14px;
}
.sec-hdr-line{width:3px;height:16px;background:#3B7DFB;border-radius:2px;flex-shrink:0;}
.sec-hdr-text{font-size:11px;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:.12em;}

/* ── MOOD BANNER ── */
.mood-banner{
    display:flex;align-items:stretch;gap:0;
    background:#0D1120;border:1px solid #0F1A35;
    border-radius:10px;overflow:hidden;margin:12px 0 16px;
}
.mood-side{
    width:5px;flex-shrink:0;
}
.mood-content{
    flex:1;padding:16px 20px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;
}
.mood-label-sm{font-size:9px;color:#334155;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;}
.mood-value{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;line-height:1;}
.mood-score-row{display:flex;align-items:center;gap:8px;margin-top:4px;}
.mood-score-bar-bg{flex:1;height:4px;background:#0A1020;border-radius:2px;}
.mood-score-bar-fill{height:4px;border-radius:2px;}
.mood-score-num{font-family:'JetBrains Mono',monospace;font-size:11px;color:#334155;}
.mood-meta{font-size:11px;color:#334155;line-height:1.8;}
.mood-tip{font-size:12px;color:#475569;margin-top:6px;padding-top:6px;border-top:1px solid #0A1020;}

/* ── PICK CARD ── */
.pick-card{
    background:#0D1120;
    border:1px solid #0F1A35;
    border-radius:10px;
    overflow:hidden;
    margin-bottom:10px;
    transition:border-color .2s;
}
.pick-card:hover{border-color:#1E3A8A;}
.pick-card-head{
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 16px 10px;
    border-bottom:1px solid #0A1020;
}
.pick-stock{
    font-family:'JetBrains Mono',monospace;
    font-size:17px;font-weight:700;color:#F1F5F9;
}
.pick-setup{font-size:11px;color:#475569;margin-top:2px;}
.pick-buy-badge{
    background:#0C1F0F;color:#00D68F;
    font-family:'JetBrains Mono',monospace;
    font-size:10px;font-weight:700;
    padding:4px 10px;border-radius:4px;
    border:1px solid #00D68F22;letter-spacing:.08em;
}
.pick-grid{
    display:grid;grid-template-columns:1fr 1fr;
    gap:1px;background:#0A1020;
}
.pick-cell{background:#0D1120;padding:10px 14px;}
.pick-cell-lbl{font-size:9px;color:#334155;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px;}
.pick-cell-val{
    font-family:'JetBrains Mono',monospace;
    font-size:15px;font-weight:600;
}
.pv-entry{color:#E2E8F0;}
.pv-sl{color:#FF4C4C;}
.pv-t1{color:#00D68F;}
.pv-t2{color:#06B6D4;}
.pick-foot{
    display:flex;align-items:center;justify-content:space-between;
    padding:9px 14px;border-top:1px solid #0A1020;
}
.pick-rr{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;}
.pick-meta{display:flex;gap:14px;font-size:11px;color:#334155;}
.pick-meta span{font-family:'JetBrains Mono',monospace;}

/* ── SCANNER TABLE FIXES ── */
.stDataFrame{border:1px solid #0F1A35;border-radius:8px;overflow:hidden;}
.stDataFrame [data-testid="stDataFrame"]{background:#0D1120;}
div[data-testid="metric-container"]{
    background:#0D1120;border:1px solid #0F1A35;
    border-radius:8px;padding:10px 14px;
}
div[data-testid="metric-container"] label{color:#334155;font-size:10px;}
div[data-testid="metric-container"] [data-testid="metric-value"]{
    font-family:'JetBrains Mono',monospace;color:#F1F5F9;font-size:20px;
}

/* ── AD SLOT ── */
.ad-slot{
    background:#07091A;border:1px dashed #0F1A35;
    border-radius:6px;padding:16px;
    text-align:center;color:#1E2D47;
    font-size:10px;letter-spacing:.1em;
    text-transform:uppercase;font-weight:500;
    margin:16px 0;
}

/* ── SECTOR QUAD ── */
.sq-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.sq-card{border-radius:8px;padding:14px;min-height:90px;}
.sq-leading{background:#051409;border:1px solid #00D68F22;}
.sq-improving{background:#07100A;border:1px solid #06B6D422;}
.sq-weakening{background:#120E05;border:1px solid #FFB02022;}
.sq-lagging{background:#120505;border:1px solid #FF4C4C22;}
.sq-title{
    font-size:9px;font-weight:700;text-transform:uppercase;
    letter-spacing:.12em;margin-bottom:8px;
    font-family:'JetBrains Mono',monospace;
}
.sq-leading .sq-title{color:#00D68F;}
.sq-improving .sq-title{color:#06B6D4;}
.sq-weakening .sq-title{color:#FFB020;}
.sq-lagging .sq-title{color:#FF4C4C;}
.sq-chip{
    display:inline-flex;align-items:center;gap:4px;
    font-size:10px;padding:2px 7px;border-radius:3px;
    background:#FFFFFF08;color:#94A3B8;
    margin:2px;font-family:'JetBrains Mono',monospace;
}
.sq-chip b{font-weight:600;}

/* ── INSTAGRAM CTA ── */
.ig-cta{
    background:#0D1120;border:1px solid #0F1A35;
    border-radius:10px;padding:24px;text-align:center;margin:20px 0;
}
.ig-cta-title{font-size:16px;font-weight:600;color:#E2E8F0;margin-bottom:6px;}
.ig-cta-sub{font-size:13px;color:#475569;margin-bottom:16px;}
.ig-btn{
    display:inline-block;
    background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);
    color:#fff;padding:9px 28px;border-radius:6px;
    text-decoration:none;font-size:13px;font-weight:600;
}

/* ── SELECTBOXES / BUTTONS ── */
.stSelectbox [data-baseweb="select"]{
    background:#0D1120;border:1px solid #0F1A35;border-radius:6px;
}
.stButton button[kind="primary"]{
    background:linear-gradient(135deg,#1D4ED8,#1E3A8A);
    border:none;color:#fff;font-weight:600;
    border-radius:6px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except:
        pass

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

@st.cache_data(ttl=14400)
def get_close(t, p="6mo"):
    for _ in range(2):
        try:
            df = yf.download(t, period=p, interval="1d", progress=False, auto_adjust=True)
            r = df['Close'].squeeze().dropna()
            if len(r) > 2: return r
        except: pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=14400)
def get_ohlcv(t, p="6mo"):
    for _ in range(2):
        try:
            df = yf.download(t, period=p, interval="1d", progress=False, auto_adjust=True)
            if len(df) > 2: return df
        except: pass
    return pd.DataFrame()

@st.cache_data(ttl=14400)
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
                        close = raw['Close'].squeeze().dropna()
                        high  = raw['High'].squeeze().dropna()
                        low   = raw['Low'].squeeze().dropna()
                        vol   = raw['Volume'].squeeze().dropna()
                    else:
                        close = raw[t]['Close'].squeeze().dropna()
                        high  = raw[t]['High'].squeeze().dropna()
                        low   = raw[t]['Low'].squeeze().dropna()
                        vol   = raw[t]['Volume'].squeeze().dropna()
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

@st.cache_data(ttl=14400)
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

@st.cache_data(ttl=7200)
def get_sector_vol_punch(sectors):
    rows = []
    for name, ticker in sectors.items():
        try:
            df   = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
            if len(df) < 20: continue
            vol  = df['Volume'].squeeze().dropna()
            avg20= float(vol.rolling(20).mean().iloc[-1])
            today= float(vol.iloc[-1])
            punch= round(today/avg20, 2) if avg20 > 0 else 1.0
            avg5 = float(vol.rolling(5).mean().iloc[-1])
            punch5=round(avg5/avg20, 2) if avg20 > 0 else 1.0
            close= df['Close'].squeeze().dropna()
            pct  = float((close.iloc[-1]/close.iloc[-2]-1)*100) if len(close)>=2 else 0
            recent_vol  = vol.iloc[-30:]
            recent_avg  = float(vol.iloc[-50:-30].mean()) if len(vol)>=50 else avg20
            vol_ratios  = (recent_vol/recent_avg).round(2).tolist()
            dates = [str(d.date()) for d in recent_vol.index]
            rows.append({"Sector": name, "Punch": punch, "Punch5": punch5,
                         "PctToday": round(pct,2), "Dates": dates, "VolRatios": vol_ratios})
        except: pass
    return sorted(rows, key=lambda x: x["Punch"], reverse=True)


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

SECTORS = {
    "IT": "^CNXIT", "Pvt Bank": "^CNXPVTBANK", "PSU Bank": "^CNXPSUBANK",
    "Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA", "FMCG": "^CNXFMCG",
    "Metal": "^CNXMETAL", "Energy": "^CNXENERGY", "Realty": "^CNXREALTY",
    "Infra": "^CNXINFRA", "Cons Dur": "^CNXCONSUM", "PSE": "^CNXPSE",
    "MNC": "^CNXMNC", "Media": "^CNXMEDIA"
}


# ── Market Data ────────────────────────────────────────────────────────────────
with st.spinner(""):
    nifty_c = get_close("^NSEI", "1y")
    bank_c  = get_close("^NSEBANK")
    vix_c   = get_close("^INDIAVIX", "1mo")

if len(nifty_c) < 2 or len(bank_c) < 2:
    st.error("⚠️ Data unavailable. Refresh in 1–2 minutes."); st.stop()

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
  <span class="ticker-time">{datetime.now().strftime('%d %b %Y  %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
hc1, hc2, hc3 = st.columns([1, 8, 2])
with hc1:
    st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png", width=48)
with hc2:
    st.markdown("""
    <div style='padding:8px 0 4px;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:15px;font-weight:700;color:#F1F5F9;letter-spacing:-.01em;'>
        ⚡ MOMENTUM FRENZY
      </div>
      <div style='font-size:10px;color:#1E3A8A;letter-spacing:.06em;margin-top:2px;'>
        INDIAN MARKETS &nbsp;·&nbsp; SWING TRADING SCANNER &nbsp;·&nbsp; FREE
      </div>
    </div>""", unsafe_allow_html=True)
with hc3:
    st.markdown("""
    <div style='text-align:right;padding-top:10px;'>
      <a href='https://instagram.com/momentumfrenzy' target='_blank'
         style='font-size:11px;color:#334155;text-decoration:none;
         border:1px solid #0F1A35;padding:5px 12px;border-radius:4px;
         font-family:"JetBrains Mono",monospace;'>
        @momentumfrenzy
      </a>
    </div>""", unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  🎯  Picks & Scanner  ", "  📈  Charts  ", "  📊  Sector Intelligence  "])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PICKS & SCANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Mood Banner ────────────────────────────────────────────────────────────
    mood_bars = {"BULLISH": "Above MA200 · Above MA50 · Trend intact", "NEUTRAL": "Mixed signals — wait for clear setups", "BEARISH": "Below key averages — risk-off mode"}
    mood_tips = {"BULLISH": "Market structure is healthy. BUY setups have higher follow-through today.",
                 "NEUTRAL": "Trade selectively. Only high-score setups worth considering.",
                 "BEARISH": "Avoid fresh longs. Focus on capital protection."}
    ma200_txt = "✓ Above MA200" if nl>ma200 else "✗ Below MA200"
    ma50_txt  = "✓ Above MA50"  if nl>ma50  else "✗ Below MA50"
    vix_txt   = "✓ VIX low"    if vl<15 else ("⚠ VIX elevated" if vl<20 else "✗ VIX high")

    st.markdown(f"""
    <div class="mood-banner">
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
          <div class="mood-meta" style="font-family:'JetBrains Mono',monospace;">
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

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    # ── Today's Picks ──────────────────────────────────────────────────────────
    st.markdown("<div class='sec-hdr'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Today's Top Swing Trade Picks</div></div>", unsafe_allow_html=True)

    with st.spinner("Scanning for best setups…"):
        picks = get_top_picks(tuple(NIFTY500[:100]), nifty_1m)

    if picks:
        pc1, pc2, pc3 = st.columns(3)
        for col, pk in zip([pc1, pc2, pc3], picks[:3]):
            rr_c = "#00D68F" if pk["RR"] >= 2 else "#FFB020" if pk["RR"] >= 1.5 else "#FF4C4C"
            setup_map = {"Breakout": "🚀 Breakout", "Pullback": "↩ Pullback", "Vol Surge": "💥 Vol Surge", "Trend": "↗ Trend"}
            with col:
                st.markdown(f"""
                <div class="pick-card">
                  <div class="pick-card-head">
                    <div>
                      <div class="pick-stock">{pk["Stock"]}</div>
                      <div class="pick-setup">{setup_map.get(pk["Setup"], pk["Setup"])} &nbsp;·&nbsp; Score {pk["Score"]}/100</div>
                    </div>
                    <div class="pick-buy-badge">BUY</div>
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
            st.markdown("<div class='sec-hdr' style='margin-top:8px;'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>More Setups</div></div>", unsafe_allow_html=True)
            more_df = pd.DataFrame(picks[3:]).rename(columns={
                "Stock":"Stock","Price":"CMP","Setup":"Setup","Score":"Score",
                "Entry":"Entry ₹","SL":"SL ₹","Target1":"T1 ₹","Target2":"T2 ₹","RR":"R:R"
            })[["Stock","CMP","Setup","Score","Entry ₹","SL ₹","T1 ₹","T2 ₹","R:R","RSI","VolSurge"]]
            st.dataframe(
                more_df.style.map(style_sc, subset=["Score"])
                .format({"CMP":"{:.1f}","Entry ₹":"{:.1f}","SL ₹":"{:.1f}","T1 ₹":"{:.1f}","T2 ₹":"{:.1f}","R:R":"{:.1f}","RSI":"{:.1f}","VolSurge":"{:.1f}x"}),
                use_container_width=True, height=260)
    else:
        st.info("No high-quality setups found today. Market may be in consolidation — wait for better opportunities.")

    st.markdown("<p style='font-size:10px;color:#1E2D47;text-align:right;margin-top:4px;font-family:\"JetBrains Mono\",monospace;'>⚠ Educational only. Not financial advice. DYOR.</p>", unsafe_allow_html=True)

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    # ── Full Scanner ───────────────────────────────────────────────────────────
    st.markdown("<div class='sec-hdr'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Full Momentum Scanner</div></div>", unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1: sf     = st.selectbox("Signal", ["All","BUY","WATCH","AVOID"])
    with fc2: rf     = st.selectbox("Risk",   ["All","Low","Medium","High"])
    with fc3: setupf = st.selectbox("Setup",  ["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with fc4: tn     = st.selectbox("Universe",["Top 50","Top 100","Top 150"], index=0)

    tm = {"Top 50":50, "Top 100":100, "Top 150":150}
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
        st.caption(f"Showing {len(filt)} of {len(scan_df)} stocks &nbsp;·&nbsp; Data: Yahoo Finance &nbsp;·&nbsp; Cached 4hrs")
    else:
        st.warning("No data available. Try refreshing.")

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="ig-cta">
      <div class="ig-cta-title">Follow @momentumfrenzy on Instagram</div>
      <div class="ig-cta-sub">Daily breakout ideas, trade setups and market analysis</div>
      <a class="ig-btn" href="https://instagram.com/momentumfrenzy" target="_blank">Follow Now</a>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("<div class='sec-hdr'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Stock Chart</div></div>", unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns([2,1,1])
    with cc1: sel   = st.selectbox("Stock", [t.replace(".NS","") for t in NIFTY500])
    with cc2: per   = st.selectbox("Period", ["3mo","6mo","1y"])
    with cc3: ctype = st.selectbox("Type", ["Candles","Line"])

    sdf = get_ohlcv(sel+".NS", per)
    if len(sdf) > 0:
        sc2_ = sdf['Close'].squeeze(); sv_ = sdf['Volume'].squeeze()
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75,0.25], vertical_spacing=0.02)
        if ctype == "Candles":
            fig2.add_trace(go.Candlestick(
                x=sdf.index, open=sdf['Open'].squeeze(), high=sdf['High'].squeeze(),
                low=sdf['Low'].squeeze(), close=sc2_, name=sel,
                increasing_line_color="#00D68F", decreasing_line_color="#FF4C4C"), row=1, col=1)
        else:
            fig2.add_trace(go.Scatter(x=sdf.index, y=sc2_, name=sel, line=dict(color="#3B7DFB",width=1.5)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=sdf.index, y=sc2_.ewm(span=20).mean(),  name="EMA20",  line=dict(color="#00D68F",width=1)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=sdf.index, y=sc2_.ewm(span=50).mean(),  name="EMA50",  line=dict(color="#FFB020",width=1)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=sdf.index, y=sc2_.ewm(span=200).mean(), name="EMA200", line=dict(color="#FF4C4C",width=1,dash="dot")), row=1, col=1)
        vc2 = ["rgba(0,214,143,0.35)" if c>=o else "rgba(255,76,76,0.35)"
               for c, o in zip(sdf['Close'].squeeze(), sdf['Open'].squeeze())]
        fig2.add_trace(go.Bar(x=sdf.index, y=sv_, marker_color=vc2, showlegend=False), row=2, col=1)
        fig2.update_layout(
            plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
            height=520, margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#0A1020", rangeslider=dict(visible=False), showgrid=True),
            xaxis2=dict(gridcolor="#0A1020"), yaxis=dict(gridcolor="#0A1020"),
            yaxis2=dict(gridcolor="#0A1020"),
            legend=dict(bgcolor="#0D1120", bordercolor="#0F1A35", font=dict(size=11, family="JetBrains Mono")))
        st.plotly_chart(fig2, use_container_width=True)

        if picks and sel in [p["Stock"] for p in picks]:
            pk = [p for p in picks if p["Stock"]==sel][0]
            m1,m2,m3,m4,m5,m6 = st.columns(6)
            m1.metric("Entry",    f"₹{pk['Entry']}")
            m2.metric("Target 1", f"₹{pk['Target1']}")
            m3.metric("Target 2", f"₹{pk['Target2']}")
            m4.metric("Stop Loss",f"₹{pk['SL']}")
            m5.metric("R:R",      f"1:{pk['RR']}")
            m6.metric("Score",    f"{pk['Score']}/100")

    st.markdown("<div class='sec-hdr' style='margin-top:16px;'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Nifty 50 — 1 Year</div></div>", unsafe_allow_html=True)
    ndf = get_ohlcv("^NSEI","1y")
    if len(ndf) > 0:
        nc_ = ndf['Close'].squeeze()
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ndf.index, y=nc_, name="Nifty 50",
            line=dict(color="#3B7DFB",width=1.5), fill="tozeroy", fillcolor="rgba(59,125,251,0.06)"))
        fig3.add_trace(go.Scatter(x=ndf.index, y=nc_.rolling(200).mean(), name="MA200",
            line=dict(color="#FF4C4C",dash="dash",width=1)))
        fig3.add_trace(go.Scatter(x=ndf.index, y=nc_.rolling(50).mean(), name="MA50",
            line=dict(color="#FFB020",dash="dot",width=1)))
        fig3.update_layout(
            plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
            height=300, margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#0A1020"), yaxis=dict(gridcolor="#0A1020"),
            legend=dict(bgcolor="#0D1120", bordercolor="#0F1A35", font=dict(size=11, family="JetBrains Mono")))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECTOR INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("<div class='sec-hdr'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Rotation — 4 Quadrant</div></div>", unsafe_allow_html=True)

    with st.spinner("Loading sectors…"):
        rows = []
        for name, ticker in SECTORS.items():
            try:
                close = get_close(ticker,"3mo")
                if len(close) < 20: continue
                r1m = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                r3m = float((close.iloc[-1]/close.iloc[0]-1)*100)
                rows.append({"Sector": name, "1M%": round(r1m,2), "3M%": round(r3m,2), "Score": round(r1m*.6+r3m*.4,2)})
            except: pass

    sector_df = pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)
    if len(sector_df) > 0:
        med1 = sector_df["1M%"].median(); med3 = sector_df["3M%"].median()
        leading  = sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]>=med3)]["Sector"].tolist()
        improving= sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]<med3)]["Sector"].tolist()
        weakening= sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]>=med3)]["Sector"].tolist()
        lagging  = sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]<med3)]["Sector"].tolist()

        def qs(lst):
            out = ""
            for s in lst:
                r = sector_df[sector_df["Sector"]==s].iloc[0]
                out += f'<span class="sq-chip">{s}&nbsp;<b style="color:#94A3B8">{r["1M%"]:+.1f}%</b></span>'
            return out or "<span style='color:#1E2D47;font-size:11px;'>—</span>"

        ql, qr = st.columns([1.2,1])
        with ql:
            st.markdown(f"""
            <div class="sq-grid">
              <div class="sq-card sq-leading">
                <div class="sq-title">↑ Leading</div>{qs(leading)}
              </div>
              <div class="sq-card sq-improving">
                <div class="sq-title">↗ Improving</div>{qs(improving)}
              </div>
              <div class="sq-card sq-weakening">
                <div class="sq-title">↘ Weakening</div>{qs(weakening)}
              </div>
              <div class="sq-card sq-lagging">
                <div class="sq-title">↓ Lagging</div>{qs(lagging)}
              </div>
            </div>""", unsafe_allow_html=True)
        with qr:
            fig_s = go.Figure(go.Bar(
                x=sector_df["Sector"], y=sector_df["Score"],
                marker_color=["#00D68F" if s>0 else "#FF4C4C" for s in sector_df["Score"]],
                text=[f"{s:+.1f}" for s in sector_df["Score"]], textposition="outside",
                textfont=dict(family="JetBrains Mono",size=10)))
            fig_s.update_layout(
                plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
                height=280, margin=dict(l=0,r=0,t=10,b=0),
                yaxis=dict(gridcolor="#0A1020"), xaxis=dict(gridcolor="#0A1020"))
            st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("<div class='sec-hdr'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Volume Punch</div></div>", unsafe_allow_html=True)
    with st.spinner("Analyzing volume activity…"):
        vp = get_sector_vol_punch(SECTORS)

    if vp:
        vp1, vp2, vp3 = st.columns(3)
        for col, item in zip([vp1,vp2,vp3], vp[:3]):
            bc = "#FF4C4C" if item["Punch"]>=3 else "#FFB020" if item["Punch"]>=2 else "#00D68F" if item["Punch"]>=1.5 else "#334155"
            pc2 = "#00D68F" if item["PctToday"]>=0 else "#FF4C4C"
            with col:
                st.markdown(f"""
                <div style='background:#0D1120;border:1px solid #0F1A35;border-left:3px solid {bc};border-radius:8px;padding:14px 16px;'>
                  <div style='font-size:11px;font-weight:600;color:#94A3B8;margin-bottom:6px;font-family:"JetBrains Mono",monospace;'>{item["Sector"]}</div>
                  <div style='font-family:"JetBrains Mono",monospace;font-size:28px;font-weight:700;color:{bc};line-height:1;'>{item["Punch"]}x</div>
                  <div style='font-size:10px;color:#334155;margin-top:4px;font-family:"JetBrains Mono",monospace;'>
                    Today &nbsp;<span style='color:{pc2};font-weight:600;'>{item["PctToday"]:+.2f}%</span>
                  </div>
                </div>""", unsafe_allow_html=True)

        sec_names  = [d["Sector"]  for d in vp]
        vol_ratios = [d["Punch"]   for d in vp]
        fig_vp = go.Figure()
        fig_vp.add_trace(go.Bar(
            x=sec_names, y=vol_ratios,
            marker_color=["#FF4C4C" if v>=3 else "#FFB020" if v>=2 else "#00D68F" if v>=1.5 else "#1E2D47" for v in vol_ratios],
            text=[f"{v:.1f}x" for v in vol_ratios], textposition="outside",
            textfont=dict(family="JetBrains Mono",size=10)))
        fig_vp.add_hline(y=1.0, line_color="#334155", line_dash="dot")
        fig_vp.add_hline(y=2.0, line_color="rgba(255,176,32,0.3)", line_dash="dash")
        fig_vp.update_layout(
            plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
            height=280, margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#0A1020"),
            yaxis=dict(gridcolor="#0A1020", title=dict(text="Vol vs 20D Avg",font=dict(family="JetBrains Mono",size=10))))
        st.plotly_chart(fig_vp, use_container_width=True)

        sel_sec = st.selectbox("30-Day Sector Volume History", [d["Sector"] for d in vp])
        sd = next((d for d in vp if d["Sector"]==sel_sec), None)
        if sd and sd["VolRatios"]:
            fig_h = go.Figure(go.Bar(
                x=sd["Dates"], y=sd["VolRatios"],
                marker_color=["#FF4C4C" if v>=3 else "#FFB020" if v>=2 else "#3B7DFB" if v>=1.5 else "#1E2D47" for v in sd["VolRatios"]]))
            fig_h.add_hline(y=1.0, line_color="#334155", line_dash="dot")
            fig_h.update_layout(
                plot_bgcolor="#07091A", paper_bgcolor="#07091A", font_color="#475569",
                height=240, margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="#0A1020",tickangle=-40),
                yaxis=dict(gridcolor="#0A1020"))
            st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:24px 20px;border-top:1px solid #0A1020;margin-top:24px;'>
  <p style='color:#1E2D47;font-size:10px;margin:0;font-family:"JetBrains Mono",monospace;letter-spacing:.04em;'>
    ⚠ For educational purposes only. Not financial advice. Always DYOR. Consult a SEBI-registered advisor.<br><br>
    © 2025 Momentum Frenzy &nbsp;·&nbsp;
    <a href='https://instagram.com/momentumfrenzy' style='color:#1E3A8A;text-decoration:none;'>@momentumfrenzy</a>
    &nbsp;·&nbsp; Data: Yahoo Finance &nbsp;·&nbsp; {datetime.now().strftime('%d %b %Y')}
  </p>
</div>""", unsafe_allow_html=True)
