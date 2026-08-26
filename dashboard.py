import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import datetime

# Safe import for Plotly
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Institutional Confidence Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- ADVANCED INSTITUTIONAL CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0B0E14; color: #E2E8F0; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Card Design */
    .metric-card {
        background-color: #131822;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        color: #94A3B8;
        font-weight: 600;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #00FFAA !important;
        background-color: #131822 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def safe_float(val, default=0.0):
    if pd.isna(val) or val in ["", None, "None", "nan"]: return default
    try: return float(val)
    except: return default

def load_json_history(filepath="performance_history.json"):
    if not os.path.exists(filepath): return pd.DataFrame()
    try:
        with open(filepath, "r") as f: data = json.load(f)
        if not data: return pd.DataFrame()
        if isinstance(data, list): return pd.DataFrame(data)
        elif isinstance(data, dict):
            max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
            padded = {k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len) for k, v in data.items()}
            return pd.DataFrame(padded)
    except: pass
    return pd.DataFrame()

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=50)
    st.title("Alpha Terminal")
    st.caption("Institutional Intelligence Engine")
    st.markdown("---")
    
    st.subheader("⚙️ Portfolio Risk Controls")
    total_corpus = st.number_input("Total Corpus (₹)", value=100000.0, step=10000.0, format="%.2f")
    max_trade_capital = st.number_input("Max Allocation / Trade (₹)", value=50000.0, step=5000.0, format="%.2f")
    risk_pct = st.slider("Risk Per Trade (%)", 0.25, 3.0, 1.0, 0.25) / 100.0
    
    st.markdown("---")
    st.info("💡 **Tip:** Click on any stock in the Live Scanner tab to load its interactive institutional chart and AI War Room breakdown.")

# --- MAIN TABS ---
tab_scanner, tab_pnl, tab_shadow = st.tabs([
    "🔭 Live Market Scanner & War Room", 
    "📈 Performance & Risk Ledger", 
    "🛡️ AI Veto Watchlist"
])

