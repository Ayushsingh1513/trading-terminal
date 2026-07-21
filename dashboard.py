import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timezone, timedelta

# --- CONFIG & SECRETS ---
BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(
    page_title="Momentum Frenzy — Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state.page = "landing"

# ══════════════════════════════════════════════════════════════════════════════
# CSS & STYLING (Fixed closing quotes and added animations)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html,body,.stApp { background:#07091A; color:#CBD5E1; font-family:'Inter',sans-serif; }
.block-container { padding:0 0 4rem 0; max-width:100%; }
header[data-testid="stHeader"], #MainMenu, footer { display:none; }

/* Global Utilities */
.mono { font-family:'JetBrains Mono',monospace; }
.text-up { color: #00D68F; }
.text-down { color: #FF4C4C; }
.text-warn { color: #FFB020; }
.text-blue { color: #3B7DFB; }

/* Telegram Panel */
.tg-panel { background:#0A1020; border:1px solid #1E3A8A; border-radius:8px; padding:16px; margin-bottom: 20px; }
.tg-title { font-size: 13px; font-weight: 600; color: #60A5FA; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.tg-btn-row { display: flex; gap: 12px; }

/* Ticker Bar */
.ticker-bar { background:#0A0E1E; border-bottom:1px solid #0F1A35; padding:0 20px; display:flex; align-items:center; position:sticky; top:0; z-index:999; height:45px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
.ticker-bar::-webkit-scrollbar { display: none; }
.ticker-item { display:flex; align-items:center; gap:8px; padding:0 18px; border-right:1px solid #0F1A35; height:100%; }
.ticker-label { font-family:'JetBrains Mono',monospace; font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:.1em; font-weight:600; }
.ticker-val { font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:700; color:#F1F5F9; }

/* Header & Typography */
.sec-hdr { display:flex; align-items:center; gap:10px; padding:24px 0 12px 0; border-bottom:1px solid #0F1A35; margin-bottom:16px; }
.sec-hdr-line { width:4px; height:18px; background:linear-gradient(to bottom, #3B7DFB, #06B6D4); border-radius:2px; }
.sec-hdr-text { font-size:13px; font-weight:700; color:#E2E8F0; text-transform:uppercase; letter-spacing:.12em; }

/* Pick Cards - Base Styling */
.pick-card { 
    background:#0D1120; 
    border:1px solid #1E2D47; 
    border-radius:12px; 
    overflow:hidden; 
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
}
.pick-card:hover { 
    border-color:#3B7DFB; 
    transform: translateY(-4px); 
    box-shadow: 0 8px 25px rgba(59, 125, 251, 0.15);
}
.pick-card-head { display:flex; align-items:center; justify-content:space-between; padding:16px; border-bottom:1px solid #0F1A35; background:linear-gradient(180deg, #101628, #0D1120); }
.pick-stock { font-family:'JetBrains Mono',monospace; font-size:20px; font-weight:800; color:#FFFFFF; }
.pick-buy-badge { background:#00D68F15; color:#00D68F; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:800; padding:6px 12px; border-radius:6px; border:1px solid #00D68F40; letter-spacing:.1em; }
.pick-grid { display:grid; grid-template-columns:1fr 1fr; gap:1px; background:#0F1A35; }
.pick-cell { background:#0A0E1E; padding:12px 16px; }

/* FIX: Completed the broken CSS line here */
.pick-cell-lbl { font-size:10px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; font-weight: 600; }

/* --- NEW PROFESSIONAL ANIMATIONS --- */
@keyframes fadeSlideUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.animated-entry {
    animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

</style>
""", unsafe_allow_html=True) # FIX: Properly closed the triple quotes

# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="sec-hdr animated-entry"><div class="sec-hdr-line"></div><div class="sec-hdr-text">Live Momentum Picks</div></div>', unsafe_allow_html=True)

# Example of how to structure your animated cards without the charts
st.markdown("""
<div class="pick-card animated-entry" style="margin-bottom: 20px;">
    <div class="pick-card-head">
        <div class="pick-stock">NVDA</div>
        <div class="pick-buy-badge">STRONG BUY</div>
    </div>
    <div class="pick-grid">
        <div class="pick-cell">
            <div class="pick-cell-lbl">Entry Price</div>
            <div class="mono" style="color: white; font-size: 16px;">$124.50</div>
        </div>
        <div class="pick-cell">
            <div class="pick-cell-lbl">Target</div>
            <div class="mono text-up" style="font-size: 16px;">$135.00</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
