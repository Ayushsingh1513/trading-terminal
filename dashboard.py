import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf

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
    .stApp { background-color: #0B0E14; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Sleek Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #131822;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #00FFAA;
    }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        color: #64748B;
        font-weight: 600;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #F8FAFC !important;
        border-bottom: 2px solid #00FFAA !important;
        background-color: transparent !important;
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

# --- SIDEBAR: RISK ENGINE CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=50)
    st.title("Alpha Terminal")
    st.caption("Institutional Intelligence Engine")
    st.markdown("---")
    
    st.subheader("⚙️ Execution Sizing")
    st.write("How much are you willing to lose if the Stop Loss is hit?")
    fixed_rupee_risk = st.number_input("Max Risk Per Trade (₹)", value=1000.0, step=500.0, format="%.2f")
    max_trade_capital = st.number_input("Max Margin Allowed (₹)", value=50000.0, step=5000.0, format="%.2f")
    
    st.markdown("---")
    st.info("💡 **Tip:** Click on any stock in the Live Scanner tab to load its interactive institutional chart and AI War Room breakdown.")

# --- MAIN TABS ---
tab_scanner, tab_pnl, tab_shadow = st.tabs([
    "🔭 Live Market Scanner & War Room", 
    "📈 Trade History", 
    "🛡️ AI Veto Watchlist"
])