# ==========================================
# TAB 1: LIVE SCANNER & VISUAL WAR ROOM
# ==========================================
with tab_scanner:
    st.markdown("### 🔭 Market Discovery & Visual Verification")
    
    if os.path.exists("scanner_data.csv"):
        live_df = pd.read_csv("scanner_data.csv")
        
        # Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Universe Scanned", len(live_df))
        high_conv = len(live_df[pd.to_numeric(live_df['Score'], errors='coerce') >= 80])
        c2.metric("High Conviction Setups", high_conv)
        golden_count = len(live_df[live_df['Setup'].astype(str).str.contains('Golden', case=False, na=False)])
        c3.metric("🏆 Golden Momentum", golden_count)
        vcp_count = len(live_df[live_df['Setup'].astype(str).str.contains('VCP', case=False, na=False)])
        c4.metric("📈 VCP Breakouts", vcp_count)
        
        st.markdown("---")
        
        if not live_df.empty:
            # Dropdown Selector for Deep Dive
            stock_list = live_df['Stock'].tolist()
            selected_stock = st.selectbox("🎯 Select Stock for Visual War Room & Chart Inspection", stock_list)
            
            # Filter row data for selected stock
            stock_row = live_df[live_df['Stock'] == selected_stock].iloc[0]
            
            # Layout: 2 Columns (Left: Interactive Chart, Right: AI War Room & Risk Blueprint)
            col_chart, col_warroom = st.columns([1.3, 1])
            
            with col_chart:
                st.markdown(f"#### 📊 Institutional Price Action: {selected_stock}")
                
                with st.spinner(f"Loading historical data for {selected_stock}..."):
                    hist_df = yf.Ticker(selected_stock).history(period="6mo")
                    
                if not hist_df.empty and HAS_PLOTLY:
                    hist_df['EMA_20'] = hist_df['Close'].ewm(span=20).mean()
                    
                    fig = go.Figure()
                    # Candlesticks
                    fig.add_trace(go.Candlestick(
                        x=hist_df.index,
                        open=hist_df['Open'], high=hist_df['High'],
                        low=hist_df['Low'], close=hist_df['Close'],
                        name="Price Action",
                        increasing_line_color='#00FFAA', decreasing_line_color='#FF4444'
                    ))
                    # 20 EMA
                    fig.add_trace(go.Scatter(
                        x=hist_df.index, y=hist_df['EMA_20'],
                        line=dict(color='#3B82F6', width=1.5), name="20 EMA"
                    ))
                    
                    # Horizontal Trade Lines
                    entry_p = safe_float(stock_row.get('Entry'))
                    sl_p = safe_float(stock_row.get('SL'))
                    t2_p = safe_float(stock_row.get('Target2'))
                    
                    if entry_p > 0:
                        fig.add_hline(y=entry_p, line_dash="dash", line_color="#00FFAA", annotation_text=f"Entry: ₹{entry_p}")
                    if sl_p > 0:
                        fig.add_hline(y=sl_p, line_dash="solid", line_color="#FF4444", annotation_text=f"Stop Loss: ₹{sl_p}")
                    if t2_p > 0:
                        fig.add_hline(y=t2_p, line_dash="dash", line_color="#3B82F6", annotation_text=f"Target: ₹{t2_p}")
                        
                    fig.update_layout(
                        template="plotly_dark",
                        plot_bgcolor='#131822', paper_bgcolor='#131822',
                        margin=dict(l=10, r=10, t=20, b=10),
                        height=420,
                        xaxis_rangeslider_visible=False,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not render interactive chart for this ticker.")
                    
            with col_warroom:
                st.markdown("#### 🤖 AI War Room & Risk Blueprint")
                
                # Fetch live news for sentiment breakdown
                with st.spinner("Consulting Newsdesk Agent..."):
                    news_data = yf.Ticker(selected_stock).news
                    
                sentiment_txt = "⚪ Neutral News Flow"
                score_val = safe_float(stock_row.get('Score', 50))
                
                st.markdown(f"""
                <div class="metric-card">
                    <b>Setup Identified:</b> {stock_row.get('Setup')}<br>
                    <b>AI Conviction Score:</b> {score_val}/100<br>
                    <b>Relative Strength (RSI):</b> {stock_row.get('RSI')}<br>
                    <b>Volume Multiplier:</b> {stock_row.get('VolSurge')}x 20D Avg<br>
                    <b>Risk-to-Reward:</b> 1:{stock_row.get('RR')}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Position Sizing Calculation
                e = safe_float(stock_row.get('Entry'))
                s = safe_float(stock_row.get('SL'))
                if e > 0 and s > 0 and e > s:
                    risk_per_share = e - s
                    max_risk_allowed = total_corpus * risk_pct
                    calc_qty = int(max_risk_allowed / risk_per_share)
                    max_cap_qty = int(max_trade_capital / e)
                    final_qty = min(calc_qty, max_cap_qty)
                    final_qty = max(1, final_qty)
                    total_deployment = final_qty * e
                    total_risk_rs = final_qty * risk_per_share
                    
                    st.markdown(f"""
                    <div style="background-color: #1E293B; padding: 12px; border-radius: 8px; border-left: 4px solid #00FFAA;">
                        📦 <b>Position Blueprint:</b><br>
                        • Shares to Acquire: <b>{final_qty} units</b><br>
                        • Capital Deployed: <b>₹{total_deployment:,.2f}</b><br>
                        • Maximum Financial Risk: <b style="color:#FF4444;">₹{total_risk_rs:,.2f} ({risk_pct*100}% of corpus)</b>
                    </div>
                    """, unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("#### 📋 Full Nifty 500 Scanner Directory")
            
            # Styled full dataframe
            st.dataframe(
                live_df.style.format({
                    "Price": "₹{:.2f}", "Entry": "₹{:.2f}", "SL": "₹{:.2f}",
                    "Target1": "₹{:.2f}", "Target2": "₹{:.2f}", "VolSurge": "{:.2f}x", "RR": "1:{:.1f}"
                }),
                use_container_width=True,
                height=300,
                hide_index=True
            )
    else:
        st.info("Awaiting initial background workflow scan. `scanner_data.csv` is currently empty.")

# ==========================================
# TAB 2: PERFORMANCE & PNL LEDGER
# ==========================================
with tab_pnl:
    st.markdown("### 📈 Portfolio Growth & Execution History")
    raw_history = load_json_history("performance_history.json")
    
    if raw_history.empty:
        st.info("No trade execution records found in ledger yet.")
    else:
        # Display KPIs
        closed_filter = raw_history['Status'].astype(str).str.contains('CLOSED|HIT|EXIT', case=False, na=False)
        closed_df = raw_history[closed_filter]
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Recorded Trades", len(raw_history))
        k2.metric("Closed Executions", len(closed_df))
        k3.metric("Starting Corpus", f"₹{total_corpus:,.2f}")
        
        st.markdown("---")
        st.dataframe(raw_history, use_container_width=True, height=400)

# ==========================================
# TAB 3: AI VETO WATCHLIST
# ==========================================
with tab_shadow:
    st.markdown("### 🛡️ AI Veto & Shadow Watchlist")
    raw_history = load_json_history("performance_history.json")
    
    if not raw_history.empty:
        veto_filter = raw_history['Status'].astype(str).str.contains('WATCHLIST|VETO', case=False, na=False)
        veto_df = raw_history[veto_filter]
        if not veto_df.empty:
            st.dataframe(veto_df, use_container_width=True, height=400)
        else:
            st.info("No stocks are currently sitting in the AI Veto shadow ledger.")
    else:
        st.info("Shadow ledger is empty.")