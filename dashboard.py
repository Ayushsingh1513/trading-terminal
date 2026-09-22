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

# Reload the tape every 45s so GitHub CSV commits show up without a manual refresh.
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
    if not os.path.exists