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

# Safe import for Alerts
try:
    from alert import send_trade_alert
    HAS_ALERTS = True
except ImportError:
    HAS_ALERTS = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Momentum Frenzy | Quantitative Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 8px;
        padding: 15px;
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
    if not os.path.exists(filepath):
        return pd.DataFrame()
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame()
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            try:
                return pd.DataFrame(data)
            except ValueError:
                max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
                padded = {
                    k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len)
                    for k, v in data.items()
                }
                return pd.DataFrame(padded)
    except Exception as e:
        st.error(f"Error reading {filepath}: {e}")
    return pd.DataFrame()

# --- SIDEBAR: RISK ENGINE CONTROLS ---
with st.sidebar:
    st.title("⚡ Momentum Frenzy")
    st.caption("Multi-Agent Quantitative Execution Engine")
    st.markdown("---")
    
    st.subheader("Risk Parameters")
    total_corpus = st.number_input("Starting Corpus (₹)", value=100000.0, step=10000.0, format="%.2f")
    max_trade_capital = st.number_input("Max Allocation / Trade (₹)", value=50000.0, step=5000.0, format="%.2f")
    risk_pct = st.slider("Risk Per Trade (%)", min_value=0.25, max_value=5.0, value=1.0, step=0.25) / 100.0
    
    st.markdown("---")
    min_score_filter = st.slider("Min Setup Score", min_value=50, max_value=100, value=100, step=5)
    
    st.markdown("---")
    st.subheader("Telegram Dispatcher")
    if HAS_ALERTS:
        if st.button("🔔 Send Test Alert", use_container_width=True):
            send_trade_alert(
                symbol="TEST_RELIANCE", 
                entry=2500.0, 
                sl=2450.0, 
                target=2600.0, 
                lot_size=50
            )
            st.success("Test signal dispatched.")
    else:
        st.warning("`alert.py` not detected. Alerts disabled.")

# --- TABS LAYOUT ---
tab_screener, tab_performance, tab_shadow = st.tabs([
    "📊 Live Market Scanner", 
    "📈 Risk Ledger & Performance", 
    "🛡️ Shadow Watchlist"
])

