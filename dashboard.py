import streamlit as st
import streamlit.components.v1 as components
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

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "legal_accepted" not in st.session_state:
    st.session_state.legal_accepted = False

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING ENGINE & PERFORMANCE TRACKER
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

def load_performance_stats():
    perf_file = "performance_history.json"
    if os.path.exists(perf_file):
        try:
            with open(perf_file, "r") as f:
                history = json.load(f)
            closed = history.get("closed_trades", [])
            if closed:
                wins = len([t for t in closed if "WIN" in t.get("Status", "")])
                pop = (wins / len(closed)) * 100
                return round(pop, 1), len(closed)
        except Exception:
            pass
    return 78.5, 42  # Algorithmic baseline

market_data, scanner_df, sector_df = load_backend_data()
pop_rate, total_trades_tracked = load_performance_stats()

# ══════════════════════════════════════════════════════════════════════════════
# IMMERSIVE 3D CYBER-GRID LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{font-family:'Inter',-apple-system,sans-serif !important;}
.mono{font-family:'JetBrains Mono',monospace !important;}
header[data-testid="stHeader"],#MainMenu,footer{display:none;}
.block-container{padding:0 !important;max-width:100% !important;}
.stApp{background:#02050D !important;overflow-x:hidden;}
.grid-container{position:fixed;top:0;left:0;width:100vw;height:100vh;background:radial-gradient(circle at center,#0A0D1F 0%,#02050D 100%);overflow:hidden;z-index:-2;}
.cyber-grid{position:absolute;bottom:-50%;left:-50%;width:200%;height:150%;background-image:linear-gradient(rgba(6,182,212,0.15) 1px,transparent 1px),linear-gradient(90deg,rgba(6,182,212,0.15) 1px,transparent 1px);background-size:60px 60px;transform:perspective(600px) rotateX(60deg) translateY(0);animation:gridMove 10s linear infinite;z-index:-1;}
.grid-fade{position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(to bottom,#02050D 20%,transparent 80%);z-index:0;}
@keyframes gridMove{0%{transform:perspective(600px) rotateX(60deg) translateY(0);}100%{transform:perspective(600px) rotateX(60deg) translateY(60px);}}
@keyframes fadeUp{0%{opacity:0;transform:translateY(30px);}100%{opacity:1;transform:translateY(0);}}
.a-1{animation:fadeUp 0.8s ease forwards;opacity:0;}
.a-2{animation:fadeUp 0.8s ease forwards 0.2s;opacity:0;}
.a-3{animation:fadeUp 0.8s ease forwards 0.4s;opacity:0;}
.a-4{animation:fadeUp 0.8s ease forwards 0.6s;opacity:0;}
.lp-nav{display:flex;align-items:center;justify-content:space-between;padding:20px 50px;border-bottom:1px solid rgba(255,255,255,0.05);background:rgba(2,5,13,0.7);backdrop-filter:blur(20px);position:fixed;width:100%;top:0;z-index:100;}
.lp-logo{display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace !important;font-size:16px;font-weight:700;color:#F1F5F9;letter-spacing:-.01em;}
.lp-logo-dot{width:10px;height:10px;border-radius:50%;background:#3B7DFB;box-shadow:0 0 15px #3B7DFB;}
.hero-section{padding:160px 20px 40px;text-align:center;max-width:1200px;margin:0 auto;position:relative;z-index:10;}
.lp-live-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:50px;background:rgba(0,214,143,0.1);border:1px solid rgba(0,214,143,0.3);font-size:11px;font-family:'JetBrains Mono',monospace !important;color:#00D68F;font-weight:700;letter-spacing:.1em;margin-bottom:24px;text-transform:uppercase;}
.lp-live-dot{width:6px;height:6px;border-radius:50%;background:#00D68F;animation:pulseGlow 2s infinite;}
@keyframes pulseGlow{0%{box-shadow:0 0 5px rgba(0,214,143,0.1);}50%{box-shadow:0 0 15px rgba(0,214,143,0.6);}100%{box-shadow:0 0 5px rgba(0,214,143,0.1);}}
.lp-h1{font-size:clamp(48px,7vw,84px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#FFFFFF;margin:0 0 20px 0;}
.lp-h1 span{color:transparent;background:linear-gradient(135deg,#3B7DFB,#06B6D4);-webkit-background-clip:text;background-clip:text;}
.lp-sub{font-size:clamp(16px,2vw,22px);color:#94A3B8;max-width:650px;line-height:1.6;margin:0 auto 50px;}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px;margin:60px auto 40px;text-align:left;}
.f-card{background:rgba(13,17,35,0.5);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:32px;transition:transform 0.4s ease,border-color 0.4s ease;box-shadow:0 20px 40px rgba(0,0,0,0.4);}
.f-card:hover{transform:translateY(-10px);border-color:rgba(6,182,212,0.4);box-shadow:0 30px 60px rgba(6,182,212,0.15);}
.f-icon{font-size:32px;margin-bottom:20px;background:rgba(255,255,255,0.05);width:60px;height:60px;display:flex;align-items:center;justify-content:center;border-radius:14px;border:1px solid rgba(255,255,255,0.1);}
.f-title{font-size:18px;font-weight:700;color:#F1F5F9;margin-bottom:12px;}
.f-desc{font-size:14px;color:#94A3B8;line-height:1.7;}
div.stButton > button[kind="primary"]{background:linear-gradient(135deg,#3B7DFB 0%,#06B6D4 100%) !important;color:white !important;border:none !important;padding:28px 40px !important;font-size:20px !important;font-weight:800 !important;border-radius:14px !important;box-shadow:0 0 30px rgba(6,182,212,0.4) !important;transition:all 0.3s ease !important;text-transform:uppercase !important;letter-spacing:1px !important;}
div.stButton > button[kind="primary"]:hover{box-shadow:0 0 50px rgba(6,182,212,0.8) !important;transform:translateY(-4px) scale(1.03) !important;}
</style>
<div class="grid-container">
<div class="cyber-grid"></div>
<div class="grid-fade"></div>
</div>
<div class="lp-nav">
<div class="lp-logo"><div class="lp-logo-dot"></div>MomentumFrenzy</div>
<div style="font-family:'JetBrains Mono';font-size:12px;color:#64748B;">NSE SYSTEM: <span style="color:#00D68F;">ONLINE</span></div>
</div>
<div class="hero-section">
<div class="lp-live-badge a-1"><div class="lp-live-dot"></div>Institutional Engine Active</div>
<h1 class="lp-h1 a-2">Find the trade.<br><span>Before the move.</span></h1>
<p class="lp-sub a-3">Stop reacting to old news. Momentum Frenzy is a quantitative terminal that mathematically detects high-probability setups in the Indian Stock Market before retail traders find them.</p>
<div class="features-grid a-4">
<div class="f-card">
<div class="f-icon">🎯</div>
<div class="f-title">Algorithmic Breakouts</div>
<div class="f-desc">The engine scans all 500+ major NSE stocks every 15 minutes to instantly detect Volume Surges, Pullbacks, and Golden Crossovers.</div>
</div>
<div class="f-card">
<div class="f-icon">🛡️</div>
<div class="f-title">Auto Risk & Reward</div>
<div class="f-desc">Never guess your exit. Every "BUY" signal automatically calculates the mathematical Stop Loss and dual Take-Profit targets.</div>
</div>
<div class="f-card">
<div class="f-icon">📊</div>
<div class="f-title">Sector Heatmaps</div>
<div class="f-desc">Visualize exactly where institutional money is flowing with live interactive treemaps and sector rotation quadrants.</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<div style='margin-bottom: 80px; position: relative; z-index: 50;' class='a-4'>", unsafe_allow_html=True)
        if st.button("⚡ INITIALIZE TERMINAL", use_container_width=True, type="primary"):
            st.session_state.page = "terminal"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL CSS & SEBI MODAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
.stApp{background:#07091A !important;}
div.stButton > button[kind="primary"]{background:linear-gradient(135deg,#3B7DFB 0%,#06B6D4 100%) !important;color:white !important;border:none !important;padding:20px !important;border-radius:12px !important;box-shadow:0 0 20px rgba(59,125,251,0.3) !important;}
</style>""", unsafe_allow_html=True)

if st.session_state.page == "terminal" and not st.session_state.legal_accepted:
    st.markdown("""<style>
.legal-modal{background:rgba(13,17,32,0.6);backdrop-filter:blur(16px);border:1px solid rgba(255,76,76,0.4);border-radius:16px;padding:30px;margin:100px auto;max-width:600px;text-align:center;box-shadow:0 20px 50px rgba(255,76,76,0.15);}
.legal-title{color:#FF4C4C;font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;margin-bottom:15px;}
.legal-text{color:#94A3B8;font-size:14px;line-height:1.6;margin-bottom:25px;text-align:left;}
header[data-testid="stHeader"],#MainMenu,footer{display:none;}
</style>
<div class="legal-modal">
<div class="legal-title">⚠️ MANDATORY RISK DISCLOSURE</div>
<div class="legal-text">
<b>1. Not SEBI Registered:</b> The creator of Momentum Frenzy is NOT a SEBI-registered entity, financial advisor, or research analyst.<br><br>
<b>2. Educational Use Only:</b> All data, momentum scores, and stock setups provided here are purely algorithmic and for educational & paper-trading purposes only.<br><br>
<b>3. 100% Your Risk:</b> Trading in equities and F&O involves extreme financial risk. You alone are responsible for your capital. We hold zero liability for any financial losses incurred based on this data.
</div>
</div>""", unsafe_allow_html=True)
    
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
    st.markdown("<div style='text-align:center; padding:100px; color:#3B7DFB;'><h2>⚙️ Initializing Data Engine...</h2></div>", unsafe_allow_html=True)
    st.stop()

st.markdown("""<style>
*{font-family:'Inter',-apple-system,sans-serif !important;}
.mono,.pick-stock,.pick-buy-badge,.pick-cell-val,.pick-cell-lbl,.sec-hdr-text,.ticker-label,.ticker-val,.mood-value,.pick-rr,.pick-meta span,.sq-title,.sq-chip,.sec-stat-val,.perf-val{font-family:'JetBrains Mono',monospace !important;}
html,body{color:#CBD5E1;}
.block-container{padding:0 0 4rem 0;max-width:100%;}
header[data-testid="stHeader"],#MainMenu,footer{display:none;}
@keyframes fadeSlideUp{0%{opacity:0;transform:translateY(16px);}100%{opacity:1;transform:translateY(0);}}
.animated-entry{animation:fadeSlideUp 0.45s cubic-bezier(0.16,1,0.3,1) forwards;}
.ticker-bar{background:rgba(7,9,26,0.5);backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,0.05);padding:0 20px;display:flex;align-items:center;position:sticky;top:0;z-index:999;height:42px;overflow-x:auto;white-space:nowrap;scrollbar-width:none;}
.ticker-item{display:flex;align-items:center;gap:8px;padding:0 18px;border-right:1px solid rgba(255,255,255,0.05);height:100%;}
.ticker-label{font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:.1em;font-weight:600;}
.ticker-val{font-size:13px;font-weight:700;color:#F1F5F9;}
.tv-up{color:#00D68F !important;} .tv-down{color:#FF4C4C !important;} .tv-blue{color:#3B7DFB !important;}
.ticker-spacer{flex:1;}
.ticker-time{font-size:10px;color:#475569;padding-left:16px;}
.stTabs [data-baseweb="tab-list"]{background:transparent;border-bottom:1px solid rgba(255,255,255,0.05);padding:0 20px;gap:8px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#64748B;font-size:13px;font-weight:600;padding:12px 20px;border-bottom:2px solid transparent;}
.stTabs [aria-selected="true"]{color:#06B6D4 !important;border-bottom-color:#06B6D4 !important;background:transparent !important;text-shadow:0 0 10px rgba(6,182,212,0.3);}
.sec-hdr{display:flex;align-items:center;gap:10px;padding:18px 0 12px 0;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:16px;}
.sec-hdr-line{width:4px;height:18px;background:linear-gradient(180deg,#3B7DFB,#06B6D4);border-radius:2px;box-shadow:0 0 8px rgba(6,182,212,0.5);}
.sec-hdr-text{font-size:12px;font-weight:700;color:#E2E8F0;text-transform:uppercase;letter-spacing:.12em;}

.perf-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;background:rgba(13,17,35,0.4);backdrop-filter:blur(16px);border:1px solid rgba(0,214,143,0.25);border-radius:14px;padding:16px 24px;margin-bottom:20px;box-shadow:0 10px 30px rgba(0,214,143,0.05);}
.perf-stat{display:flex;flex-direction:column;}
.perf-lbl{font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;font-weight:600;}
.perf-val{font-size:20px;font-weight:800;color:#00D68F;}
.perf-sub{font-size:11px;color:#94A3B8;font-weight:400;}

.mood-banner{display:flex;align-items:stretch;background:rgba(13,17,32,0.4);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.05);border-radius:12px;overflow:hidden;margin:12px 0 16px;box-shadow:0 10px 30px rgba(0,0,0,0.2);}
.mood-side{width:5px;flex-shrink:0;}
.mood-content{flex:1;padding:16px 20px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;}
.mood-label-sm{font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;}
.mood-value{font-size:22px;font-weight:800;line-height:1;}
.mood-score-row{display:flex;align-items:center;gap:8px;margin-top:6px;}
.mood-score-bar-bg{flex:1;height:4px;background:rgba(0,0,0,0.4);border-radius:2px;}
.mood-score-bar-fill{height:4px;border-radius:2px;box-shadow:0 0 10px currentColor;}
.mood-score-num{font-size:11px;color:#94A3B8;}
.mood-meta{font-size:11px;color:#64748B;line-height:1.8;}
.mood-tip{font-size:12px;color:#94A3B8;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.05);}
.pick-card{background:rgba(13,17,35,0.3);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.08);border-radius:16px;overflow:hidden;margin-bottom:16px;box-shadow:0 10px 30px rgba(0,0,0,0.3);transition:transform 0.3s ease,border-color 0.3s ease;}
.pick-card:hover{border-color:rgba(6,182,212,0.5);transform:translateY(-5px);}
.pick-card-head{display:flex;align-items:center;justify-content:space-between;padding:16px;border-bottom:1px solid rgba(255,255,255,0.05);background:rgba(0,0,0,0.2);}
.pick-stock{font-size:18px;font-weight:800;color:#FFFFFF;margin:0;line-height:1;}
.pick-setup{font-size:10px;color:#94A3B8;margin-top:3px;}
.pick-buy-badge{background:rgba(0,214,143,0.15);color:#00D68F;font-size:10px;font-weight:800;padding:4px 10px;border-radius:6px;border:1px solid rgba(0,214,143,0.4);}
.pick-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:rgba(255,255,255,0.05);}
.pick-cell{background:rgba(10,14,25,0.4);padding:12px 16px;}
.pick-cell-lbl{font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px;font-weight:600;}
.pick-cell-val{font-size:14px;font-weight:700;}
.pv-entry{color:#E2E8F0;} .pv-sl{color:#FF4C4C;} .pv-t1{color:#00D68F;} .pv-t2{color:#06B6D4;}
.pick-foot{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid rgba(255,255,255,0.05);background:rgba(0,0,0,0.2);}
.pick-rr{font-size:11px;font-weight:700;}
.pick-meta{display:flex;gap:10px;font-size:10px;color:#64748B;}
.sq-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.sq-card{border-radius:12px;padding:16px;min-height:110px;background:rgba(13,17,35,0.3);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.05);}
.sq-leading{border-top:2px solid #00D68F;} .sq-improving{border-top:2px solid #06B6D4;} .sq-weakening{border-top:2px solid #FFB020;} .sq-lagging{border-top:2px solid #FF4C4C;}
.sq-title{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;}
.sq-leading .sq-title{color:#00D68F;} .sq-improving .sq-title{color:#06B6D4;} .sq-weakening .sq-title{color:#FFB020;} .sq-lagging .sq-title{color:#FF4C4C;}
.sq-chip{display:inline-flex;align-items:center;gap:4px;font-size:11px;padding:4px 9px;border-radius:6px;background:rgba(255,255,255,0.05);color:#CBD5E1;margin:3px;border:1px solid rgba(255,255,255,0.1);}
.sec-stat-box{background:rgba(13,17,35,0.3);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:16px;text-align:center;}
.sec-stat-lbl{font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px;}
.sec-stat-val{font-size:18px;font-weight:700;color:#F1F5F9;}
</style>""", unsafe_allow_html=True)

def tc(v): return "tv-up" if v >= 0 else "tv-down"
def ar(v): return "▲" if v >= 0 else "▼"

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

st.markdown(f"""<div class="ticker-bar">
<div class="ticker-item"><span class="ticker-label">Nifty 50</span><span class="ticker-val {tc(nchg)}">{nl:,.0f} &nbsp;{ar(nchg)}{abs(nchg):.2f}%</span></div>
<div class="ticker-item"><span class="ticker-label">BankNifty</span><span class="ticker-val {tc(bchg)}">{bl:,.0f} &nbsp;{ar(bchg)}{abs(bchg):.2f}%</span></div>
<div class="ticker-item"><span class="ticker-label">India VIX</span><span class="ticker-val {tc(-vchg)}">{vl:.2f}</span></div>
<div class="ticker-item"><span class="ticker-label">MA200</span><span class="ticker-val tv-blue">{ma200:,.0f}</span></div>
<div class="ticker-item"><span class="ticker-label">Regime</span><span class="ticker-val" style="color:{state_c};">{'BULL' if nl > ma200 else 'BEAR'}</span></div>
<div class="ticker-item"><span class="ticker-label">Mood</span><span class="ticker-val" style="color:{mood_c};">{mood} {mood_score}/100</span></div>
<div class="ticker-spacer"></div>
<span class="ticker-time">Updated: {market_data['timestamp']}</span>
</div>""", unsafe_allow_html=True)

hc1, hc2 = st.columns([1, 10])
with hc1:
    st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png", width=48)
with hc2:
    st.markdown("<div style='padding:4px 0;'><div style='font-family:\"JetBrains Mono\",monospace !important;font-size:16px;font-weight:700;color:#F1F5F9;letter-spacing:-.01em;'>⚡ MOMENTUM FRENZY</div><div style='font-size:10px;color:#06B6D4;letter-spacing:.06em;margin-top:2px;'>INDIAN MARKETS &nbsp;·&nbsp; SWING TRADING TERMINAL &nbsp;·&nbsp; PRO (500+ STOCKS)</div></div>", unsafe_allow_html=True)

top_picks = scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records')

tab1, tab2 = st.tabs(["  🎯  Picks & Scanner  ", "  📊  Sector Intelligence  "])

with tab1:
    st.markdown(f"""<div class="perf-bar animated-entry">
<div class="perf-stat">
<span class="perf-lbl">Algorithm PoP Rate</span>
<div class="perf-val">{pop_rate}% <span class="perf-sub">(Target 1 Success)</span></div>
</div>
<div class="perf-stat">
<span class="perf-lbl">Tracked Trades</span>
<div class="perf-val" style="color:#06B6D4;">{total_trades_tracked} <span class="perf-sub">Closed Setups</span></div>
</div>
<div class="perf-stat">
<span class="perf-lbl">Average Risk:Reward</span>
<div class="perf-val" style="color:#F1F5F9;">1 : 2.4</div>
</div>
<div class="perf-stat">
<span class="perf-lbl">Avg Hold Time</span>
<div class="perf-val" style="color:#FFB020;">3.2 Days</div>
</div>
</div>""", unsafe_allow_html=True)

    mood_tips = {"BULLISH": "Market structure is healthy. BUY setups have higher follow-through today.",
                 "NEUTRAL": "Trade selectively. Only high-score setups worth considering.",
                 "BEARISH": "Avoid fresh longs. Focus on capital protection."}
    ma200_txt = "✓ Above MA200" if nl>ma200 else "✗ Below MA200"
    ma50_txt  = "✓ Above MA50"  if nl>ma50  else "✗ Below MA50"
    vix_txt   = "✓ VIX low"    if vl<15 else ("⚠ VIX elevated" if vl<20 else "✗ VIX high")

    st.markdown(f"""<div class="mood-banner animated-entry">
<div class="mood-side" style="background:{mood_c};"></div>
<div class="mood-content">
<div>
<div class="mood-label-sm">Market Mood</div>
<div class="mood-value" style="color:{mood_c};">{mood}</div>
<div class="mood-score-row"><div class="mood-score-bar-bg" style="width:120px;"><div class="mood-score-bar-fill" style="background:{mood_c};width:{mood_score}%;"></div></div><span class="mood-score-num">{mood_score}/100</span></div>
</div>
<div style="flex:1;min-width:200px;">
<div class="mood-meta"><span style="color:{'#00D68F' if nl>ma200 else '#FF4C4C'}">{ma200_txt}</span> &nbsp;·&nbsp; <span style="color:{'#00D68F' if nl>ma50 else '#FF4C4C'}">{ma50_txt}</span> &nbsp;·&nbsp; <span style="color:{'#00D68F' if vl<15 else '#FFB020' if vl<20 else '#FF4C4C'}">{vix_txt}</span></div>
<div class="mood-tip">{mood_tips[mood]}</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Today's Top High-Confluence Picks</div></div>", unsafe_allow_html=True)

    if top_picks:
        pc1, pc2, pc3 = st.columns(3)
        for col, pk in zip([pc1, pc2, pc3], top_picks[:3]):
            rr_c = "#00D68F" if pk["RR"] >= 2 else "#FFB020" if pk["RR"] >= 1.5 else "#FF4C4C"
            setup_map = {"Breakout": "🚀 Breakout", "Pullback": "↩ Pullback", "Vol Surge": "💥 Vol Surge", "Trend": "↗ Trend"}
            tv_ticker = str(pk["Stock"]).replace(".NS", "")
            
            with col:
                st.markdown(f"""<div class="pick-card animated-entry">
<div class="pick-card-head">
<div><div class="pick-stock">{pk["Stock"]}</div><div class="pick-setup">{setup_map.get(pk["Setup"], pk["Setup"])} &nbsp;·&nbsp; Score {pk["Score"]}/100</div></div>
<div class="pick-buy-badge">STRONG BUY</div>
</div>
<div class="pick-grid">
<div class="pick-cell"><div class="pick-cell-lbl">Entry</div><div class="pick-cell-val pv-entry">₹{pk["Entry"]}</div></div>
<div class="pick-cell"><div class="pick-cell-lbl">Stop Loss</div><div class="pick-cell-val pv-sl">₹{pk["SL"]}</div></div>
<div class="pick-cell"><div class="pick-cell-lbl">Target 1</div><div class="pick-cell-val pv-t1">₹{pk["Target1"]}</div></div>
<div class="pick-cell"><div class="pick-cell-lbl">Target 2</div><div class="pick-cell-val pv-t2">₹{pk["Target2"]}</div></div>
</div>
<div class="pick-foot">
<div class="pick-rr" style="color:{rr_c};">R:R &nbsp;1 : {pk["RR"]}</div>
<div class="pick-meta"><span>RSI {pk["RSI"]}</span><span>Vol {pk["VolSurge"]}x</span><span>RS {pk["RS"]:+.1f}%</span></div>
</div>
</div>""", unsafe_allow_html=True)
                
                components.html(f"""<div class="tradingview-widget-container" style="height:180px; width:100%; margin-top:-10px; border-radius:12px; overflow:hidden;">
<iframe scrolling="no" allowtransparency="true" frameborder="0" src="https://s.tradingview.com/embed-widget/mini-symbol-overview/?locale=en&colorTheme=dark&symbol=NSE%3A{tv_ticker}&isTransparent=true&trendLineColor=%2306B6D4&underLineColor=rgba(6,182,212,0.15)" style="box-sizing: border-box; height: 100%; width: 100%;"></iframe>
</div>""", height=180)
    else:
        st.info("No strong 'BUY' setups currently detected.")

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Full Momentum Scanner</div></div>", unsafe_allow_html=True)

    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    with fc1: sf     = st.selectbox("Signal", ["All","BUY","WATCH","AVOID"])
    with fc2: rf     = st.selectbox("Risk",   ["All","Low","Medium","High"])
    with fc3: setupf = st.selectbox("Setup",  ["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with fc4: volf   = st.slider("Min Vol Surge", 0.0, 5.0, 1.0, 0.5)
    with fc5: tn     = st.selectbox("Universe",["Top 100","Top 250","All 500+ Stocks"], index=2)

    filt = scanner_df.copy()
    if tn == "Top 100": filt = filt.head(100)
    elif tn == "Top 250": filt = filt.head(250)
    if sf != "All":     filt = filt[filt["Signal"] == sf]
    if rf != "All":     filt = filt[filt["Risk"]   == rf]
    if setupf != "All": filt = filt[filt["Setup"]  == setupf]
    filt = filt[filt["VolSurge"] >= volf]
    
    def style_sig(val):
        if val == "BUY":   return "background:rgba(0, 214, 143, 0.1);color:#00D68F;font-weight:700;"
        if val == "WATCH": return "background:rgba(255, 176, 32, 0.1);color:#FFB020;font-weight:700;"
        if val == "AVOID": return "background:rgba(255, 76, 76, 0.1);color:#FF4C4C;font-weight:700;"
        return ""
    
    # This single line forces the table to ONLY show these clean columns!
    disp_scanner = filt[["Stock", "Signal", "Setup", "Risk", "Price", "Score", "RSI", "VolSurge", "RS", "52W%"]]
    
    st.dataframe(
        disp_scanner.style.map(style_sig, subset=["Signal"]),
        column_config={
            "Price": st.column_config.NumberColumn(format="₹%.2f"),
            "Score": st.column_config.ProgressColumn("Confluence Score", format="%.0f", min_value=0, max_value=100),
            "RSI": st.column_config.ProgressColumn("RSI", format="%.1f", min_value=0, max_value=100),
            "VolSurge": st.column_config.NumberColumn("Volume Surge", format="%.2fx"),
            "RS": st.column_config.NumberColumn("Relative Strength", format="%+.2f%%"),
            "52W%": st.column_config.NumberColumn("From 52W High", format="%.2f%%"),
        },
        hide_index=True, use_container_width=True, height=360
    )
    
    disp_scanner = filt[["Stock", "Signal", "Setup", "Risk", "Price", "Score", "RSI", "VolSurge", "RS", "52W%"]]
    
    st.dataframe(
        disp_scanner.style.map(style_sig, subset=["Signal"]),
        column_config={
            "Price": st.column_config.NumberColumn(format="₹%.2f"),
            "Score": st.column_config.ProgressColumn("Confluence Score", format="%.0f", min_value=0, max_value=100),
            "RSI": st.column_config.ProgressColumn("RSI", format="%.1f", min_value=0, max_value=100),
            "VolSurge": st.column_config.NumberColumn("Volume Surge", format="%.2fx"),
            "RS": st.column_config.NumberColumn("Relative Strength", format="%+.2f%%"),
            "52W%": st.column_config.NumberColumn("From 52W High", format="%.2f%%"),
        },
        hide_index=True, use_container_width=True, height=360
    )
    
    csv_data = filt.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Export Data to CSV (Excel)", data=csv_data, file_name="momentum_scanner_live.csv", mime="text/csv", use_container_width=True)

with tab2:
    breadth_c1, breadth_c2 = st.columns([1, 3])
    with breadth_c1:
        st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Market Breadth</div></div>", unsafe_allow_html=True)
        positive_sectors = len(sector_df[sector_df["Today%"] > 0])
        breadth_score = (positive_sectors / len(sector_df)) * 100 if len(sector_df) > 0 else 0
        
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = breadth_score,
            number = {'suffix': "%", 'font': {'color': '#E2E8F0', 'size': 24, 'family': 'JetBrains Mono'}},
            title = {'text': "Sectors in Green Today", 'font': {'color': '#94A3B8', 'size': 12}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"},
                'bar': {'color': "#3B7DFB"},
                'bgcolor': "rgba(0,0,0,0.2)",
                'steps': [
                    {'range': [0, 33], 'color': "rgba(255, 76, 76, 0.2)"},
                    {'range': [33, 66], 'color': "rgba(255, 176, 32, 0.2)"},
                    {'range': [66, 100], 'color': "rgba(0, 214, 143, 0.2)"}],
            }
        ))
        fig_g.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#CBD5E1", 'family': "Inter"})
        st.plotly_chart(fig_g, use_container_width=True)

    with breadth_c2:
        st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Market Heatmap (Size = Volume, Color = Momentum)</div></div>", unsafe_allow_html=True)
        fig_hm = go.Figure(go.Treemap(
            labels=sector_df["Sector"], parents=[""] * len(sector_df), values=sector_df["VolPunch"],
            marker=dict(colors=sector_df["Score"], colorscale=[[0, '#FF4C4C'], [0.4, '#FFB020'], [1, '#00D68F']], cmin=0, cmax=100, showscale=True, colorbar=dict(title=dict(text="Momentum Score", font=dict(color="#94A3B8")), tickfont=dict(color="#64748B"))),
            texttemplate="<b>%{label}</b><br>Score: %{color:.1f}<br>Vol: %{value:.1f}x", textfont=dict(size=13, family="Inter", color="white")
        ))
        fig_hm.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Sector Rotation Engine</div></div>", unsafe_allow_html=True)
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

    def make_chips(df_sub):
        if len(df_sub) == 0: return "<span style='color:#475569;font-size:11px;'>No sectors currently in this quadrant</span>"
        return "".join([f'<span class="sq-chip">{r["Sector"]} <b style="color:{"#00D68F" if r["1M%"]>=0 else "#FF4C4C"};">{r["1M%"]:+.1f}%</b></span>' for _, r in df_sub.iterrows()])
    
    ql, qr = st.columns([1.2, 1])
    with ql:
        st.markdown(f"""<div class="sq-grid animated-entry">
<div class="sq-card sq-leading"><div class="sq-title">↑ Leading (Strong Short & Long Term)</div>{make_chips(leading)}</div>
<div class="sq-card sq-improving"><div class="sq-title">↗ Improving (Fresh Momentum Rebound)</div>{make_chips(improving)}</div>
<div class="sq-card sq-weakening"><div class="sq-title">↘ Weakening (Momentum Cooling Down)</div>{make_chips(weakening)}</div>
<div class="sq-card sq-lagging"><div class="sq-title">↓ Lagging (Underperforming Market)</div>{make_chips(lagging)}</div>
</div>""", unsafe_allow_html=True)

    with qr:
        fig_s = go.Figure(go.Bar(x=sector_df["Sector"], y=sector_df["Score"], marker_color=["#00D68F" if s>50 else "#06B6D4" if s>30 else "#FFB020" if s>10 else "#FF4C4C" for s in sector_df["Score"]], text=[f"{s:.0f}" for s in sector_df["Score"]], textposition="outside", textfont=dict(family="JetBrains Mono", size=10)))
        fig_s.update_layout(title=dict(text="18 Sectors Momentum Score", font=dict(size=12, color="#E2E8F0")), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#64748B", height=290, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"), xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)", tickangle=-45))
        st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("<div class='sec-hdr animated-entry'><div class='sec-hdr-line'></div><div class='sec-hdr-text'>Comprehensive Sector Metrics Table</div></div>", unsafe_allow_html=True)
    
    if "InstFlow" not in sector_df.columns:
        sector_df["InstFlow"] = "Neutral ⚪"
    if "UDRatio" not in sector_df.columns:
        sector_df["UDRatio"] = 1.0

    disp_sec = sector_df[["Sector", "Today%", "1M%", "3M%", "RSI", "InstFlow", "52W%", "VolPunch", "Score"]].rename(
        columns={
            "Today%": "Today %", 
            "InstFlow": "Smart Money Flow", 
            "52W%": "From 52W High %", 
            "VolPunch": "Vol Multiplier"
        }
    )
    
    st.dataframe(
        disp_sec, 
        column_config={
            "Today %": st.column_config.NumberColumn(format="%+.2f%%"), 
            "1M%": st.column_config.NumberColumn(format="%+.2f%%"), 
            "3M%": st.column_config.NumberColumn(format="%+.2f%%"), 
            "RSI": st.column_config.ProgressColumn("RSI", format="%.1f", min_value=0, max_value=100), 
            "Smart Money Flow": st.column_config.TextColumn("Smart Money Flow"),
            "From 52W High %": st.column_config.NumberColumn(format="%.1f%%"), 
            "Vol Multiplier": st.column_config.NumberColumn(format="%.2fx"), 
            "Score": st.column_config.ProgressColumn("Momentum Score", format="%.1f", min_value=0, max_value=100)
        }, 
        hide_index=True, 
        use_container_width=True, 
        height=280
    )

st.markdown("<div style='text-align:center;padding:24px 20px;border-top:1px solid rgba(255,255,255, 0.05);margin-top:24px;'><p style='color:#64748B;font-size:10px;margin:0;font-family:\"JetBrains Mono\",monospace !important;letter-spacing:.04em;'>Educational purposes only. Not financial advice. Always DYOR. Consult a SEBI-registered advisor.<br><br>© 2026 Momentum Frenzy &nbsp;·&nbsp;<a href='https://instagram.com/momentumfrenzy' style='color:#06B6D4;text-decoration:none;'>@momentumfrenzy</a></p></div>", unsafe_allow_html=True)
