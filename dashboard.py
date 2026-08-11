import os
import json
import pandas as pd
import streamlit as st

# Safe import for Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(page_title="Momentum Frenzy | Terminal", layout="wide", page_icon="⚡")

# --- SIDEBAR RISK CONTROLS ---
with st.sidebar:
    st.title("⚡ Momentum Frenzy")
    st.header("Risk Engine Parameters")
    
    total_corpus = st.number_input("Starting Corpus (₹)", value=100000.0, step=10000.0)
    max_trade_capital = st.number_input("Max Allocation / Trade (₹)", value=50000.0, step=5000.0)
    risk_pct = st.slider("Max Risk / Trade (%)", 0.5, 5.0, 1.0, 0.1) / 100.0
    
    st.markdown("---")
    st.info("Applies only to 100/100 Score trades in Performance History.")

# --- TABS LAYOUT ---
tab1, tab2 = st.tabs(["📊 Live Screener", "📈 Performance History (Risk Ledger)"])

# ==========================================
# TAB 1: YOUR LIVE SCREENER (OLD INTERFACE)
# ==========================================
with tab1:
    st.header("Live Market Scanner")
    st.write("*(Your existing live scanner, sector data, and websocket tables will load here just like they used to. You can paste your original scanner code here if it was separated.)*")
    
    if os.path.exists("scanner_data.csv"):
        try:
            live_df = pd.read_csv("scanner_data.csv")
            st.dataframe(live_df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load live scanner: {e}")

# ==========================================
# TAB 2: PERFORMANCE HISTORY (CORPUS TRACKER)
# ==========================================
with tab2:
    st.header("Historical Performance & Quantitative Growth")
    
    # 1. Load the old results with safe padding for uneven arrays
    history_df = pd.DataFrame()
    if os.path.exists("performance_history.json"):
        try:
            with open("performance_history.json", "r") as f:
                data = json.load(f)
            
            if data:
                if isinstance(data, dict):
                    try:
                        history_df = pd.DataFrame(data)
                    except ValueError:
                        max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
                        padded_data = {
                            k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len)
                            for k, v in data.items()
                        }
                        history_df = pd.DataFrame(padded_data)
                elif isinstance(data, list):
                    history_df = pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error loading history: {e}")
            
    if history_df.empty:
        st.warning("No historical data found in performance_history.json.")
    else:
        # 2. FILTER: Only take trades with a 100/100 Score
        score_col = next((col for col in history_df.columns if col.lower() == 'score'), None)
        if score_col:
            history_df = history_df[history_df[score_col].astype(str).str.contains('100', na=False)]
            st.success(f"Filtered to {len(history_df)} high-conviction trades (Score: 100/100).")
        else:
            st.warning("No 'Score' column found in your data. Processing all historical trades.")

        # 3. CORPUS ENGINE LOOP
        current_corpus = total_corpus
        ledger = []
        chart_data = [{"Date": "Start", "Corpus": total_corpus}]

        for idx, row in history_df.iterrows():
            entry = float(row.get("Entry", row.get("entry", 0)) or 0)
            sl = float(row.get("SL", row.get("Stoploss", row.get("sl", entry * 0.98))) or (entry * 0.98))
            target = float(row.get("Target", row.get("target", entry * 1.04)) or (entry * 1.04))
            actual_exit = float(row.get("Exit Price", row.get("Exit", row.get("exit", entry))) or entry)
            contract_lot = int(row.get("Lot Size", row.get("lot_size", 1)) or 1)
            date_val = row.get("Date", row.get("date", f"Trade #{idx}"))

            if entry <= 0:
                continue

            risk_per_share = abs(entry - sl)
            reward_per_share = abs(target - entry)
            rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0
            
            max_risk_allowed = current_corpus * risk_pct
            
            qty_allowed_by_risk = int(max_risk_allowed / risk_per_share) if risk_per_share > 0 else 0
            qty_allowed_by_capital = int(max_trade_capital / entry)
            
            max_qty = min(qty_allowed_by_risk, qty_allowed_by_capital)
            number_of_lots = max_qty // contract_lot if contract_lot > 0 else 0
            executed_qty = number_of_lots * contract_lot
            
            capital_deployed = executed_qty * entry
            actual_pnl = executed_qty * (actual_exit - entry)
            actual_pnl = max(actual_pnl, -max_risk_allowed) # Enforce stop loss
            
            current_corpus += actual_pnl
            
            new_row = row.to_dict()
            new_row.update({
                "R:R Ratio": f"1:{rr_ratio:.2f}",
                "Executed Lots": number_of_lots,
                "Total Qty": executed_qty,
                "Deployed Capital": capital_deployed,
                "Net PnL": actual_pnl,
                "Updated Corpus": current_corpus,
            })
            
            ledger.append(new_row)
            chart_data.append({"Date": str(date_val), "Corpus": current_corpus})

        # 4. ADVANCED MATH & DATAFRAMES
        df_ledger = pd.DataFrame(ledger)
        df_chart = pd.DataFrame(chart_data)
        
        # Calculate Drawdowns
        if not df_chart.empty:
            df_chart["Peak"] = df_chart["Corpus"].cummax()
            df_chart["Drawdown"] = df_chart["Corpus"] - df_chart["Peak"]
            df_chart["Drawdown_Pct"] = (df_chart["Drawdown"] / df_chart["Peak"]) * 100
        
        # --- KPIs ---
        total_pnl = current_corpus - total_corpus
        pnl_pct = (total_pnl / total_corpus) * 100
        
        if not df_ledger.empty:
            win_count = len(df_ledger[df_ledger["Net PnL"] > 0])
            total_trades = len(df_ledger)
            win_rate = win_count / total_trades
            loss_rate = 1.0 - win_rate
            
            winning_trades = df_ledger[df_ledger["Net PnL"] > 0]
            losing_trades = df_ledger[df_ledger["Net PnL"] < 0]
            
            avg_win = winning_trades["Net PnL"].mean() if not winning_trades.empty else 0.0
            avg_loss = abs(losing_trades["Net PnL"].mean()) if not losing_trades.empty else 0.0
            
            gross_profit = winning_trades["Net PnL"].sum() if not winning_trades.empty else 0.0
            gross_loss = abs(losing_trades["Net PnL"].sum()) if not losing_trades.empty else 0.0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
            
            expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
            
            max_dd_pct = df_chart["Drawdown_Pct"].min()
            max_dd_val = df_chart["Drawdown"].min()
        else:
            win_rate = expectancy = profit_factor = max_dd_pct = max_dd_val = 0.0
            total_trades = 0

        # --- RENDER KPI CARDS (2 ROWS) ---
        st.subheader("Quantitative System Metrics")
        
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
        row1_col1.metric("Current Corpus", f"₹{current_corpus:,.2f}", f"{pnl_pct:+.2f}%")
        row1_col2.metric("Total Net PnL", f"₹{total_pnl:,.2f}")
        row1_col3.metric("Win Rate", f"{win_rate * 100:.1f}%")
        row1_col4.metric("Trades Executed", f"{total_trades}")
        
        st.write("") # Spacing
        
        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
        exp_color = "normal" if expectancy >= 0 else "inverse"
        row2_col1.metric("Expectancy / Trade", f"₹{expectancy:,.2f}", delta="Per setup", delta_color=exp_color)
        row2_col2.metric("Profit Factor", f"{profit_factor:.2f}", delta="Gross Profit / Gross Loss", delta_color="off")
        row2_col3.metric("Max Drawdown (%)", f"{max_dd_pct:.2f}%", delta="Peak-to-Trough", delta_color="inverse")
        row2_col4.metric("Max Drawdown (₹)", f"₹{max_dd_val:,.2f}")

        st.markdown("---")

        # --- CHARTS ---
        st.subheader("Corpus Growth & Drawdown Analysis")
        
        if HAS_PLOTLY and not df_chart.empty and len(df_chart) > 1:
            col_chart1, col_chart2 = st.columns([2, 1]) # Split width for charts
            
            with col_chart1:
                # Main Growth Curve
                fig1 = px.line(df_chart, x="Date", y="Corpus", markers=True, title="Account Equity Curve")
                fig1.update_traces(line_color="#00FFAA", marker=dict(size=6))
                fig1.add_hline(y=total_corpus, line_dash="dash", line_color="#FF4444", annotation_text="Initial Capital")
                fig1.update_layout(yaxis_title="Corpus Balance (₹)", height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig1, use_container_width=True)
                
            with col_chart2:
                # Drawdown Underwater Chart
                fig2 = px.area(df_chart, x="Date", y="Drawdown_Pct", title="Underwater Drawdown (%)")
                fig2.update_traces(line_color="#FF4444", fillcolor="rgba(255, 68, 68, 0.3)")
                fig2.update_layout(yaxis_title="Drawdown %", height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig2, use_container_width=True)
                
        elif not df_chart.empty and len(df_chart) > 1:
            st.line_chart(df_chart.set_index("Date")[["Corpus"]], height=300)
        else:
            st.info("Not enough data to draw charts yet.")

        st.markdown("---")
        
        # --- LEDGER ---
        st.subheader("Combined Historical Trade Ledger")
        if not df_ledger.empty:
            format_dict = {
                "Deployed Capital": "₹{:,.2f}",
                "Net PnL": "₹{:,.2f}",
                "Updated Corpus": "₹{:,.2f}"
            }
            
            for col in ["Entry", "SL", "Target", "Exit Price", "Stoploss"]:
                if col in df_ledger.columns:
                    format_dict[col] = "₹{:,.2f}"
                    
            styled_df = df_ledger.style.format(format_dict).map(
                lambda x: 'color: #00FF00' if x > 0 else ('color: #FF4444' if x < 0 else ''), 
                subset=['Net PnL']
            )
            
            st.dataframe(styled_df, use_container_width=True, height=400)
        else:
            st.info("No trades matching the 100/100 Score filter were found. The ledger is currently empty.")