# ==========================================
# TAB 1: LIVE MARKET SCANNER
# ==========================================
with tab_screener:
    st.header("Live Scanner Universe")
    
    if os.path.exists("scanner_data.csv"):
        try:
            live_df = pd.read_csv("scanner_data.csv")
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("Scanned Symbols", len(live_df))
            
            score_col = next((c for c in live_df.columns if c.lower() == 'score'), None)
            if score_col:
                clean_sc = live_df[score_col].astype(str).str.extract(r'(\d+(?:\.\d+)?)', expand=False)
                num_sc = pd.to_numeric(clean_sc, errors='coerce').fillna(0.0)
                top_setups = live_df[num_sc >= 80]
                col_s2.metric("High Conviction (≥80)", len(top_setups))
            else:
                col_s2.metric("High Conviction", "N/A")
                
            vol_col = next((c for c in live_df.columns if 'volume' in c.lower() or 'volsurge' in c.lower()), None)
            if vol_col:
                vol_clean = pd.to_numeric(live_df[vol_col], errors='coerce').fillna(0)
                col_s3.metric("Volume Spikes", len(live_df[vol_clean > 1.5]))
            else:
                col_s3.metric("Volume Spikes", "N/A")
                
            col_s4.metric("Status", "Online", delta="Syncing Daily")

            st.markdown("---")
            
            search = st.text_input("Filter Tickers / Sectors", "")
            if search:
                live_df = live_df[live_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
                
            st.dataframe(live_df, use_container_width=True, height=450)
            
        except Exception as e:
            st.error(f"Error loading live scanner: {e}")
    else:
        st.info("`scanner_data.csv` not found. Awaiting daily scan data.")

# ==========================================
# TAB 2: PERFORMANCE & RISK LEDGER
# ==========================================
with tab_performance:
    st.header("Historical Trade Performance")
    
    raw_history = load_json_history("performance_history.json")
    
    if raw_history.empty:
        st.warning("No historical execution records found in `performance_history.json`.")
    else:
        # 1. Filter by Score Safely
        score_key = next((c for c in raw_history.columns if 'score' in c.lower()), None)
        if score_key:
            clean_scores = (
                raw_history[score_key]
                .astype(str)
                .str.extract(r'(\d+(?:\.\d+)?)', expand=False)
            )
            numeric_scores = pd.to_numeric(clean_scores, errors='coerce').fillna(0.0)
            history_df = raw_history[numeric_scores >= float(min_score_filter)].copy()
        else:
            history_df = raw_history.copy()
            
        # 2. Filter Valid Trades
        status_key = next((c for c in history_df.columns if 'status' in c.lower()), None)
        if status_key:
            valid_mask = history_df[status_key].astype(str).str.contains(
                'ACTIVE|HIT|CLOSED|EXIT|TARGET|SL', case=False, regex=True, na=False
            )
            history_df = history_df[valid_mask].copy()

        # 3. Simulate Sizing & Portfolio Dynamics
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

            if entry <= 0:
                continue

            risk_per_share = abs(entry - sl)
            reward_per_share = abs(target - entry)
            rr_ratio = (reward_per_share / risk_per_share) if risk_per_share > 0 else 0.0

            # Position Sizing
            max_risk_allowed = current_corpus * risk_pct
            qty_by_risk = int(max_risk_allowed / risk_per_share) if risk_per_share > 0 else 0
            qty_by_capital = int(max_trade_capital / entry) if entry > 0 else 0
            
            allowed_qty = min(qty_by_risk, qty_by_capital)
            num_lots = allowed_qty // contract_lot
            executed_qty = num_lots * contract_lot
            
            deployed_capital = executed_qty * entry
            
            # PnL Calculation
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
                "Executed Lots": num_lots,
                "Executed Qty": executed_qty,
                "Deployed Capital": deployed_capital,
                "Net PnL": actual_pnl,
                "Updated Corpus": current_corpus,
                "Is Closed": closed
            })
            ledger.append(row_record)
            
            if closed:
                chart_data.append({"Date": str(date_val), "Corpus": current_corpus})

        df_ledger = pd.DataFrame(ledger)
        df_chart = pd.DataFrame(chart_data)

        # 4. KPI Calculations
        if not df_chart.empty:
            df_chart["Peak"] = df_chart["Corpus"].cummax()
            df_chart["Drawdown"] = df_chart["Corpus"] - df_chart["Peak"]
            df_chart["Drawdown_Pct"] = (df_chart["Drawdown"] / df_chart["Peak"]) * 100

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
                loss_rate = 1.0 - win_rate
                
                avg_win = wins["Net PnL"].mean() if not wins.empty else 0.0
                avg_loss = abs(losses["Net PnL"].mean()) if not losses.empty else 0.0
                
                gross_profit = wins["Net PnL"].sum() if not wins.empty else 0.0
                gross_loss = abs(losses["Net PnL"].sum()) if not losses.empty else 0.0
                profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)
                
                expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
            else:
                win_rate = loss_rate = avg_win = avg_loss = profit_factor = expectancy = 0.0
                
            max_dd_pct = df_chart["Drawdown_Pct"].min() if not df_chart.empty else 0.0
            max_dd_val = df_chart["Drawdown"].min() if not df_chart.empty else 0.0
        else:
            total_closed = total_active = win_rate = profit_factor = expectancy = max_dd_pct = max_dd_val = 0.0

        # 5. Render KPIs
        st.subheader("Quantitative System Metrics")
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.metric("Current Corpus", f"₹{current_corpus:,.2f}", f"{pnl_pct:+.2f}%")
        kpi_col2.metric("Total Net PnL", f"₹{total_pnl:,.2f}")
        kpi_col3.metric("Win Rate", f"{win_rate * 100:.1f}%")
        kpi_col4.metric("Trades", f"{total_closed} Closed", f"{total_active} Active", delta_color="off")
        
        st.write("")
        kpi2_col1, kpi2_col2, kpi2_col3, kpi2_col4 = st.columns(4)
        exp_delta_col = "normal" if expectancy >= 0 else "inverse"
        kpi2_col1.metric("Expectancy / Trade", f"₹{expectancy:,.2f}", delta="Edge Per Setup", delta_color=exp_delta_col)
        kpi2_col2.metric("Profit Factor", f"{profit_factor:.2f}", delta="Gross Profit / Loss", delta_color="off")
        kpi2_col3.metric("Max Drawdown (%)", f"{max_dd_pct:.2f}%", delta="Peak-to-Trough", delta_color="inverse")
        kpi2_col4.metric("Max Drawdown (₹)", f"₹{max_dd_val:,.2f}")

        st.markdown("---")

        # 6. Render Charts
        st.subheader("Equity Curve & Drawdown Profile")
        if HAS_PLOTLY and len(df_chart) > 1:
            c_left, c_right = st.columns([2, 1])
            with c_left:
                fig1 = px.line(df_chart, x="Date", y="Corpus", markers=True, title="Portfolio Growth Curve")
                fig1.update_traces(line_color="#00FFAA", marker=dict(size=6))
                fig1.add_hline(y=total_corpus, line_dash="dash", line_color="#FF4444", annotation_text="Initial Capital")
                fig1.update_layout(yaxis_title="Corpus (₹)", height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig1, use_container_width=True)
            with c_right:
                fig2 = px.area(df_chart, x="Date", y="Drawdown_Pct", title="Underwater Drawdown (%)")
                fig2.update_traces(line_color="#FF4444", fillcolor="rgba(255, 68, 68, 0.25)")
                fig2.update_layout(yaxis_title="Drawdown %", height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig2, use_container_width=True)
        elif len(df_chart) > 1:
            st.line_chart(df_chart.set_index("Date")[["Corpus"]], height=300)
        else:
            st.info("Execute and close at least one trade to plot performance charts.")

        st.markdown("---")

        # 7. Render Ledger Table
        st.subheader("Trade Execution Ledger")
        if not df_ledger.empty:
            format_rules = {
                "Deployed Capital": "₹{:,.2f}",
                "Net PnL": "₹{:,.2f}",
                "Updated Corpus": "₹{:,.2f}"
            }
            for col in ["Entry", "entry", "SL", "sl", "Stoploss", "Target", "target", "Exit Price", "Exit", "exit"]:
                if col in df_ledger.columns:
                    format_rules[col] = "₹{:,.2f}"

            def color_pnl(val):
                if val > 0:
                    return 'color: #00FF66; font-weight: bold;'
                elif val < 0:
                    return 'color: #FF4D4D; font-weight: bold;'
                return ''

            display_df = df_ledger.drop(columns=["Is Closed"], errors="ignore")
            styled_table = display_df.style.format(format_rules).map(color_pnl, subset=['Net PnL'])
            st.dataframe(styled_table, use_container_width=True, height=400)

# ==========================================
# TAB 3: SHADOW WATCHLIST
# ==========================================
with tab_shadow:
    st.header("Shadow Watchlist (AI Vetoed / Watch Setups)")
    st.caption("Trades rejected by the Bear Agent or Judge for low sentiment, high RSI, or high risk.")
    
    if not raw_history.empty:
        status_k = next((c for c in raw_history.columns if 'status' in c.lower()), None)
        if status_k:
            shadow_df = raw_history[raw_history[status_k].astype(str).str.contains('WATCH|VETO|SHADOW|REJECT', case=False, na=False)]
            if not shadow_df.empty:
                st.dataframe(shadow_df, use_container_width=True)
            else:
                st.info("No vetoed setups currently in the shadow ledger.")
        else:
            st.info("Status field not found in records.")
    else:
        st.info("No shadow data available.")