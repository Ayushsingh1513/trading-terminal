import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Momentum Frenzy | Terminal", layout="wide", page_icon="⚡")

# --- 2. SIDEBAR RISK CONTROLS ---
with st.sidebar:
    st.title("⚡ Momentum Frenzy")
    st.header("Risk Engine Parameters")
    
    total_corpus = st.number_input("Starting Corpus (₹)", value=100000.0, step=10000.0)
    max_trade_capital = st.number_input("Max Allocation / Trade (₹)", value=50000.0, step=5000.0)
    risk_pct = st.slider("Max Risk / Trade (%)", 0.5, 5.0, 1.0, 0.1) / 100
    
    st.markdown("---")
    st.info("Adjusting parameters updates position sizing, lot counts, and corpus growth across historical trades.")

# --- 3. DATA LOADER ---
@st.cache_data(ttl=60)
def load_trade_history():
    # Primary source: performance_history.json
    if os.path.exists("performance_history.json"):
        try:
            with open("performance_history.json", "r") as f:
                data = json.load(f)
                if data:
                    return pd.DataFrame(data)
        except Exception:
            pass
            
    # Fallback source: scanner_data.csv
    if os.path.exists("scanner_data.csv"):
        try:
            df = pd.read_csv("scanner_data.csv")
            if not df.empty:
                return df
        except Exception:
            pass
            
    # Default fallback data if files are empty/missing
    return pd.DataFrame([
        {"trade_id": 1, "date": "2026-08-01", "symbol": "RELIANCE", "entry": 2500.0, "sl": 2450.0, "target": 2600.0, "exit": 2600.0, "lot_size": 1},
        {"trade_id": 2, "date": "2026-08-02", "symbol": "TATASTEEL", "entry": 150.0, "sl": 145.0, "target": 165.0, "exit": 145.0, "lot_size": 1},
        {"trade_id": 3, "date": "2026-08-05", "symbol": "NIFTY_FUT", "entry": 24000.0, "sl": 23960.0, "target": 24120.0, "exit": 24120.0, "lot_size": 25},
    ])

raw_df = load_trade_history()

# --- 4. SEQUENTIAL RISK & POSITION SIZING ENGINE ---
current_corpus = total_corpus
ledger = []
chart_data = [{"Date": "Start", "Corpus": total_corpus}]

if not raw_df.empty:
    for idx, row in raw_df.iterrows():
        trade_id = row.get("trade_id", idx + 1)
        date = row.get("date", f"Trade #{idx + 1}")
        symbol = str(row.get("symbol", "UNKNOWN"))
        entry = float(row.get("entry", 0))
        sl = float(row.get("sl", entry * 0.98))
        target = float(row.get("target", entry * 1.04))
        actual_exit = float(row.get("exit", entry))
        contract_lot = int(row.get("lot_size", 1))
        
        if entry <= 0:
            continue

        # Points & R:R Ratio
        risk_per_share = abs(entry - sl)
        reward_per_share = abs(target - entry)
        rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        # Max Allowed Risk (1% of current active corpus = ₹1,000 baseline)
        max_risk_allowed = current_corpus * risk_pct
        
        # Quantity capping rules
        qty_allowed_by_risk = int(max_risk_allowed / risk_per_share) if risk_per_share > 0 else 0
        qty_allowed_by_capital = int(max_trade_capital / entry)
        
        # Final selected quantity & lot sizing
        max_qty = min(qty_allowed_by_risk, qty_allowed_by_capital)
        number_of_lots = max_qty // contract_lot if contract_lot > 0 else 0
        executed_qty = number_of_lots * contract_lot
        
        # Capital Deployment & PnL
        capital_deployed = executed_qty * entry
        actual_pnl = executed_qty * (actual_exit - entry)
        
        # Enforce max stop loss cap
        actual_pnl = max(actual_pnl, -max_risk_allowed)
        
        # Corpus update
        current_corpus += actual_pnl
        remaining_funds = current_corpus - capital_deployed
        
        ledger.append({
            "ID": trade_id,
            "Date": date,
            "Symbol": symbol,
            "Entry": entry,
            "SL": sl,
            "Target": target,
            "R:R": f"1:{rr_ratio:.2f}",
            "Lots": number_of_lots,
            "Qty": executed_qty,
            "Deployed Capital": capital_deployed,
            "Trade PnL": actual_pnl,
            "Updated Corpus": current_corpus,
            "Available Funds": remaining_funds
        })
        chart_data.append({"Date": str(date), "Corpus": current_corpus})

df_ledger = pd.DataFrame(ledger)
df_chart = pd.DataFrame(chart_data)

# --- 5. UI DISPLAY ---
st.title("Momentum Frenzy | Risk & Performance Ledger")

col1, col2, col3, col4 = st.columns(4)
total_pnl = current_corpus - total_corpus
pnl_pct = (total_pnl / total_corpus) * 100
win_count = len(df_ledger[df_ledger["Trade PnL"] > 0]) if not df_ledger.empty else 0
win_rate = (win_count / len(df_ledger)) * 100 if not df_ledger.empty else 0

col1.metric("Current Corpus", f"₹{current_corpus:,.2f}", f"{pnl_pct:+.2f}%")
col2.metric("Total Net PnL", f"₹{total_pnl:,.2f}")
col3.metric("Win Rate", f"{win_rate:.1f}%")
col4.metric("Trades Executed", f"{len(df_ledger)}")

st.markdown("---")

# Growth Curve
st.subheader("Account Growth Curve")
fig = px.line(df_chart, x="Date", y="Corpus", markers=True)
fig.update_traces(line_color="#00FFAA", marker=dict(size=8))
fig.add_hline(y=total_corpus, line_dash="dash", line_color="#FF4444", annotation_text="Initial Capital")
fig.update_layout(yaxis_title="Corpus Balance (₹)", height=350)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Trade Ledger
st.subheader("Sequential Trade Ledger")
if not df_ledger.empty:
    styled_df = df_ledger.style.format({
        "Entry": "₹{:,.2f}",
        "SL": "₹{:,.2f}",
        "Target": "₹{:,.2f}",
        "Deployed Capital": "₹{:,.2f}",
        "Trade PnL": "₹{:,.2f}",
        "Updated Corpus": "₹{:,.2f}",
        "Available Funds": "₹{:,.2f}",
    }).map(lambda x: 'color: #00FF00' if x > 0 else ('color: #FF4444' if x < 0 else ''), subset=['Trade PnL'])
    st.dataframe(styled_df, use_container_width=True, height=380)
else:
    st.warning("No historical trade records found.")