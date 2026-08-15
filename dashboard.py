import os
import json
import pandas as pd
import numpy as np
import streamlit as st

# Safe import for Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Momentum Frenzy | Alpha Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Clean Top Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Styled Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1A1C23;
        border: 1px solid #2D303E;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #00FFAA;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #A0AEC0;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #FFFFFF;
        border-bottom: 2px solid #00FFAA;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def safe_float(val, default=0.0):
    if pd.isna(val) or val in ["", None, "None", "nan"]: 
        return default
    try: 
        return float(val)
    except (ValueError, TypeError): 
        return default

def is_trade_closed(status_str):
    status = str(status_str).upper()
    return any(keyword in status for keyword in ["CLOSED", "HIT", "EXIT", "STOPPED", "TARGET"])

def load_json_history(filepath="performance_history.json"):
    if not os.path.exists(filepath): return pd.DataFrame()
    try:
        with open(filepath, "r") as f: data = json.load(f)
        if not data: return pd.DataFrame()
        if isinstance(data, list): return pd.DataFrame(data)
        elif isinstance(data, dict):
            try: return pd.DataFrame(data)
            except ValueError:
                max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
                padded = {k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len) for k, v in data.items()}
                return pd.DataFrame(padded)
    except Exception: pass
    return pd.DataFrame()

# --- SIDEBAR: RISK ENGINE CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/combo-chart.png", width=60)
    st.title("Momentum Engine")
    st.caption("v3.0 | Multi-Agent Execution")
    st.markdown("---")
    
    st.subheader("⚙️ Risk Parameters")
    total_corpus = st.number_input("Starting Corpus (₹)", value=100000.0, step=10000.0, format="%.2f")
    max_trade_capital = st.number_input("Max Allocation / Trade (₹)", value=50000.0, step=5000.0, format="%.2f")
    risk_pct = st.slider("Risk Per Trade (%)", min_value=0.25, max_value=5.0, value=1.0, step=0.25) / 100.0
    
    st.markdown("---")
    min_score_filter = st.slider("Filter Minimum Score", min_value=50, max_value=100, value=80, step=5)

# --- TABS LAYOUT ---
tab_screener, tab_performance, tab_shadow = st.tabs([
    "🔭 Live Market Scanner", 
    "📈 Risk Ledger & PnL", 
    "🛡️ AI Veto Watchlist"
])

# ==========================================
# TAB 1: LIVE MARKET SCANNER
# ==========================================
with tab_screener:
    st.markdown("### 🔭 Market Discovery Engine")
    
    if os.path.exists("scanner_data.csv"):
        try:
            live_df = pd.read_csv("scanner_data.csv")
            
            # Overview Metrics
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("Total Scanned", len(live_df))
            
            score_col = next((c for c in live_df.columns if c.lower() == 'score'), None)
            if score_col:
                clean_sc = live_df[score_col].astype(str).str.extract(r'(\d+(?:\.\d+)?)', expand=False)
                num_sc = pd.to_numeric(clean_sc, errors='coerce').fillna(0.0)
                col_s2.metric("High Conviction (≥80)", len(live_df[num_sc >= 80]))
            
            vol_col = next((c for c in live_df.columns if 'volume' in c.lower() or 'volsurge' in c.lower()), None)
            if vol_col:
                vol_clean = pd.to_numeric(live_df[vol_col], errors='coerce').fillna(0)
                col_s3.metric("Institutional Vol Spikes", len(live_df[vol_clean > 1.5]))
                
            setup_col = next((c for c in live_df.columns if 'setup' in c.lower() or 'signal' in c.lower()), None)
            if setup_col:
                # Count any of the 3 new elite setups
                elite_mask = live_df[setup_col].astype(str).str.contains('Golden|VCP|EMA', case=False, na=False)
                elite_count = len(live_df[elite_mask])
                col_s4.metric("🏆 Elite Setups", elite_count)

            st.markdown("---")
            
            # Interactive Search
            search = st.text_input("🔍 Filter by Ticker, Sector, or Setup Type...", "")
            if search:
                live_df = live_df[live_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
                
            # --- PANDAS STYLING FOR NEW SETUPS ---
            def style_dataframe(df):
                def highlight_rows(row):
                    setup = str(row.get('Setup', '')).lower()
                    signal = str(row.get('Signal', '')).upper()
                    
                    if 'golden' in setup:
                        return ['background-color: rgba(255, 215, 0, 0.15); color: #FFD700; font-weight: bold; border-left: 4px solid #FFD700'] * len(row)
                    elif 'vcp' in setup:
                        return ['background-color: rgba(184, 38, 255, 0.15); color: #E066FF; font-weight: bold; border-left: 4px solid #E066FF'] * len(row)
                    elif 'ema' in setup:
                        return ['background-color: rgba(0, 191, 255, 0.15); color: #00BFFF; font-weight: bold; border-left: 4px solid #00BFFF'] * len(row)
                    elif 'BUY' in signal:
                        return ['background-color: rgba(0, 255, 170, 0.05); color: #00FFAA; font-weight: bold; border-left: 4px solid #00FFAA'] * len(row)
                    elif 'WATCH' in signal:
                        return ['color: #FFB86C; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                
                return df.style.apply(highlight_rows, axis=1).format({
                    "Price": "₹{:.2f}",
                    "Entry": "₹{:.2f}",
                    "SL": "₹{:.2f}",
                    "Target1": "₹{:.2f}",
                    "Target2": "₹{:.2f}",
                    "VolSurge": "{:.2f}x",
                    "RR": "1:{:.1f}"
                })
            
            st.dataframe(
                style_dataframe(live_df),
                use_container_width=True, 
                height=500,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "AI Score",
                        help="Combined Technical & News Sentiment Score",
                        format="%d",
                        min_value=0,
                        max_value=100,
                    ),
                    "Stock": st.column_config.TextColumn("Ticker", width="medium")
                }
            )
            
        except Exception as e:
            st.error(f"Error rendering table: {e}")
    else:
        st.info("Awaiting daily scan data. `scanner_data.csv` not found.")