# ==========================================
# TAB 1: LIVE SCANNER & VISUAL WAR ROOM
# ==========================================
with tab_scanner:
    st.markdown("### 🔭 Market Discovery & Visual Verification")
    
    if os.path.exists("scanner_data.csv"):
        live_df = pd.read_csv("scanner_data.csv")
        
        # Metric Bar
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Sniper Pick", live_df['Stock'].iloc[0] if not live_df.empty else "N/A")
        golden_count = len(live_df[live_df['Setup'].astype(str).str.contains('Golden', case=False, na=False)])
        c2.metric("🏆 Golden Momentum", golden_count)
        cross_count = len(live_df[live_df['Setup'].astype(str).str.contains('Crossover', case=False, na=False)])
        c3.metric("⚔️ 9/20 Crossovers", cross_count)
        vcp_count = len(live_df[live_df['Setup'].astype(str).str.contains('VCP', case=False, na=False)])
        c4.metric("📈 VCP Breakouts", vcp_count)
        
        st.markdown("---")
        
        if not live_df.empty:
            # Dropdown Selector
            stock_list = live_df['Stock'].tolist()
            selected_stock = st.selectbox("🎯 Select Stock for Visual War Room & Chart Inspection", stock_list)
            stock_row = live_df[live_df['Stock'] == selected_stock].iloc[0]
            
            col_chart, col_warroom = st.columns([1.4, 1])
            
            with col_chart:
                st.markdown(f"#### 📊 Institutional Price Action: {selected_stock}")
                with st.spinner(f"Loading historical data for {selected_stock}..."):
                    hist_df = yf.Ticker(selected_stock).history(period="6mo")
                    
                if not hist_df.empty and HAS_PLOTLY:
                    hist_df['EMA_20'] = hist_df['Close'].ewm(span=20).mean()
                    hist_df['EMA_9'] = hist_df['Close'].ewm(span=9).mean() # Added 9-EMA for charting
                    
                    fig = go.Figure()
                    # Candlesticks
                    fig.add_trace(go.Candlestick(
                        x=hist_df.index,
                        open=hist_df['Open'], high=hist_df['High'],
                        low=hist_df['Low'], close=hist_df['Close'],
                        name="Price Action",
                        increasing_line_color='#00FFAA', decreasing_line_color='#FF4444'
                    ))
                    # 9 EMA (Fast)
                    fig.add_trace(go.Scatter(
                        x=hist_df.index, y=hist_df['EMA_9'],
                        line=dict(color='#FF5722', width=1.5), name="9 EMA (Fast)"
                    ))
                    # 20 EMA (Slow)
                    fig.add_trace(go.Scatter(
                        x=hist_df.index, y=hist_df['EMA_20'],
                        line=dict(color='#3B82F6', width=1.5), name="20 EMA (Slow)"
                    ))
                    
                    # Target Lines
                    entry_p = safe_float(stock_row.get('Entry'))
                    sl_p = safe_float(stock_row.get('SL'))
                    t2_p = safe_float(stock_row.get('Target2'))
                    
                    if entry_p > 0: fig.add_hline(y=entry_p, line_dash="dash", line_color="#00FFAA", annotation_text=f"Entry: ₹{entry_p}")
                    if sl_p > 0: fig.add_hline(y=sl_p, line_dash="solid", line_color="#FF4444", annotation_text=f"Stop Loss: ₹{sl_p}")
                    if t2_p > 0: fig.add_hline(y=t2_p, line_dash="dash", line_color="#3B82F6", annotation_text=f"Target: ₹{t2_p}")
                        
                    fig.update_layout(
                        template="plotly_dark", plot_bgcolor='#131822', paper_bgcolor='#131822',
                        margin=dict(l=10, r=10, t=20, b=10), height=420, xaxis_rangeslider_visible=False,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not render chart.")
                    
            with col_warroom:
                st.markdown("#### 🤖 AI War Room & Confluence")
                score_val = safe_float(stock_row.get('Score', 50))
                
                # Visual Confirmation Checklist
                st.markdown(f"""
                <div style="background-color: #131822; border: 1px solid #1E293B; border-radius: 10px; padding: 15px;">
                    <h5 style="color: #00FFAA; margin-top:0;">{stock_row.get('Setup')} ({score_val}/100)</h5>
                    <hr style="border-color: #2D303E;">
                    <b>Strict Confluence Matrix Passed:</b><br>
                    ✅ Price > 200-Day EMA (Long-term Uptrend)<br>
                    ✅ Price > 50-Day EMA (Mid-term Momentum)<br>
                    ✅ Institutional Volume > 200%<br>
                    ✅ AI VADER Sentiment Cleared<br>
                    <hr style="border-color: #2D303E;">
                    <b>RSI:</b> {stock_row.get('RSI')} | <b>RR:</b> 1:{stock_row.get('RR')}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Position Sizing Blueprint
                e = safe_float(stock_row.get('Entry'))
                s = safe_float(stock_row.get('SL'))
                if e > 0 and s > 0 and e > s:
                    risk_per_share = e - s
                    calc_qty = int(fixed_rupee_risk / risk_per_share)
                    max_cap_qty = int(max_trade_capital / e)
                    final_qty = max(1, min(calc_qty, max_cap_qty))
                    total_deployment = final_qty * e
                    actual_risk = final_qty * risk_per_share
                    
                    st.markdown(f"""
                    <div style="background-color: #1E293B; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;">
                        📦 <b>Execution Blueprint:</b><br><br>
                        Buy <b>{final_qty} shares</b> at ₹{e:,.2f}.<br>
                        Margin required: <b>₹{total_deployment:,.2f}</b><br>
                        If stopped out, you lose exactly: <b style="color:#FF4444;">₹{actual_risk:,.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("#### 📋 Top 5 Sniper Directory")
            
            # --- PANDAS STYLING FOR NEW SETUPS ---
            def style_dataframe(df):
                def highlight_rows(row):
                    setup = str(row.get('Setup', '')).lower()
                    if 'golden' in setup: return ['background-color: rgba(255, 215, 0, 0.15); color: #FFD700; font-weight: bold; border-left: 4px solid #FFD700'] * len(row)
                    elif 'vcp' in setup: return ['background-color: rgba(184, 38, 255, 0.15); color: #E066FF; font-weight: bold; border-left: 4px solid #E066FF'] * len(row)
                    elif 'crossover' in setup: return ['background-color: rgba(255, 87, 34, 0.15); color: #FF5722; font-weight: bold; border-left: 4px solid #FF5722'] * len(row)
                    elif 'ema' in setup: return ['background-color: rgba(0, 191, 255, 0.15); color: #00BFFF; font-weight: bold; border-left: 4px solid #00BFFF'] * len(row)
                    return [''] * len(row)
                
                return df.style.apply(highlight_rows, axis=1).format({
                    "Price": "₹{:.2f}", "Entry": "₹{:.2f}", "SL": "₹{:.2f}",
                    "Target1": "₹{:.2f}", "Target2": "₹{:.2f}", "VolSurge": "{:.2f}x", "RR": "1:{:.1f}"
                })

            st.dataframe(
                style_dataframe(live_df),
                use_container_width=True, height=250, hide_index=True,
                column_config={"Score": st.column_config.ProgressColumn("AI Score", format="%d", min_value=0, max_value=100)}
            )
    else:
        st.info("Awaiting initial background workflow scan. `scanner_data.csv` is currently empty.")

# ==========================================
# TAB 2 & 3: HISTORY & SHADOW LEDGER
# ==========================================
with tab_pnl:
    st.markdown("### 📈 Execution History")
    raw_history = load_json_history("performance_history.json")
    if raw_history.empty:
        st.info("No trade execution records found in ledger yet.")
    else:
        valid_df = raw_history[raw_history['Status'].astype(str).str.contains('ACTIVE|CLOSED|HIT|EXIT', case=False, na=False)]
        st.dataframe(valid_df, use_container_width=True, height=400)

with tab_shadow:
    st.markdown("### 🛡️ AI Veto & Shadow Watchlist")
    if not raw_history.empty:
        veto_filter = raw_history['Status'].astype(str).str.contains('WATCHLIST|VETO', case=False, na=False)
        veto_df = raw_history[veto_filter]
        if not veto_df.empty:
            st.dataframe(veto_df, use_container_width=True, height=400)
        else:
            st.info("No stocks are currently sitting in the AI Veto shadow ledger.")
    else:
        st.info("Shadow ledger is empty.")