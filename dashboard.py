import streamlit as st
import pandas as pd
import json
import os

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Momentum Frenzy v2.0", layout="wide", page_icon="⚡")
st.title("⚡ Momentum Frenzy | Quantitative Terminal")
st.markdown("Automated NSE Swing Trading Setups, Sector Intelligence & Algorithmic Ledger")

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def load_csv(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return None

mkt = load_json("market_data.json")
history = load_json("performance_history.json") or {"active_trades": [], "closed_trades": []}
scan_df = load_csv("scanner_data.csv")
sector_df = load_csv("sector_data.csv")

# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR: MARKET PULSE & PCR
# ══════════════════════════════════════════════════════════════════════════════
if mkt:
    cols = st.columns(5)
    cols[0].metric("🏛️ NIFTY 50", f"{mkt.get('nifty', 0):,.0f}", f"{mkt.get('nifty_chg', 0):.2f}%")
    cols[1].metric("🏛️ SENSEX", f"{mkt.get('sensex', 0):,.0f}", f"{mkt.get('sensex_chg', 0):.2f}%")
    cols[2].metric("🛡️ Market Regime", mkt.get('mood', 'N/A'))
    
    pcr_status = mkt.get('pcr_status', '')
    cols[3].metric("⚖️ PCR (Put-Call Ratio)", mkt.get('pcr', 'N/A'), pcr_status)
    cols[4].write(f"**Last Engine Update:**\n{mkt.get('timestamp', 'Unknown')}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["⚡ Live Scanner", "📊 Sector Intelligence", "🏆 Performance History"])

# ─── TAB 1: LIVE SCANNER ───────────────────────────────────────────────────────
with tab1:
    st.subheader("🟢 High-Confluence Breakout Setups")
    if scan_df is not None and not scan_df.empty:
        buy_df = scan_df[scan_df['Signal'] == 'BUY']
        
        if not buy_df.empty:
            st.dataframe(
                buy_df[['Stock', 'Score', 'Setup', 'Sector', 'Entry', 'SL', 'Target1', 'Target2', 'RR', 'VolSurge']], 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No 'BUY' signals triggered in the most recent scan. Waiting for high-probability setups...")
        
        with st.expander("View Full Market Scan (All Analyzed Stocks)"):
            st.dataframe(scan_df, use_container_width=True)
    else:
        st.warning("Scanner data is currently unavailable. Ensure the Python engine is running.")

# ─── TAB 2: SECTOR INTELLIGENCE ───────────────────────────────────────────────
with tab2:
    st.subheader("🔥 Institutional Flow & Sector Leadership")
    if sector_df is not None and not sector_df.empty:
        def highlight_flow(val):
            if "Big Money Buying" in str(val): return 'color: #00FF00; font-weight: bold;'
            if "Big Money Selling" in str(val): return 'color: #FF0000; font-weight: bold;'
            return ''
            
        styled_sector = sector_df.style.map(highlight_flow, subset=['Smart Money Flow'])
        st.dataframe(styled_sector, use_container_width=True, hide_index=True)
    else:
        st.warning("Sector Intelligence data is not available yet.")

# ─── TAB 3: PERFORMANCE HISTORY (THE LEDGER) ──────────────────────────────────
with tab3:
    st.subheader("📈 Trade Ledger & System Accuracy")
    
    active_trades = history.get("active_trades", [])
    closed_trades = history.get("closed_trades", [])
    
    total_closed = len(closed_trades)
    wins = sum(1 for t in closed_trades if "TARGET" in t.get("Status", ""))
    losses = total_closed - wins
    win_rate = round((wins / total_closed) * 100, 1) if total_closed > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🟢 Active Open Trades", len(active_trades))
    m2.metric("🔒 Total Closed Trades", total_closed)
    m3.metric("🎯 System Win Rate", f"{win_rate}%")
    m4.metric("⚖️ Wins vs Losses", f"{wins}W - {losses}L")
    
    st.divider()
    
    st.markdown("### 🔴 Closed Trades Log")
    if closed_trades:
        df_closed = pd.DataFrame(closed_trades)
        
        def calc_result(row):
            if 'Exit_Price' in row and pd.notna(row['Exit_Price']) and pd.notna(row['Entry']):
                return round(((row['Exit_Price'] - row['Entry']) / row['Entry']) * 100, 2)
            return 0.0
            
        df_closed['Result %'] = df_closed.apply(calc_result, axis=1)
        
        def color_returns(val):
            color = '#00FF00' if val > 0 else '#FF4B4B'
            return f'color: {color}; font-weight: bold;'
            
        cols_to_show = ["Stock", "Status", "Entry", "Exit_Price", "Result %"]
        cols_to_show = [c for c in cols_to_show if c in df_closed.columns]
        
        styled_closed = df_closed[cols_to_show].style.map(color_returns, subset=['Result %'])
        st.dataframe(styled_closed, use_container_width=True, hide_index=True)
    else:
        st.info("No closed trades recorded in the ledger yet.")
        
    st.divider()
    
    st.markdown("### 🟢 Active Trades Log (Live Monitoring)")
    if active_trades:
        df_active = pd.DataFrame(active_trades)
        if 'T1_Hit' in df_active.columns:
            df_active['Risk Status'] = df_active['T1_Hit'].apply(lambda x: "✅ Risk Free (SL Trailed)" if x else "⏳ Standard Risk")
            
        cols_to_show_active = ["Stock", "Status", "Entry", "SL", "Target1", "Target2", "Risk Status"]
        cols_to_show_active = [c for c in cols_to_show_active if c in df_active.columns]
        
        st.dataframe(df_active[cols_to_show_active], use_container_width=True, hide_index=True)
    else:
        st.info("No active trades currently running in the market.")