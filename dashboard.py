import streamlit as st

# --- CONFIG & SECRETS ---
BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(
    page_title="Momentum Frenzy — Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS & STYLING (Forced Fonts & Cleaned Classes)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

/* Force the base fonts using !important to override Streamlit's defaults */
html, body, .stApp, div { 
    font-family: 'Inter', sans-serif !important; 
}
.mono, .pick-stock, .pick-buy-badge, .pick-cell-lbl, .sec-hdr-text { 
    font-family: 'JetBrains Mono', monospace !important; 
}

html, body, .stApp { background:#07091A; color:#CBD5E1; }
.block-container { padding: 2rem 1rem 4rem 1rem; max-width: 100%; }
header[data-testid="stHeader"], #MainMenu, footer { display:none; }

/* Header & Typography */
.sec-hdr { display:flex; align-items:center; gap:10px; padding:12px 0; border-bottom:1px solid #0F1A35; margin-bottom:24px; }
.sec-hdr-line { width:4px; height:18px; background:linear-gradient(to bottom, #3B7DFB, #06B6D4); border-radius:2px; }
.sec-hdr-text { font-size:14px; font-weight:700; color:#E2E8F0; text-transform:uppercase; letter-spacing:.12em; }

/* Pick Cards */
.pick-card { 
    background:#0D1120; 
    border:1px solid #1E2D47; 
    border-radius:12px; 
    overflow:hidden; 
    transition: transform 0.3s ease, border-color 0.3s ease; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
    margin-bottom: 20px;
}
.pick-card:hover { 
    border-color:#3B7DFB; 
    transform: translateY(-4px); 
}
.pick-card-head { 
    display:flex; 
    align-items:center; 
    justify-content:space-between; 
    padding:16px; 
    border-bottom:1px solid #0F1A35; 
    background:linear-gradient(180deg, #101628, #0D1120); 
}
.pick-stock { font-size:22px; font-weight:800; color:#FFFFFF; margin:0; line-height:1;}
.pick-buy-badge { 
    background: rgba(0, 214, 143, 0.15); 
    color:#00D68F; 
    font-size:11px; 
    font-weight:800; 
    padding:6px 12px; 
    border-radius:6px; 
    border:1px solid rgba(0, 214, 143, 0.4); 
    letter-spacing:.1em; 
    white-space: nowrap;
}
.pick-grid { display:grid; grid-template-columns:1fr 1fr; gap:1px; background:#0F1A35; }
.pick-cell { background:#0A0E1E; padding:12px 16px; }
.pick-cell-lbl { font-size:10px; color:#64748B; text-transform:uppercase; letter-spacing:.1em; margin-bottom:4px; font-weight: 600; }
.text-up { color: #00D68F; }

/* Animation */
@keyframes fadeSlideUp {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}
.animated-entry { animation: fadeSlideUp 0.5s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="sec-hdr animated-entry">
    <div class="sec-hdr-line"></div>
    <div class="sec-hdr-text">Live Momentum Picks</div>
</div>
""", unsafe_allow_html=True)

# Use Streamlit columns to prevent the cards from stretching across the whole wide screen!
# 3 columns means each card will take up 1/3 of the screen width.
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="pick-card animated-entry">
        <div class="pick-card-head">
            <div class="pick-stock">NVDA</div>
            <div class="pick-buy-badge">STRONG BUY</div>
        </div>
        <div class="pick-grid">
            <div class="pick-cell">
                <div class="pick-cell-lbl">Entry Price</div>
                <div class="mono" style="color: white; font-size: 16px; font-weight: 600;">$124.50</div>
            </div>
            <div class="pick-cell">
                <div class="pick-cell-lbl">Target</div>
                <div class="mono text-up" style="font-size: 16px; font-weight: 600;">$135.00</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pick-card animated-entry" style="animation-delay: 0.1s;">
        <div class="pick-card-head">
            <div class="pick-stock">AMD</div>
            <div class="pick-buy-badge" style="color:#FFB020; background:rgba(255,176,32,0.15); border-color:rgba(255,176,32,0.4);">WATCH</div>
        </div>
        <div class="pick-grid">
            <div class="pick-cell">
                <div class="pick-cell-lbl">Entry Price</div>
                <div class="mono" style="color: white; font-size: 16px; font-weight: 600;">$156.20</div>
            </div>
            <div class="pick-cell">
                <div class="pick-cell-lbl">Target</div>
                <div class="mono" style="color: #FFB020; font-size: 16px; font-weight: 600;">$165.00</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