# ==========================================
# TAB 2: PERFORMANCE & RISK LEDGER
# ==========================================
with tab_performance:
    st.markdown("### 📈 Portfolio & Risk Ledger")
    
    raw_history = load_json_history("performance_history.json")
    
    if raw_history.empty:
        st.warning("No historical execution records found.")
    else:
        score_key = next((c for c in raw_history.columns if 'score' in c.lower()), None)
        if score_key:
            clean_scores = raw_history[score_key].astype(str).str.extract(r'(\d+(?:\.\d+)?)', expand=False)
            numeric_scores = pd.to_numeric(clean_scores, errors='coerce').fillna(0.0)
            history_df = raw_history[numeric_scores >= float(min_score_filter)].copy()
        else:
            history_df = raw_history.copy()
            
        status_key = next((c for c in history_df.columns if 'status' in c.lower()), None)
        if status_key:
            valid_mask = history_df[status_key].astype(str).str.contains(
                'ACTIVE|HIT|CLOSED|EXIT|TARGET|SL', case=False, regex=True, na=False
            )
            history_df = history_df[valid_mask].copy()

        # Simulate Sizing & Portfolio Dynamics
        current_corpus = total_corpus
        ledger = []
        chart_data = [{"Date": "Start", "Corpus": total_corpus}]

        for idx, row in history_df.iterrows():
            entry = safe_float(row.get("Entry", row.get("entry")), 0.0)
            sl = safe_float(row.get("SL", row.get("Stoploss", row.get("sl"))), entry * 0.98)
            target = safe_float(row.get("Target", row.get("target")), entry * 1.04)
            actual_exit = safe_float(row.get("Exit Price", row.get("Exit", row.get("exit"))), entry)
            contract_lot = max(1, int(safe_float(row.get("Lot Size", row.get("lot_size")), 1)))
            date_val = row.get("Date", row.get("date", f"Trade #{idx+1}"))
            status_val = str(row.get(status_key, "ACTIVE") if status_key else "ACTIVE")

            if entry <= 0: continue

            risk_per_share = abs(entry - sl)
            reward_per_share = abs(target - entry)
            rr_ratio = (reward_per_share / risk_per_share) if risk_per_share > 0 else 0.0

            max_risk_allowed = current_corpus * risk_pct
            qty_by_risk = int(max_risk_allowed / risk_per_share) if risk_per_share > 0 else 0
            qty_by_capital = int(max_trade_capital / entry) if entry > 0 else 0
            
            allowed_qty = min(qty_by_risk, qty_by_capital)
            num_lots = allowed_qty // contract_lot
            executed_qty = num_lots * contract_lot
            
            deployed_capital = executed_qty * entry
            
            closed = is_trade_closed(status_val)
            if closed:
                raw_pnl = executed_qty * (actual_exit - entry)
                actual_pnl = max(raw_pnl, -max_risk_allowed)
                current_corpus += actual_pnl
            else:
                actual_pnl = 0.0

            row_record = row.to_dict()
            row_record.update({
                "R:R Ratio": f"1:{rr_ratio:.2f}",
                "Lots": num_lots,
                "Qty": executed_qty,
                "Capital": deployed_capital,
                "Net PnL": actual_pnl,
                "Updated Corpus": current_corpus,
                "Is Closed": closed
            })
            ledger.append(row_record)
            if closed:
                chart_data.append({"Date": str(date_val), "Corpus": current_corpus})

        df_ledger = pd.DataFrame(ledger)
        df_chart = pd.DataFrame(chart_data)

        # KPIs
        total_pnl = current_corpus - total_corpus
        pnl_pct = (total_pnl / total_corpus) * 100

        if not df_ledger.empty:
            closed_trades = df_ledger[df_ledger["Is Closed"] == True]
            active_trades = df_ledger[df_ledger["Is Closed"] == False]
            total_closed = len(closed_trades)
            total_active = len(active_trades)

            if total_closed > 0:
                wins = closed_trades[closed_trades["Net PnL"] > 0]
                losses = closed_trades[closed_trades["Net PnL"] < 0]
                win_rate = len(wins) / total_closed
            else:
                win_rate = 0.0
        else:
            total_closed = total_active = win_rate = 0.0

        # KPI Render
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("Active Capital", f"₹{current_corpus:,.2f}", f"{pnl_pct:+.2f}%")
        kpi_col2.metric("Total Net Profit", f"₹{total_pnl:,.2f}")
        kpi_col3.metric("System Win Rate", f"{win_rate * 100:.1f}%")
        kpi_col4.metric("Live Positions", f"{total_active} Active", f"{total_closed} Closed", delta_color="off")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Ledger Table
        if not df_ledger.empty:
            def color_pnl_text(val):
                if val > 0: return 'color: #00FFAA; font-weight: bold;'
                elif val < 0: return 'color: #FF4444; font-weight: bold;'
                return 'color: #888888;'

            display_df = df_ledger.drop(columns=["Is Closed", "Symbol", "Date", "T1_Hit"], errors="ignore")
            
            st.dataframe(
                display_df.style.map(color_pnl_text, subset=['Net PnL']).format({
                    "Entry": "₹{:.2f}", "Target1": "₹{:.2f}", "Target2": "₹{:.2f}", "Target": "₹{:.2f}",
                    "SL": "₹{:.2f}", "Exit Price": "₹{:.2f}", "Capital": "₹{:,.2f}", 
                    "Net PnL": "₹{:,.2f}", "Updated Corpus": "₹{:,.2f}"
                }),
                use_container_width=True, 
                height=350
            )

        st.markdown("---")
        
        if HAS_PLOTLY and len(df_chart) > 1:
            fig1 = px.line(df_chart, x="Date", y="Corpus", title="Equity Curve")
            fig1.update_traces(line_color="#00FFAA", line_width=3, marker=dict(size=8, color="#00FFAA"))
            fig1.add_hline(y=total_corpus, line_dash="dash", line_color="#888888", annotation_text="Starting Capital")
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'), yaxis_title="Account Balance (₹)",
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#2D303E')
            )
            st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# TAB 3: SHADOW WATCHLIST
# ==========================================
with tab_shadow:
    st.markdown("### 🛡️ AI Veto Ledger")
    st.caption("Trades rejected by the Bear Agent or Judge for low sentiment, high RSI, or high risk. Margins set to ₹0.")
    
    if not raw_history.empty and status_key:
        shadow_df = raw_history[raw_history[status_key].astype(str).str.contains('WATCH|VETO|SHADOW|REJECT', case=False, na=False)]
        if not shadow_df.empty:
            st.dataframe(
                shadow_df.style.format({"Entry": "₹{:.2f}", "Target1": "₹{:.2f}", "Target2": "₹{:.2f}", "SL": "₹{:.2f}"}),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No vetoed setups currently in the shadow ledger.")
    else:
        st.info("No shadow data available.")