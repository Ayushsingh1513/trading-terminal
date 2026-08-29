import json
import os

import pandas as pd
import streamlit as st
import yfinance as yf

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(
    page_title="Intraday Sector Tape",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0B0E14; color: #E2E8F0; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="metric-container"] {
        background-color: #131822;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 15px 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #F8FAFC !important;
        border-bottom: 2px solid #00FFAA !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


def safe_float(val, default=0.0):
    if pd.isna(val) or val in ["", None, "None", "nan"]:
        return default
    try:
        return float(val)
    except Exception:
        return default


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
        if isinstance(data, dict):
            max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
            padded = {
                k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len)
                for k, v in data.items()
            }
            return pd.DataFrame(padded)
    except Exception:
        pass
    return pd.DataFrame()


def load_market():
    if not os.path.exists("market_data.json"):
        return {}
    try:
        with open("market_data.json") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            return raw
    except Exception:
        pass
    return {}


with st.sidebar:
    st.title("Sector Tape")
    st.caption("Intraday · sector first · opening range")
    st.markdown("---")
    st.subheader("Sizing")
    fixed_rupee_risk = st.number_input("Max risk per trade (Rs)", value=400.0, step=100.0, format="%.2f")
    max_trade_capital = st.number_input("Max margin (Rs)", value=50000.0, step=5000.0, format="%.2f")
    st.markdown("---")
    st.info("Scan runs \~09:45 IST on weekdays. Longs only from BULLISH sectors. Flat by 15:10.")

tab_scanner, tab_pnl, tab_shadow = st.tabs(
    ["Live tape", "Trade history", "Watchlist"]
)

