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
    page_title="Sector Tape",
    layout="wide",
    page_icon="■",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
    .stApp { background: #050608; color: #d4d6db; }
    .block-container { padding: 1rem 1.5rem 2rem; max-width: 1400px; }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    section[data-testid="stSidebar"] {
        background: #0a0b0e; border-right: 1px solid #1c1e24;
    }

    .topbar {
        display: flex; align-items: baseline; gap: 1.25rem;
        padding: 0.25rem 0 1rem; border-bottom: 1px solid #1c1e24;
        margin-bottom: 1.25rem;
    }
    .topbar-title {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700; font-size: 0.95rem;
        letter-spacing: 0.12em; text-transform: uppercase; color: #f0f1f3;
    }
    .topbar-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: #6b6e78;
    }
    .pill {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem; font-weight: 600;
        letter-spacing: 0.08em; text-transform: uppercase;
        padding: 3px 8px; border-radius: 3px;
    }
    .pill-up { background: #0f2a1c; color: #3ecf8e; }
    .pill-dn { background: #2a0f0f; color: #f07178; }
    .pill-flat { background: #1a1c22; color: #8b8e98; }

    .strip {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
        margin-bottom: 1.25rem;
    }
    .strip-cell {
        background: #0d0e12; border: 1px solid #1c1e24;
        border-radius: 4px; padding: 12px 14px;
    }
    .strip-label {
        font-size: 0.62rem; text-transform: uppercase;
        letter-spacing: 0.1em; color: #6b6e78; margin-bottom: 4px;
    }
    .strip-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem; font-weight: 600; color: #f0f1f3;
    }
    .strip-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: #6b6e78; margin-top: 2px;
    }
    .up { color: #3ecf8e !important; }
    .dn { color: #f07178 !important; }

    .sec-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 8px; margin-bottom: 1.5rem;
    }
    .sec-card {
        background: #0d0e12; border: 1px solid #1c1e24;
        border-radius: 4px; padding: 10px 12px; border-top: 2px solid #1c1e24;
    }
    .sec-card.bull { border-top-color: #3ecf8e; }
    .sec-card.weak { border-top-color: #f07178; }
    .sec-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; font-weight: 600;
        letter-spacing: 0.06em; text-transform: uppercase;
        color: #a0a3ab; margin-bottom: 6px;
    }
    .sec-ret {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem; font-weight: 600;
    }
    .sec-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem; color: #6b6e78; margin-top: 4px;
    }

    .setup {
        background: #0d0e12; border: 1px solid #1c1e24;
        border-radius: 4px; padding: 14px 16px; margin-bottom: 10px;
        display: grid; grid-template-columns: 100px 1fr auto;
        gap: 16px; align-items: center;
    }
    .setup.buy { border-left: 3px solid #3ecf8e; }
    .setup.sell { border-left: 3px solid #f07178; }
    .setup-side {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
    }
    .setup-side.buy { color: #3ecf8e; }
    .setup-side.sell { color: #f07178; }
    .setup-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem; font-weight: 600; color: #f0f1f3;
    }
    .setup-sub { font-size: 0.72rem; color: #6b6e78; margin-top: 2px; }
    .setup-levels {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: #a0a3ab;
        text-align: right; line-height: 1.55;
    }
    .setup-levels b { color: #f0f1f3; font-weight: 600; }

    .section-h {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.14em; text-transform: uppercase;
        color: #6b6e78; margin: 0 0 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; border-bottom: 1px solid #1c1e24; background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 36px; background: transparent; color: #6b6e78;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; font-weight: 500;
        letter-spacing: 0.08em; text-transform: uppercase;
        border-radius: 0; padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #f0f1f3 !important;
        border-bottom: 2px solid #3ecf8e !important;
        background: transparent !important;
    }
    .stSelectbox label { display: none; }
    .empty {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem; color: #6b6e78;
        padding: 24px; text-align: center;
        border: 1px dashed #1c1e24; border-radius: 4px;
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
    st.markdown("**Risk**")
    fixed_rupee_risk = st.number_input("INR risk / trade", value=400.0, step=100.0, format="%.0f")
    max_trade_capital = st.number_input("INR max margin", value=50000.0, step=5000.0, format="%.0f")
    st.caption("Long + short · 0.4% corpus · max 2 · 1/sector · flat 15:10")

mkt = load_market()
nifty = safe_float(mkt.get("nifty"))
nret = safe_float(mkt.get("nifty_ret"))
mood = str(mkt.get("mood") or "—")
as_of = mkt.get("as_of") or "—"
ret_cls = "up" if nret >= 0 else "dn"
mood_pill = (
    "pill-up" if mood.upper() == "BULLISH"
    else ("pill-dn" if mood.upper() in ("HEAVY", "BEARISH") else "pill-flat")
)

st.markdown(
    f"""
    <div class="topbar">
      <div class="topbar-title">Sector Tape</div>
      <span class="pill {mood_pill}">{mood}</span>
      <div class="topbar-meta">{as_of}</div>
    </div>
    <div class="strip">
      <div class="strip-cell">
        <div class="strip-label">Nifty</div>
        <div class="strip-val">{nifty:,.0f}</div>
        <div class="strip-sub {ret_cls}">{nret:+.2f}%</div>
      </div>
      <div class="strip-cell">
        <div class="strip-label">Long sectors</div>
        <div class="strip-val" style="font-size:0.85rem">{mkt.get('bullish_sectors') or '—'}</div>
      </div>
      <div class="strip-cell">
        <div class="strip-label">Short sectors</div>
        <div class="strip-val" style="font-size:0.85rem">{mkt.get('weak_sectors') or '—'}</div>
      </div>
      <div class="strip-cell">
        <div class="strip-label">Bias</div>
        <div class="strip-val" style="font-size:0.95rem">{mood}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_tape, tab_hist, tab_watch = st.tabs(["Tape", "History", "Watchlist"])

with tab_tape:
    st.markdown('<p class="section-h">Sector map</p>', unsafe_allow_html=True)

    if os.path.exists("sector_data.csv"):
        sec_df = pd.read_csv("sector_data.csv")
        if sec_df.empty:
            st.markdown('<div class="empty">No sector data — run scanner</div>', unsafe_allow_html=True)
        else:
            cards = []
            for _, r in sec_df.iterrows():
                bias = str(r.get("Bias", "")).upper()
                cls = "bull" if bias == "BULLISH" else ("weak" if bias == "WEAK" else "")
                ret = safe_float(r.get("ReturnPct"))
                ret_c = "up" if ret >= 0 else "dn"
                vs = safe_float(r.get("VsNifty"))
                br = int(safe_float(r.get("Breadth")))
                cards.append(
                    f"""
                    <div class="sec-card {cls}">
                      <div class="sec-name">{r.get('Sector')}</div>
                      <div class="sec-ret {ret_c}">{ret:+.2f}%</div>
                      <div class="sec-meta">vsN {vs:+.2f} · br {br}%</div>
                      <div class="sec-meta">{bias}</div>
                    </div>
                    """
                )
            st.markdown(f'<div class="sec-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty">sector_data.csv missing</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-h">Setups · long + short</p>', unsafe_allow_html=True)

    if os.path.exists("scanner_data.csv"):
        live_df = pd.read_csv("scanner_data.csv")
        if live_df.empty:
            st.markdown('<div class="empty">No setups — stand aside</div>', unsafe_allow_html=True)
        else:
            rows_html = []
            for _, t in live_df.iterrows():
                sig = str(t.get("Signal", "BUY")).upper()
                side = "buy" if sig == "BUY" else "sell"
                side_label = "LONG" if side == "buy" else "SHORT"
                name = str(t.get("Stock", "")).replace(".NS", "")
                rows_html.append(
                    f"""
                    <div class="setup {side}">
                      <div>
                        <div class="setup-side {side}">{side_label}</div>
                        <div class="setup-sub">{t.get('Setup')}</div>
                      </div>
                      <div>
                        <div class="setup-name">{name}</div>
                        <div class="setup-sub">{t.get('Sector')} · RVOL {t.get('VolSurge')}x · score {t.get('Score')}</div>
                      </div>
                      <div class="setup-levels">
                        Entry <b>INR {safe_float(t.get('Entry')):,.2f}</b><br>
                        SL <b>INR {safe_float(t.get('SL')):,.2f}</b><br>
                        T1 INR {safe_float(t.get('Target1')):,.2f} · T2 INR {safe_float(t.get('Target2')):,.2f}<br>
                        Qty {int(safe_float(t.get('Qty')))} · risk INR {safe_float(t.get('RiskRs')):,.0f}
                      </div>
                    </div>
                    """
                )
            st.markdown("".join(rows_html), unsafe_allow_html=True)

            st.markdown('<p class="section-h" style="margin-top:1.5rem">Inspect</p>', unsafe_allow_html=True)
            stock_list = live_df["Stock"].tolist()
            selected = st.selectbox("stock", stock_list, label_visibility="collapsed")
            row = live_df[live_df["Stock"] == selected].iloc[0]
            sig = str(row.get("Signal", "BUY")).upper()

            col_c, col_t = st.columns([1.6, 1])
            with col_c:
                hist = yf.Ticker(selected).history(period="5d", interval="5m")
                if hist.empty:
                    hist = yf.Ticker(selected).history(period="5d")
                if not hist.empty and HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(
                        go.Candlestick(
                            x=hist.index,
                            open=hist["Open"],
                            high=hist["High"],
                            low=hist["Low"],
                            close=hist["Close"],
                            increasing_line_color="#3ecf8e",
                            decreasing_line_color="#f07178",
                            increasing_fillcolor="#3ecf8e",
                            decreasing_fillcolor="#f07178",
                        )
                    )
                    for y, color, label in [
                        (safe_float(row.get("Entry")), "#a0a3ab", "Entry"),
                        (safe_float(row.get("SL")), "#f07178", "SL"),
                        (safe_float(row.get("Target1")), "#3ecf8e", "T1"),
                        (safe_float(row.get("Target2")), "#6b6e78", "T2"),
                    ]:
                        if y:
                            fig.add_hline(
                                y=y, line_dash="dot", line_color=color, line_width=1,
                                annotation_text=label, annotation_font_size=10,
                            )
                    fig.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="#0d0e12",
                        paper_bgcolor="#0d0e12",
                        font=dict(family="JetBrains Mono", size=10, color="#6b6e78"),
                        margin=dict(l=4, r=4, t=8, b=4),
                        height=380,
                        xaxis_rangeslider_visible=False,
                        showlegend=False,
                        xaxis=dict(gridcolor="#15171c"),
                        yaxis=dict(gridcolor="#15171c", side="right"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_t:
                e = safe_float(row.get("Entry"))
                s = safe_float(row.get("SL"))
                risk_ps = abs(e - s) if e and s else 0
                if risk_ps > 0:
                    qty = max(1, min(int(fixed_rupee_risk / risk_ps), int(max_trade_capital / e)))
                else:
                    qty = int(safe_float(row.get("Qty")))
                action = "BUY" if sig == "BUY" else "SELL / SHORT"
                side_cls = "buy" if sig == "BUY" else "sell"
                st.markdown(
                    f"""
                    <div class="setup {side_cls}" style="grid-template-columns:1fr;display:block">
                      <div class="setup-side {side_cls}">{action}</div>
                      <div class="setup-name" style="margin:8px 0">{str(selected).replace('.NS','')}</div>
                      <div class="setup-levels" style="text-align:left">
                        Entry <b>INR {e:,.2f}</b><br>
                        SL <b>INR {s:,.2f}</b><br>
                        T1 <b>INR {safe_float(row.get('Target1')):,.2f}</b><br>
                        T2 <b>INR {safe_float(row.get('Target2')):,.2f}</b><br><br>
                        Size <b>{qty}</b> sh<br>
                        Margin INR {qty * e:,.0f}<br>
                        Risk INR {qty * risk_ps:,.0f}
                      </div>
                      <div class="setup-sub" style="margin-top:10px">MIS only · skip gap SL · flat 15:10</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown('<div class="empty">scanner_data.csv missing</div>', unsafe_allow_html=True)

raw_history = load_json_history("performance_history.json")

with tab_hist:
    if raw_history.empty:
        st.markdown('<div class="empty">No ledger</div>', unsafe_allow_html=True)
    else:
        valid = raw_history[
            raw_history["Status"].astype(str).str.contains("ACTIVE|CLOSED|HIT|EXIT", case=False, na=False)
        ]
        st.dataframe(valid, use_container_width=True, height=400, hide_index=True)

with tab_watch:
    if raw_history.empty:
        st.markdown('<div class="empty">Empty</div>', unsafe_allow_html=True)
    else:
        veto = raw_history[
            raw_history["Status"].astype(str).str.contains("WATCHLIST|VETO", case=False, na=False)
        ]
        if veto.empty:
            st.markdown('<div class="empty">Nothing parked</div>', unsafe_allow_html=True)
        else:
            st.dataframe(veto, use_container_width=True, height=400, hide_index=True)