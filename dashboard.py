import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Momentum Frenzy v2.0", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

@st.cache_data(ttl=30)
def load_data():
    if not os.path.exists("market_data.json") or not os.path.exists("scanner_data.csv") or not os.path.exists("sector_data.csv"): 
        return None, None, None
    try: 
        return json.load(open("market_data.json")), pd.read_csv("scanner_data.csv"), pd.read_csv("sector_data.csv")
    except: 
        return None, None, None

market_data, scanner_df, sector_df = load_data()

if market_data is None:
    st.markdown("<div style='text-align:center; padding:100px; color:#06B6D4;'><h2>⚙️ Initializing Engine v2.0...</h2></div>", unsafe_allow_html=True)
    st.stop()

st.markdown("""<style>
.stApp{background:#07091A !important; color:#CBD5E1;} 
header[data-testid="stHeader"],#MainMenu,footer{display:none;}
.block-container{padding:0 1rem 3rem 1rem !important;}
.ticker-bar{background:rgba(13,17,32,0.8); backdrop-filter:blur(10px); border-bottom:1px solid rgba(255,255,255,0.08); padding:8px 20px; display:flex; gap:20px; align-items:center; font-family:monospace; font-size:12px; margin-bottom:20px;}
.pick-card{background:rgba(13,17,35,0.5); border:1px solid rgba(0,214,143,0.3); border-radius:14px; padding:16px; margin-bottom:16px;}
.pick-head{display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px; margin-bottom:12px;}
.pick-stock{font-size:20px; font-weight:800; color:#FFF;}
.pick-badge{background:rgba(0,214,143,0.15); color:#00D68F; font-size:10px; font-weight:800; padding:4px 8px; border-radius:4px; border:1px solid rgba(0,214,143,0.4);}
.pick-grid{display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:8px; text-align:center; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;}
.pick-lbl{font-size:9px; color:#64748B; text-transform:uppercase;} 
.pick-val{font-size:14px; font-weight:700;}
</style>""", unsafe_allow_html=True)

nl, nchg = market_data.get('nifty', 0), market_data.get('nifty_chg', 0)
sl, schg = market_data.get('sensex', 0), market_data.get('sensex_chg', 0)
tc = "color:#00D68F;" if nchg >= 0 else "color:#FF4C4C;"
sc = "color:#00D68F;" if schg >= 0 else "color:#FF4C4C;"

st.markdown(f"""<div class="ticker-bar">
<div><b>NIFTY:</b> {nl:,.0f} <span style="{tc}">{nchg:+.2f}%</span></div>
<div><b>SENSEX:</b> {sl:,.0f} <span style="{sc}">{schg:+.2f}%</span></div>
<div><b>REGIME:</b> <span style="color:#00D68F;">{market_data.get('mood', 'N/A')}</span></div>
<div><b>PCR:</b> {market_data.get('pcr', 1.0)} ({market_data.get('pcr_status', 'NEUTRAL')})</div>
<div style="margin-left:auto; color:#64748B;">Updated: {market_data.get('timestamp', '')}</div>
</div>""", unsafe_allow_html=True)

st.title("⚡ Momentum Frenzy v2.0")

st.subheader("🎯 Top Rated Setups (MTF & Weekly Trend Aligned)")
top_buys = scanner_df[scanner_df['Signal'] == 'BUY'].to_dict('records') if 'Signal' in scanner_df.columns else []

if top_buys:
    cols_per_row = 3
    for i in range(0, len(top_buys), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, pk in zip(cols, top_buys[i:i+cols_per_row]):
            mtf_val = pk.get('MTF', 'Cash Only')
            weekly_val = pk.get('WeeklyTrend', 'N/A')
            with col:
                st.markdown(f"""<div class="pick-card">
<div class="pick-head">
<div><div class="pick-stock">{pk.get('Stock', '')}</div><div style="font-size:11px; color:#94A3B8;">{mtf_val} · Weekly: {weekly_val}</div></div>
<div class="pick-badge">SCORE {pk.get('Score', 0)}/100</div>
</div>
<div class="pick-grid">
<div><div class="pick-lbl">Entry</div><div class="pick-val" style="color:#E2E8F0;">₹{pk.get('Entry', 0)}</div></div>
<div><div class="pick-lbl">Stop Loss</div><div class="pick-val" style="color:#FF4C4C;">₹{pk.get('SL', 0)}</div></div>
<div><div class="pick-lbl">Target 1</div><div class="pick-val" style="color:#00D68F;">₹{pk.get('Target1', 0)}</div></div>
<div><div class="pick-lbl">Target 2</div><div class="pick-val" style="color:#06B6D4;">₹{pk.get('Target2', 0)}</div></div>
</div>
<div style="margin-top:10px; font-size:11px; display:flex; justify-content:space-between; color:#94A3B8;">
<span>R:R = 1:{pk.get('RR', 0)}</span><span>{pk.get('Setup', '')}</span>
</div>
</div>""", unsafe_allow_html=True)
else:
    st.info("No stocks meet the strict institutional criteria right now. Cash is a position.")

st.subheader("🔍 Institutional Scanner Database")
def style_sig(val):
    if val == "BUY": return "background:rgba(0, 214, 143, 0.15); color:#00D68F; font-weight:700;"
    if val == "WATCH": return "background:rgba(255, 176, 32, 0.15); color:#FFB020; font-weight:700;"
    return "background:rgba(255, 76, 76, 0.15); color:#FF4C4C; font-weight:700;"

available_cols = [col for col in ["Stock", "Signal", "MTF", "WeeklyTrend", "Setup", "Price", "Score", "RSI", "VolSurge"] if col in scanner_df.columns]
clean_table = scanner_df[available_cols]

st.dataframe(
    clean_table.style.map(style_sig, subset=["Signal"]) if "Signal" in clean_table.columns else clean_table,
    column_config={
        "Price": st.column_config.NumberColumn(format="₹%.2f"),
        "Score": st.column_config.ProgressColumn("Confluence", format="%.0f", min_value=0, max_value=100),
        "RSI": st.column_config.ProgressColumn("RSI", format="%.1f", min_value=0, max_value=100),
        "VolSurge": st.column_config.NumberColumn("Volume Surge", format="%.2fx"),
    }, hide_index=True, use_container_width=True, height=360
)
