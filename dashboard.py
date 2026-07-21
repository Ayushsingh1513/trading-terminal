import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Momentum Frenzy — Indian Stock Scanner Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "legal_accepted" not in st.session_state:
    st.session_state.legal_accepted = False

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM UI ANIMATIONS & SEBI SHIELD CSS (WITH GLASSMORPHISM)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Animated Breathing Background */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp {
    background: linear-gradient(-45deg, #050714, #0A0D1F, #02050D, #080B1A) !important;
    background-size: 400% 400% !important;
    animation: gradientBG 15s ease infinite !important;
}

/* Make Primary Streamlit Buttons POP and GLOW */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B7DFB 0%, #06B6D4 100%) !important;
    color: white !important;
    border: none !important;
    padding: 24px 32px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(59, 125, 251, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 40px rgba(6, 182, 212, 0.7) !important;
    transform: translateY(-4px) scale(1.02) !important;
}

/* Pulsing Glow for Buy Badges */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 5px rgba(0,214,143,0.1); }
    50% { box-shadow: 0 0 15px rgba(0,214,143,0.6); }
    100% { box-shadow: 0 0 5px rgba(0,214,143,0.1); }
}

/* Legal Modal Styling */
.legal-modal {
    background: rgba(13, 17, 32, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 76, 76, 0.4); 
    border-radius: 16px;
    padding: 30px; margin: 40px auto; max-width: 600px; text-align: center;
    box-shadow: 0 20px 50px rgba(255, 76, 76, 0.15);
}
.legal-title { color: #FF4C4C; font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-bottom: 15px; }
.legal-text { color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 25px; text-align: left; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING ENGINE (INSTANT LOAD)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
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
# ADVANCED GLASSMORPHISM LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* { font-family: 'Inter', -apple-system, sans-serif !important; }
.mono { font-family: 'JetBrains Mono', monospace !important; }
.block-container { padding:0; max-width:100%; position: relative; overflow: hidden; }
header[data-testid="stHeader"], #MainMenu, footer { display:none; }
.bg-orb { position: absolute; border-radius: 50%; filter: blur(90px); z-index: 0; opacity: 0.4; animation: float 12s infinite alternate ease-in-out; }
.orb-1 { width: 400px; height: 400px; background: #3B7DFB; top: -10%; left: 10%; }
.orb-2 { width: 500px; height: 500px; background: #06B6D4; bottom: -20%; right: 5%; animation-delay: -5s; }
@keyframes float { 0% { transform: translateY(0px) scale(1); } 100% { transform: translateY(50px) scale(1.1); } }
.lp-nav { display:flex; align-items:center; justify-content:space-between; padding:16px 40px; border-bottom:1px solid rgba(255,255,255,0.05); background:rgba(7, 9, 26, 0.4); backdrop-filter:blur(20px); position:sticky; top:0; z-index:99; }
.lp-logo { display:flex; align-items:center; gap:10px; font-family:'JetBrains Mono',monospace !important; font-size:15px; font-weight:700; color:#F1F5F9; letter-spacing:-.01em; }
.lp-logo-dot { width:8px; height:8px; border-radius:50%; background:#3B7DFB; box-shadow:0 0 10px #3B7DFB; }
.lp-nav-tag { font-size:11px; color:#94A3B8; border:1px solid rgba(255,255,255,0.1); border-radius:4px; padding:4px 10px; text-transform:uppercase; font-weight:600; background: rgba(255,255,255,0.03); }
.lp-hero { min-height:85vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:60px 24px 40px; position: relative; z-index: 10; }
.glass-panel { background: rgba(13, 17, 35, 0.3); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; padding: 60px 40px; box-shadow: 0 30px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1); max-width: 900px; margin: 0 auto; width: 100%; }
.lp-eyebrow { display:inline-flex; align-items:center; gap:6px; background:rgba(59, 125, 251, 0.1); border:1px solid rgba(59, 125, 251, 0.3); border-radius:4px; padding:6px 14px; font-family:'JetBrains Mono',monospace !important; font-size:11px; color:#3B7DFB; font-weight:600; letter-spacing:.1em; text-transform:uppercase; margin-bottom:28px; }
.lp-eyebrow-dot { width:6px; height:6px; border-radius:50%; background:#3B7DFB; animation:blink 1.4s infinite; box-shadow: 0 0 8px #3B7DFB; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:.3;} }
.lp-h1 { font-size:clamp(42px,6vw,72px); font-weight:800; line-height:1.1; letter-spacing:-.03em; color:#F1F5F9; margin:0 0 16px 0; }
.lp-h1 span { color:transparent; background:linear-gradient(135deg,#3B7DFB,#06B6D4); -webkit-background-clip:text; background-clip:text; }
.lp-sub { font-size:clamp(15px,1.8vw,19px); color:#94A3B8; max-width:540px; line-height:1.75; margin:0 auto 40px; }
.lp-stats { display:flex; flex-wrap: wrap; border:1px solid rgba(255,255,255,0.05); border-radius:12px; background:rgba(0,0,0,0.2); overflow:hidden; margin:40px auto 0; }
.lp-stat { flex:1; min-width: 120px; padding:20px 10px; text-align:center; border-right:1px solid rgba(255,255,255,0.05); }
.lp-stat:last-child { border-right:none; }
.lp-stat-n { font-family:'JetBrains Mono',monospace !important; font-size:26px; font-weight:700; color:#06B6D4; text-shadow: 0 0 10px rgba(6,182,212,0.3); }
.lp-stat-l { font-size:10px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; margin-top:4px; }
</style>
<div class="bg-orb orb-1"></div>
<div class="bg-orb orb-2"></div>
<div class="lp-nav">
<div class="lp-logo"><div class="lp-logo-dot"></div>MomentumFrenzy</div>
<div class="lp-nav-tag">Free · NSE Terminal · Pro</div>
</div>
<div class="lp-hero">
<div class="glass-panel">
<div class="lp-eyebrow"><div class="lp-eyebrow-dot"></div>Indian Markets · High-Probability Swing Scanner</div>
<h1 class="lp-h1">Find the trade.<br><span>Before the move.</span></h1>
<p class="lp-sub">Institutional momentum scanner for NSE. Entry, Stop Loss, Targets, and Sector Rotation auto-calculated in real time.</p>
<div style="height: 30px;"></div>
<div class="lp-stats">
<div class="lp-stat"><div class="lp-stat-n">500+</div><div class="lp-stat-l">Stocks Scanned</div></div>
<div class="lp-stat"><div class="lp-stat-n">18</div><div class="lp-stat-l">Sectors Tracked</div></div>
<div class="lp-stat"><div class="lp-stat-n">15 min</div><div class="lp-stat-l">Live Refresh</div></div>
<div class="lp-stat"><div class="lp-stat-n">Free</div><div class="lp-stat-l">Always</div></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div style='margin-top: -240px; position: relative; z-index: 50;'>", unsafe_allow_html=True)
        if st.button("⚡ Launch Terminal — Free", use_container_width=True, type="primary"):
            st.session_state.page = "terminal"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SEBI SHIELD POPUP
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "terminal" and not st.session_state.legal_accepted:
    st.markdown("""
    <div class="legal-modal">
        <div class="legal-title">⚠️ MANDATORY RISK DISCLOSURE</div>
        <div class="legal-text">
            <b>1. Not SEBI Registered:</b> The creator of Momentum Frenzy is NOT a SEBI-registered entity, financial advisor, or research analyst.<br><br>
            <b>2. Educational Use Only:</b> All data, momentum scores, and stock setups provided here are purely algorithmic and for educational & paper-trading purposes only.<br><br>
            <b>3. 100% Your Risk:</b> Trading in equities and F&O involves extreme financial risk. You alone are responsible for your capital. We hold zero liability for any financial losses incurred based on this data.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I Understand & Agree to these Terms", type="primary", use_container_width=True):
            st.session_state.legal_accepted = True
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL UI INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
if market_data is None:
    st.markdown("""
    <div style='text-align:center; padding:100px; color:#3B7DFB; font-family:"JetBrains Mono",monospace;'>
        <h2>⚙️ Initializing Data Engine...</h2>
        <p style='color:#64748B;'>Please wait while the backend syncs live market data.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("""
<style>
* { font-family: 'Inter', -apple-system, sans-serif !important; }
.mono, .pick-stock, .pick-buy-badge, .pick-cell-val, .pick-cell-lbl, .sec-hdr-text, 
.ticker-label, .ticker-val, .mood-value, .pick-rr, .pick-meta span, .sq-title, .sq-chip, .sec-stat-val {
    font-family: 'JetBrains Mono', monospace !important;
}
html, body { color:#CBD5E1; }
.block-container { padding: 0 0 4rem 0; max-width: 100%; }
header[data-testid="stHeader"], #MainMenu, footer { display: none; }
@keyframes fadeSlideUp { 0% { opacity: 0; transform: translateY(16px); } 100% { opacity: 1; transform: translateY(0); } }
.animated-entry { animation: fadeSlideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.ticker-bar { background:rgba(7, 9, 26, 0.5); backdrop-filter: blur(16px); border-bottom:1px solid rgba(255, 255, 255, 0.05); padding:0 20px; display:flex; align-items:center; position:sticky; top:0; z-index:999; height:42px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
.ticker-bar::-webkit-scrollbar { display: none; }
.ticker-item { display:flex; align-items:center; gap:8px; padding:0 18px; border-right:1px solid rgba(255, 255, 255, 0.05); height:100%; }
.ticker-item:last-child { border-right:none; }
.ticker-label { font-size:10px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; font-weight:600; }
.ticker-val { font-size:13px; font-weight:700; color:#F1F5F9; }
.tv-up { color:#00D68F !important; }
.tv-down { color:#FF4C4C !important; }
.tv-blue { color:#3B7DFB !important; }
.ticker-spacer { flex:1; }
.ticker-time { font-size:10px; color:#475569; padding-left:16px; }
.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid rgba(255,255,255, 0.05); padding:0 20px; gap:8px; }
.stTabs [data-baseweb="tab"] { background:transparent; color:#64748B; font-size:13px; font-weight:600; padding:12px 20px; border-bottom:2px solid transparent; }
.stTabs [aria-selected="true"] { color:#06B6D4 !important; border-bottom-color:#06B6D4 !important; background:transparent !important; text-shadow: 0 0 10px rgba(6,182,212,0.3); }
.stTabs [data-baseweb="tab-panel"] { padding: 16px 20px; }
.sec-hdr { display:flex; align-items:center; gap:10px; padding:18px 0 12px 0; border-bottom:1px solid rgba(255,255,255, 0.05); margin-bottom:16px; }
.sec-hdr-line { width:4px; height:18px; background:linear-gradient(180deg, #3B7DFB, #06B6D4); border-radius:2px; box-shadow: 0 0 8px rgba(6,182,212,0.5); }
.sec-hdr-text { font-size:12px; font-weight:700; color:#E2E8F0; text-transform:uppercase; letter-spacing:.12em; }
.mood-banner { display:flex; align-items:stretch; background:rgba(13, 17, 32, 0.4); backdrop-filter: blur(12px); border:1px solid rgba(255,255,255, 0.05); border-radius:12px; overflow:hidden; margin:12px 0 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.mood-side { width:5px; flex-shrink:0; }
.mood-content { flex:1; padding:16px 20px; display:flex; align-items:center; gap:24px; flex-wrap:wrap; }
.mood-label-sm { font-size:10px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.mood-value { font-size:22px; font-weight:800; line-height:1; }
.mood-score-row { display:flex; align-items:center; gap:8px; margin-top:6px; }
.mood-score-bar-bg { flex:1; height:4px; background:rgba(0,0,0,0.4); border-radius:2px; }
.mood-score-bar-fill { height:4px; border-radius:2px; box-shadow: 0 0 10px currentColor; }
.mood-score-num { font-size:11px; color:#94A3B8; }
.mood-meta { font-size:11px; color:#64748B; line-height:1.8; }
.mood-tip { font-size:12px; color:#94A3B8; margin-top:6px; padding-top:6px; border-top:1px solid rgba(255,255,255,0.05); }
.pick-card { background:rgba(13, 17, 35, 0.3); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border:1px solid rgba(255, 255, 255, 0.08); border-radius:16px; overflow:hidden; margin-bottom:16px; transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.pick-card:hover { border-color:rgba(6, 182, 212, 0.5); transform: translateY(-5px); box-shadow: 0 15px 35px rgba(6, 182, 212, 0.15); }
.pick-card-head { display:flex; align-items:center; justify-content:space-between; padding:16px; border-bottom:1px solid rgba(255, 255, 255, 0.05); background:rgba(0,0,0,0.2); }
.pick-stock { font-size:18px; font-weight:800; color:#FFFFFF; margin:0; line-height:1; }
.pick-setup { font-size:10px; color:#94A3B8; margin-top:3px; }
.pick-buy-badge { animation: pulseGlow 2s infinite; background:rgba(0, 214, 143, 0.15); color:#00D68F; font-size:10px; font-weight:800; padding:4px 10px; border-radius:6px; border:1px solid rgba(0, 214, 143, 0.4); letter-spacing:.08em; }
.pick-grid { display:grid; grid-template-columns:1fr 1fr; gap:1px; background:rgba(255, 255, 255, 0.05); }
.pick-cell { background:rgba(10, 14, 25, 0.4); padding:12px 16px; }
.pick-cell-lbl { font-size:9px; color:#64748B; text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px; font-weight:600; }
.pick-cell-val { font-size:14px; font-weight:700; }
.pv-entry { color:#E2E8F0; } .pv-sl { color:#FF4C4C; } .pv-t1 { color:#00D68F; } .pv-t2 { color:#06B6D4; }
.pick-foot { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-top:1px solid rgba(255, 255, 255, 0.05); background:rgba(0,0,0,0.2); }
.pick-rr { font-size:11px; font-weight:700; }
.pick-meta { display:flex; gap:10px; font-size:10px; color:#64748B; }
.stDataFrame { border:1px solid rgba(255, 255, 255, 0.05); border-radius:12px; overflow:hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.sq-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.sq-card { border-radius:12px; padding:16px; min-height:110px; background:rgba(13, 17, 35, 0.3); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); transition: transform 0.2s; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
.sq-card:hover { transform: translateY(-3px); }
.sq-leading { border-top: 2px solid #00D68F; }
.sq-improving { border-top: 2px solid #06B6D4; }
.sq-weakening { border-top: 2px solid #FFB020; }
.sq-lagging { border-top: 2px solid #FF4C4C; }
.sq-title { font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.12em; margin-bottom:10px; }
.sq-leading .sq-title { color:#00D68F; }
.sq-improving .sq-title { color:#06B6D4; }
.sq-weakening .sq-title { color:#FFB020; }
.sq-lagging .sq-title { color:#FF4C4C; }
.sq-chip { display:inline-flex; align-items:center; gap:4px; font-size:11px; padding:4px 9px; border-radius:6px; background:rgba(255,255,255,0.05); color:#CBD5E1; margin:3px; border:1px solid rgba(255,255,255,0.1); }
.sec-stat-box { background:rgba(13, 17, 35, 0.3); backdrop-filter: blur(12px); border:1px solid rgba(255, 255, 255, 0.05); border-radius:12px; padding:16px; text-align:center; box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
.sec-stat-lbl { font-size:9px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; }
.sec-stat-val { font-size:18px; font-weight:700; color:#F1F5F9; }
.ig-cta { background:rgba(13, 17, 35, 0.3); backdrop-filter: blur(12px); border:1px solid rgba(255, 255, 255, 0.08); border-radius:16px; padding:24px; text-align:center; margin:20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.ig-cta-title { font-size:15px; font-weight:700; color:#E2E8F0; margin-bottom:4px; }
.ig-cta-sub { font-size:12px; color:#94A3B8; margin-bottom:14px; }
.ig-btn { display:inline-block; background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); color:#fff !important; padding:10px 28px; border-radius:8px; text-decoration:none; font-size:13px; font-weight:700; box-shadow: 0 4px 15px rgba(253, 29, 29, 0.3); transition: transform 0.2s; }
.ig-btn:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

def tc(v):  return "tv-up" if v >= 0 else "tv-down"
def ar(v):  return "▲" if v >= 0 else "▼"

def style_sig(val):
    if val == "BUY":   return "background:rgba(0, 214, 143, 0.1);color:#00D68F;font-weight:700;font-family:JetBrains Mono,monospace"
    if val == "WATCH": return "background:rgba(255, 176, 32, 0.1);color:#FFB020;font-weight:700;font-family:JetBrains Mono,monospace"
    if val == "AVOID": return "background:rgba(255, 76, 76, 0.1);color:#FF4C4C;font-weight:700;font-family:JetBrains Mono,monospace"
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

hc1, hc2 = st.columns([1, 10])
with hc1:
    st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png", width=48)
with hc2:
    st.markdown("""
    <div style='padding:4px 0;'>
      <div style='font-family:"JetBrains Mono",monospace !important;font-size:16px;font-weight:700;color:#F1F5F9;letter-spacing:-.01em;'>
        ⚡ MOMENTUM FRENZY
      </div>
      <div style='font-size:10px;color:#06B6D4;letter-spacing:.06em;margin-top:2px;'>
        INDIAN MARKETS &nbsp;·&nbsp; SWING TRADING TERMINAL &nbsp;·&nbsp; PRO (500+ STOCKS)
      </div>
    </div>""", unsafe_allow_html=True)

top_picks = scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records')

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
          <div class="mood-value" style="color:{mood_c}; text-shadow: 0 0 10px {mood_c}40;">{mood}</div>
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
    else:
        st.info("No strong 'BUY' setups currently detected. Market conditions may be choppy.")

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
    m5.markdown(f"<div class='sec-stat-box'><div class='sec-stat-lbl'>Top Vol Surge</div><div class='sec-stat-val' style='color:#3B7DFB;'>{top_vol['Sector']}</div></div>", unsafe_allow_html=True)

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
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#64748B",
            height=290, margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"), xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)", tickangle=-45)
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
<div style='text-align:center;padding:24px 20px;border-top:1px solid rgba(255,255,255, 0.05);margin-top:24px;'>
  <p style='color:#64748B;font-size:10px;margin:0;font-family:"JetBrains Mono",monospace !important;letter-spacing:.04em;'>
    Educational purposes only. Not financial advice. Always DYOR. Consult a SEBI-registered advisor.<br><br>
    © 2026 Momentum Frenzy &nbsp;·&nbsp;
    <a href='https://instagram.com/momentumfrenzy' style='color:#06B6D4;text-decoration:none;'>@momentumfrenzy</a>
  </p>
</div>""", unsafe_allow_html=True)