with tab_scanner:
    mkt = load_market()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nifty", f"{safe_float(mkt.get('nifty')):,.0f}", f"{safe_float(mkt.get('nifty_ret')):+.2f}%")
    c2.metric("Mood", mkt.get("mood", "—"))
    c3.metric("Bullish sectors", mkt.get("bullish_sectors") or "none")
    c4.metric("As of", mkt.get("as_of", "—"))

    st.markdown("### Sector scorecard")
    st.caption("Bias from opening drive vs Nifty, breadth (% of names green), and VWAP.")
    if os.path.exists("sector_data.csv"):
        sec_df = pd.read_csv("sector_data.csv")
        if sec_df.empty:
            st.warning("Sector file is empty. Run `python intraday_scanner.py` or wait for the 09:45 job.")
        else:
            def color_bias(val):
                v = str(val).upper()
                if v == "BULLISH":
                    return "background-color: rgba(0,255,170,0.12); color: #00FFAA; font-weight: 600"
                if v == "WEAK":
                    return "background-color: rgba(255,68,68,0.12); color: #FF6B6B; font-weight: 600"
                return "background-color: rgba(100,116,139,0.12); color: #94A3B8"

            st.dataframe(
                sec_df.style.map(color_bias, subset=["Bias"]).format(
                    {"ReturnPct": "{:+.2f}%", "VsNifty": "{:+.2f}", "Breadth": "{:.0f}%", "Last": "{:.2f}", "VWAP": "{:.2f}"}
                ),
                use_container_width=True,
                hide_index=True,
                height=320,
            )
    else:
        st.info("No sector_data.csv yet.")

    st.markdown("### Stock setups (from bullish sectors only)")
    if os.path.exists("scanner_data.csv"):
        live_df = pd.read_csv("scanner_data.csv")
        if live_df.empty:
            st.success("No long setups — stand aside. That is a valid output.")
        else:
            stock_list = live_df["Stock"].tolist()
            selected_stock = st.selectbox("Inspect", stock_list)
            stock_row = live_df[live_df["Stock"] == selected_stock].iloc[0]

            col_chart, col_ticket = st.columns([1.4, 1])
            with col_chart:
                st.markdown(f"#### {selected_stock}")
                hist_df = yf.Ticker(selected_stock).history(period="5d", interval="5m")
                if hist_df.empty:
                    hist_df = yf.Ticker(selected_stock).history(period="5d")
                if not hist_df.empty and HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(
                        go.Candlestick(
                            x=hist_df.index,
                            open=hist_df["Open"],
                            high=hist_df["High"],
                            low=hist_df["Low"],
                            close=hist_df["Close"],
                            name="Price",
                            increasing_line_color="#00FFAA",
                            decreasing_line_color="#FF4444",
                        )
                    )
                    entry_p = safe_float(stock_row.get("Entry"))
                    sl_p = safe_float(stock_row.get("SL"))
                    t1_p = safe_float(stock_row.get("Target1"))
                    t2_p = safe_float(stock_row.get("Target2"))
                    orh = safe_float(stock_row.get("ORHigh"))
                    orl = safe_float(stock_row.get("ORLow"))
                    if entry_p:
                        fig.add_hline(y=entry_p, line_dash="dash", line_color="#00FFAA", annotation_text=f"Entry {entry_p}")
                    if sl_p:
                        fig.add_hline(y=sl_p, line_dash="solid", line_color="#FF4444", annotation_text=f"SL {sl_p}")
                    if t1_p:
                        fig.add_hline(y=t1_p, line_dash="dot", line_color="#3B82F6", annotation_text=f"T1 {t1_p}")
                    if t2_p:
                        fig.add_hline(y=t2_p, line_dash="dash", line_color="#64748B", annotation_text=f"T2 {t2_p}")
                    if orh:
                        fig.add_hline(y=orh, line_dash="dot", line_color="#94A3B8", annotation_text="OR high")
                    if orl:
                        fig.add_hline(y=orl, line_dash="dot", line_color="#94A3B8", annotation_text="OR low")
                    fig.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="#131822",
                        paper_bgcolor="#131822",
                        margin=dict(l=10, r=10, t=20, b=10),
                        height=420,
                        xaxis_rangeslider_visible=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not render chart.")

            with col_ticket:
                e = safe_float(stock_row.get("Entry"))
                s = safe_float(stock_row.get("SL"))
                st.markdown(f"**{stock_row.get('Setup')}** · {stock_row.get('Sector')}")
                st.write(
                    f"Entry Rs {e:,.2f}  \n"
                    f"SL (OR low) Rs {s:,.2f}  \n"
                    f"T1 (2R) Rs {safe_float(stock_row.get('Target1')):,.2f}  \n"
                    f"T2 (3R) Rs {safe_float(stock_row.get('Target2')):,.2f}  \n"
                    f"RVOL {stock_row.get('VolSurge')}x  ·  vs sector {stock_row.get('VsSector')}%"
                )
                if e > s > 0:
                    risk_ps = e - s
                    calc_qty = int(fixed_rupee_risk / risk_ps)
                    max_cap_qty = int(max_trade_capital / e)
                    final_qty = max(1, min(calc_qty, max_cap_qty))
                    st.markdown(
                        f"""
<div style="background:#1E293B;padding:14px;border-radius:8px;border-left:4px solid #00FFAA;">
Buy <b>{final_qty}</b> shares at Rs {e:,.2f}.<br>
Margin Rs {final_qty * e:,.0f}. If stopped: <b>Rs {final_qty * risk_ps:,.0f}</b>.<br>
<span style="color:#94A3B8">Skip if the next bar gaps through the stop. Exit by 15:10.</span>
</div>
""",
                        unsafe_allow_html=True,
                    )

            show_cols = [
                c
                for c in [
                    "Stock",
                    "Setup",
                    "Sector",
                    "Score",
                    "Price",
                    "Entry",
                    "SL",
                    "Target1",
                    "Target2",
                    "RR",
                    "VolSurge",
                    "VsSector",
                    "Qty",
                    "RiskRs",
                ]
                if c in live_df.columns
            ]
            st.dataframe(live_df[show_cols], use_container_width=True, hide_index=True, height=260)
    else:
        st.info("Awaiting first scan. `scanner_data.csv` is missing.")

raw_history = load_json_history("performance_history.json")

with tab_pnl:
    st.markdown("### Execution history")
    if raw_history.empty:
        st.info("No ledger yet.")
    else:
        valid_df = raw_history[
            raw_history["Status"].astype(str).str.contains("ACTIVE|CLOSED|HIT|EXIT", case=False, na=False)
        ]
        st.dataframe(valid_df, use_container_width=True, height=400)

with tab_shadow:
    st.markdown("### Watchlist / veto")
    if raw_history.empty:
        st.info("Empty.")
    else:
        veto_df = raw_history[
            raw_history["Status"].astype(str).str.contains("WATCHLIST|VETO", case=False, na=False)
        ]
        if veto_df.empty:
            st.info("Nothing parked.")
        else:
            st.dataframe(veto_df, use_container_width=True, height=400)