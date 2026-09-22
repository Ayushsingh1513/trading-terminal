import json
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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

components.html(
    """
    <script>
      setTimeout(function () { window.parent.location.reload(); }, 45000);
    </script>
    """,
    height=0,
    width=0,
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
        display: flex; align-items: baseline; gap: 1.25rem; flex-wrap: wrap;
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
        display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px;
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
        font-size: 1.05rem; font-weight: 600; color: #f0f1f3;
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
        display: grid; grid-template-columns: 100px 1fr auto auto;
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
    .conf {
        font-family: 'JetBrains Mono', monospace;
        text-align: right;
    }
    .conf-n {
        font-size: 1.2rem; font-weight: 700;
    }
    .conf-l { font-size: 0.6rem; letter-spacing: 0.1em; color: #6b6e78; text-transform: uppercase; }

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

    .agent-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px; margin-bottom: 1.5rem;
    }
    .agent {
        background: #0d0e12; border: 1px solid #1c1e24;
        border-radius: 4px; padding: 12px 14px;
        border-top: 2px solid #1c1e24;
    }
    .agent.long { border-top-color: #3ecf8e; }
    .agent.short { border-top-color: #f07178; }
    .agent.flat { border-top-color: #6b6e78; }
    .agent-k {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem; letter-spacing: 0.12em;
        text-transform: uppercase; color: #6b6e78; margin-bottom: 6px;
    }
    .agent-v {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem; font-weight: 700; letter-spacing: 0.06em;
    }
    .agent-c {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; margin-top: 4px; color: #a0a3ab;
    }
    .agent-why {
        font-size: 0.7rem; color: #6b6e78; margin-top: 8px; line-height: 1.4;
    }
    .bar {
        height: 4px; background: #1c1e24; border-radius: 2px; margin-top: 8px;
        overflow: hidden;
    }
    .bar > i {
        display: block; height: 100%; background: #3ecf8e;
    }
    .bar.dn > i { background: #f07178; }
    .bar.fl > i { background: #6b6e78; }

    table.mtx {
        width: 100%; border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        margin-bottom: 1.5rem;
    }
    table.mtx th {
        text-align: left; color: #6b6e78; font-weight: 500;
        letter-spacing: 0.08em; text-transform: uppercase;
        padding: 8px 10px; border-bottom: 1px solid #1c1e24;
    }
    table.mtx td {
        padding: 9px 10px; border-bottom: 1px solid #15171c; color: #d4d6db;
    }
    table.mtx tr:hover td { background: #0d0e12; }
    .cell {
        display: inline-block; min-width: 64px; text-align: right;
        padding: 2px 6px; border-radius: 3px;
    }
    .hi { background: #0f2a1c; color: #3ecf8e; }
    .lo { background: #2a0f0f; color: #f07178; }
    .mid { background: #1a1c22; color: #8b8e98; }

    @media (max-width: 900px) {
        .strip { grid-template-columns: repeat(2, 1fr); }
        .setup { grid-template-columns: 1fr 1fr; }
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


def load_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def setup_confidence(row, nifty_ret):
    score = safe_float(row.get("Score"))
    rvol = safe_float(row.get("VolSurge"))
    vs = safe_float(row.get("VsSector"))
    sig = str(row.get("Signal", "BUY")).upper()
    orh = safe_float(row.get("ORHigh"))
    orl = safe_float(row.get("ORLow"))
    entry = safe_float(row.get("Entry"))
    pts = 0.0
    pts += min(30.0, max(0.0, (score - 70) * 1.5))
    pts += min(20.0, max(0.0, (rvol - 1.2) * 12))
    pts += min(15.0, abs(vs) * 10)
    if entry and orh and orl:
        width = abs(orh - orl) / entry
        if 0.003 <= width <= 0.008:
            pts += 15
        elif width <= 0.012:
            pts += 8
    if sig == "BUY" and nifty_ret >= 0.25:
        pts += 20
    elif sig == "SELL" and nifty_ret <= -0.25:
        pts += 20
    elif abs(nifty_ret) < 0.25:
        pts -= 10
    return int(max(0, min(99, round(pts))))


def free_agents(sec_df, live_df, nret, mood):
    agents = []
    abs_n = abs(nret)
    if abs_n < 0.25:
        agents.append({
            "name": "Regime",
            "vote": "FLAT",
            "conf": int(min(95, 70 + (0.25 - abs_n) * 80)),
            "why": f"Nifty drive {nret:+.2f}% inside ±0.25. Stand aside.",
        })
    elif nret >= 0.25:
        agents.append({
            "name": "Regime",
            "vote": "LONG",
            "conf": int(min(95, 55 + abs_n * 40)),
            "why": f"Nifty open-drive {nret:+.2f}%. Longs only.",
        })
    else:
        agents.append({
            "name": "Regime",
            "vote": "SHORT",
            "conf": int(min(95, 55 + abs_n * 40)),
            "why": f"Nifty open-drive {nret:+.2f}%. Shorts only.",
        })

    if sec_df.empty:
        agents.append({"name": "Breadth", "vote": "FLAT", "conf": 0, "why": "No sector tape."})
        agents.append({"name": "RelStr", "vote": "FLAT", "conf": 0, "why": "No sector tape."})
    else:
        br = sec_df["Breadth"].astype(float)
        vs = sec_df["VsNifty"].astype(float)
        n_bull = int((sec_df["Bias"].astype(str).str.upper() == "BULLISH").sum())
        n_weak = int((sec_df["Bias"].astype(str).str.upper() == "WEAK").sum())
        avg_br = float(br.mean())
        if n_bull >= 2 and avg_br >= 55:
            agents.append({
                "name": "Breadth",
                "vote": "LONG",
                "conf": int(min(95, 40 + avg_br * 0.5 + n_bull * 8)),
                "why": f"{n_bull} bull sectors · avg breadth {avg_br:.0f}%.",
            })
        elif n_weak >= 2 and avg_br <= 45:
            agents.append({
                "name": "Breadth",
                "vote": "SHORT",
                "conf": int(min(95, 40 + (100 - avg_br) * 0.5 + n_weak * 8)),
                "why": f"{n_weak} weak sectors · avg breadth {avg_br:.0f}%.",
            })
        else:
            agents.append({
                "name": "Breadth",
                "vote": "FLAT",
                "conf": 55,
                "why": f"Split tape · bull {n_bull} / weak {n_weak} · br {avg_br:.0f}%.",
            })

        lead = vs.max()
        lag = vs.min()
        spread = lead - lag
        if lead >= 0.40 and lead > abs(lag):
            name = str(sec_df.loc[vs.idxmax(), "Sector"])
            agents.append({
                "name": "RelStr",
                "vote": "LONG",
                "conf": int(min(95, 50 + lead * 30)),
                "why": f"{name} leads vs Nifty {lead:+.2f}. Spread {spread:.2f}.",