import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(page_title="Momentum Frenzy Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* ── Base ── */
html, body, .stApp { background:#0a0a0f; color:#e0e0e0; font-family:'Inter',sans-serif; }
.block-container { padding:0rem 1rem 2rem 1rem; max-width:100%; }
header[data-testid="stHeader"] { display:none; }
#MainMenu { display:none; }
footer { display:none; }

/* ── Market Pulse Bar ── */
.pulse-bar {
  display:flex; gap:12px; flex-wrap:wrap;
  background:linear-gradient(90deg,#0f0f1a,#111128);
  border-bottom:1px solid #1e1e3a;
  padding:8px 16px; margin-bottom:12px;
  position:sticky; top:0; z-index:999;
}
.pulse-item { display:flex; flex-direction:column; align-items:center; min-width:90px; }
.pulse-label { font-size:10px; color:#888; text-transform:uppercase; letter-spacing:.08em; }
.pulse-value { font-size:14px; font-weight:700; color:#e0e0e0; }
.pulse-up   { color:#00e676 !important; }
.pulse-down { color:#ff5252 !important; }

/* ── Cards ── */
.card {
  background:#0f0f1a; border:1px solid #1e1e3a;
  border-radius:10px; padding:14px 18px; margin-bottom:12px;
}
.card-title { font-size:13px; text-transform:uppercase; letter-spacing:.1em; color:#888; margin-bottom:10px; }

/* ── Scanner Table ── */
.stDataFrame { border-radius:8px; overflow:hidden; }
div[data-testid="stDataFrame"] th { background:#111128 !important; color:#888 !important; font-size:12px; }

/* ── Metrics ── */
div[data-testid="metric-container"] {
  background:#0f0f1a; border:1px solid #1e1e3a;
  border-radius:8px; padding:10px 14px;
}
div[data-testid="metric-container"] label { color:#888; font-size:11px; }

/* ── Signal badges ── */
.badge-buy   { background:#00382a; color:#00e676; border:1px solid #00e676; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700; }
.badge-watch { background:#2a2200; color:#ffaa00; border:1px solid #ffaa00; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700; }
.badge-avoid { background:#2a0000; color:#ff5252; border:1px solid #ff5252; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700; }

/* ── Quadrant grid ── */
.quad-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.quad { border-radius:8px; padding:12px; min-height:110px; }
.quad-leading   { background:#00380a22; border:1px solid #00e67655; }
.quad-improving { background:#1a2a0022; border:1px solid #aaff0055; }
.quad-weakening { background:#2a1a0022; border:1px solid #ffaa0055; }
.quad-lagging   { background:#2a000022; border:1px solid #ff525255; }
.quad-title { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; margin-bottom:6px; }
.quad-leading .quad-title   { color:#00e676; }
.quad-improving .quad-title { color:#aaff00; }
.quad-weakening .quad-title { color:#ffaa00; }
.quad-lagging .quad-title   { color:#ff5252; }
.quad-stock { font-size:12px; padding:2px 6px; border-radius:3px; display:inline-block; margin:2px; background:#ffffff10; }

/* ── Section headers ── */
.section-header {
  font-size:12px; text-transform:uppercase; letter-spacing:.15em;
  color:#555; border-bottom:1px solid #1e1e3a;
  padding-bottom:6px; margin:16px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

@st.cache_data(ttl=900)
def get_close(ticker, period="1y"):
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    return df['Close'].squeeze().dropna()

@st.cache_data(ttl=900)
def get_ohlcv(ticker, period="6mo"):
    return yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)

def color_val(v):
    return "pulse-up" if v >= 0 else "pulse-down"

def arrow(v):
    return "▲" if v >= 0 else "▼"

def momentum_score(rsi, rs, vol_surge, vcp, pct_from_high):
    s  = min(max((rsi - 40) / 30 * 25, 0), 25)
    s += min(max(rs / 10 * 20, 0), 20)
    s += min(max((vol_surge - 1) / 2 * 20, 0), 20)
    s += vcp / 4 * 25
    s += min(max((10 + pct_from_high) / 10 * 10, 0), 10)
    return round(min(s, 100))

def setup_type(stage2, rsi, vol_surge, pct_from_high):
    if stage2 and pct_from_high > -3 and vol_surge >= 1.5:
        return "Breakout"
    if stage2 and 40 <= rsi <= 55:
        return "Pullback"
    if rsi < 35:
        return "Oversold"
    if stage2 and vol_surge >= 2:
        return "Vol Surge"
    if stage2:
        return "Trend"
    return "Base"

def signal_label(score, stage2):
    if score >= 65 and stage2:
        return "BUY"
    if score >= 45:
        return "WATCH"
    return "AVOID"

def risk_level(vol_surge, pct_from_high, rsi):
    r = 0
    if vol_surge > 3: r += 1
    if pct_from_high < -20: r += 1
    if rsi > 75: r += 1
    if r == 0: return "Low"
    if r == 1: return "Medium"
    return "High"


# ── Data Load ─────────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    nifty_close   = get_close("^NSEI")
    bank_close    = get_close("^NSEBANK")
    vix_close     = get_close("^INDIAVIX", period="1mo")

nifty_last  = float(nifty_close.iloc[-1])
nifty_prev  = float(nifty_close.iloc[-2])
nifty_chg   = (nifty_last / nifty_prev - 1) * 100

bank_last   = float(bank_close.iloc[-1])
bank_prev   = float(bank_close.iloc[-2])
bank_chg    = (bank_last / bank_prev - 1) * 100

vix_last    = float(vix_close.iloc[-1])
vix_prev    = float(vix_close.iloc[-2])
vix_chg     = (vix_last / vix_prev - 1) * 100

ma200       = float(nifty_close.rolling(200).mean().iloc[-1])
ma50        = float(nifty_close.rolling(50).mean().iloc[-1])
state       = "BULL" if nifty_last > ma200 else "BEAR"
state_color = "#00e676" if state == "BULL" else "#ff5252"
nifty_1m    = float((nifty_close.iloc[-1] / nifty_close.iloc[-21] - 1) * 100)


# ── Market Pulse Bar ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pulse-bar">
  <div class="pulse-item">
    <span class="pulse-label">Nifty 50</span>
    <span class="pulse-value {color_val(nifty_chg)}">{nifty_last:,.0f} {arrow(nifty_chg)} {abs(nifty_chg):.2f}%</span>
  </div>
  <div class="pulse-item">
    <span class="pulse-label">BankNifty</span>
    <span class="pulse-value {color_val(bank_chg)}">{bank_last:,.0f} {arrow(bank_chg)} {abs(bank_chg):.2f}%</span>
  </div>
  <div class="pulse-item">
    <span class="pulse-label">India VIX</span>
    <span class="pulse-value {color_val(-vix_chg)}">{vix_last:.1f} {arrow(vix_chg)} {abs(vix_chg):.1f}%</span>
  </div>
  <div class="pulse-item">
    <span class="pulse-label">MA200</span>
    <span class="pulse-value">{ma200:,.0f}</span>
  </div>
  <div class="pulse-item">
    <span class="pulse-label">Market</span>
    <span class="pulse-value" style="color:{state_color}">{state}</span>
  </div>
  <div class="pulse-item">
    <span class="pulse-label">Nifty 1M</span>
    <span class="pulse-value {color_val(nifty_1m)}">{arrow(nifty_1m)} {abs(nifty_1m):.1f}%</span>
  </div>
  <div class="pulse-item" style="margin-left:auto">
    <span class="pulse-label">Updated</span>
    <span class="pulse-value" style="font-size:11px;color:#666">{datetime.now().strftime('%d %b %H:%M')}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#00e676;margin:0 0 4px 0;font-size:20px;letter-spacing:.05em'>⚡ MOMENTUM FRENZY TRADING TERMINAL</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;font-size:12px;margin:0'>Indian Markets · Real-time Momentum Scanner</p>", unsafe_allow_html=True)


# ── Sector Rotation ───────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📊 Sector Rotation — 4 Quadrant</div>", unsafe_allow_html=True)

sectors = {
    "IT": "^CNXIT", "Bank": "^NSEBANK", "Auto": "^CNXAUTO",
    "Pharma": "^CNXPHARMA", "FMCG": "^CNXFMCG", "Metal": "^CNXMETAL",
    "Energy": "^CNXENERGY", "Realty": "^CNXREALTY"
}

with st.spinner("Loading sector data…"):
    rows = []
    for name, ticker in sectors.items():
        try:
            close = get_close(ticker, period="3mo")
            if len(close) < 20: continue
            ret_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100)
            ret_3m = float((close.iloc[-1] / close.iloc[0]  - 1) * 100)
            score  = round(ret_1m * 0.6 + ret_3m * 0.4, 2)
            rows.append({"Sector": name, "1M%": round(ret_1m,2), "3M%": round(ret_3m,2), "Score": score})
        except: pass

sector_df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)

# Quadrant logic: above/below median 1M and 3M
med_1m = sector_df["1M%"].median()
med_3m = sector_df["3M%"].median()

leading   = sector_df[(sector_df["1M%"] >= med_1m) & (sector_df["3M%"] >= med_3m)]["Sector"].tolist()
improving = sector_df[(sector_df["1M%"] >= med_1m) & (sector_df["3M%"] <  med_3m)]["Sector"].tolist()
weakening = sector_df[(sector_df["1M%"] <  med_1m) & (sector_df["3M%"] >= med_3m)]["Sector"].tolist()
lagging   = sector_df[(sector_df["1M%"] <  med_1m) & (sector_df["3M%"] <  med_3m)]["Sector"].tolist()

def quad_stocks(lst, sector_df):
    out = ""
    for s in lst:
        row = sector_df[sector_df["Sector"]==s].iloc[0]
        out += f'<span class="quad-stock">{s} <b>{row["1M%"]:+.1f}%</b></span>'
    return out or "<span style='color:#444;font-size:12px'>—</span>"

col_left, col_right = st.columns([1.2, 1])
with col_left:
    st.markdown(f"""
    <div class="quad-grid">
      <div class="quad quad-leading">
        <div class="quad-title">🚀 Leading (Strong)</div>
        {quad_stocks(leading, sector_df)}
      </div>
      <div class="quad quad-improving">
        <div class="quad-title">📈 Improving</div>
        {quad_stocks(improving, sector_df)}
      </div>
      <div class="quad quad-weakening">
        <div class="quad-title">⚠️ Weakening</div>
        {quad_stocks(weakening, sector_df)}
      </div>
      <div class="quad quad-lagging">
        <div class="quad-title">📉 Lagging</div>
        {quad_stocks(lagging, sector_df)}
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    fig_s = go.Figure(go.Bar(
        x=sector_df["Sector"], y=sector_df["Score"],
        marker_color=["#00e676" if s > 0 else "#ff5252" for s in sector_df["Score"]],
        text=[f"{s:+.1f}" for s in sector_df["Score"]],
        textposition="outside"
    ))
    fig_s.update_layout(
        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
        font_color="#888", height=240, margin=dict(l=0,r=0,t=10,b=0),
        yaxis=dict(gridcolor="#1a1a2e", zeroline=True, zerolinecolor="#333"),
        xaxis=dict(gridcolor="#1a1a2e")
    )
    st.plotly_chart(fig_s, use_container_width=True)


# ── Momentum Scanner ──────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🔍 Momentum Scanner — Action Table</div>", unsafe_allow_html=True)

watchlist = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "SBIN.NS","WIPRO.NS","AXISBANK.NS","LT.NS","BAJFINANCE.NS",
    "MARUTI.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS",
    "TITAN.NS","HINDUNILVR.NS","TECHM.NS","HCLTECH.NS",
    "POWERGRID.NS","NTPC.NS","COALINDIA.NS","TATAPOWER.NS",
    "DIXON.NS","HAL.NS","BEL.NS"
]

with st.spinner("Scanning stocks…"):
    rows2 = []
    for t in watchlist:
        try:
            df = yf.download(t, period="1y", interval="1d", progress=False, auto_adjust=True)
            if len(df) < 50: continue
            close  = df['Close'].squeeze().dropna()
            volume = df['Volume'].squeeze().dropna()

            ema20  = float(close.ewm(span=20).mean().iloc[-1])
            ema50  = float(close.ewm(span=50).mean().iloc[-1])
            ema200 = float(close.ewm(span=200).mean().iloc[-1])
            price  = float(close.iloc[-1])

            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = -delta.clip(upper=0).rolling(14).mean()
            rsi   = float(100 - (100 / (1 + gain.iloc[-1] / (loss.iloc[-1] + 1e-9))))

            week52_high  = float(close.rolling(min(252,len(close))).max().iloc[-1])
            pct_from_high = round((price / week52_high - 1)*100, 1)

            vol_avg20 = float(volume.rolling(20).mean().iloc[-1])
            vol_today = float(volume.iloc[-1])
            vol_surge = round(vol_today / vol_avg20, 1) if vol_avg20 > 0 else 0

            stock_1m = float((close.iloc[-1]/close.iloc[-21]-1)*100)
            rs = round(stock_1m - nifty_1m, 1)

            stage2  = price > ema20 > ema50 > ema200
            near_52w = pct_from_high > -10
            vol_ok   = vol_surge >= 1.5
            rs_ok    = rs > 0
            vcp_int  = sum([stage2, near_52w, vol_ok, rs_ok])

            mscore = momentum_score(rsi, rs, vol_surge, vcp_int, pct_from_high)
            setup  = setup_type(stage2, rsi, vol_surge, pct_from_high)
            sig    = signal_label(mscore, stage2)
            risk   = risk_level(vol_surge, pct_from_high, rsi)

            rows2.append({
                "Stock": t.replace(".NS",""),
                "Price": round(price,1),
                "Setup": setup,
                "Score": mscore,
                "Signal": sig,
                "RSI": round(rsi,1),
                "RS": rs,
                "VolSurge": vol_surge,
                "52W%": pct_from_high,
                "Risk": risk,
                "VCP": f"{vcp_int}/4",
                "Stage2": "✅" if stage2 else "❌",
            })
        except: pass

scan_df = pd.DataFrame(rows2).sort_values("Score", ascending=False).reset_index(drop=True)

# Filter controls
c1, c2, c3, _ = st.columns([1,1,1,3])
with c1:
    sig_filter = st.selectbox("Signal", ["All","BUY","WATCH","AVOID"])
with c2:
    risk_filter = st.selectbox("Risk", ["All","Low","Medium","High"])
with c3:
    setup_filter = st.selectbox("Setup", ["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])

filtered = scan_df.copy()
if sig_filter  != "All": filtered = filtered[filtered["Signal"]  == sig_filter]
if risk_filter != "All": filtered = filtered[filtered["Risk"]    == risk_filter]
if setup_filter!= "All": filtered = filtered[filtered["Setup"]   == setup_filter]

def style_signal(val):
    if val == "BUY":   return "background-color:#00380a;color:#00e676;font-weight:700"
    if val == "WATCH": return "background-color:#2a2200;color:#ffaa00;font-weight:700"
    if val == "AVOID": return "background-color:#2a0000;color:#ff5252;font-weight:700"
    return ""

def style_score(val):
    if val >= 65: return "color:#00e676;font-weight:700"
    if val >= 45: return "color:#ffaa00"
    return "color:#ff5252"

styled = filtered.style\
    .map(style_signal, subset=["Signal"])\
    .map(style_score,  subset=["Score"])\
    .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"})

st.dataframe(styled, use_container_width=True, height=320)

st.caption(f"Showing {len(filtered)} of {len(scan_df)} stocks · Score 0–100 · Signal = BUY/WATCH/AVOID")


# ── Chart Viewer ──────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📈 Chart Viewer</div>", unsafe_allow_html=True)

chart_col, info_col = st.columns([3,1])
with chart_col:
    selected_stock  = st.selectbox("Select Stock", [t.replace(".NS","") for t in watchlist])
with info_col:
    period_choice = st.selectbox("Period", ["3mo","6mo","1y"])

selected_ticker = selected_stock + ".NS"
stock_df = get_ohlcv(selected_ticker, period_choice)

if len(stock_df) > 0:
    sc = stock_df['Close'].squeeze()
    sv = stock_df['Volume'].squeeze()

    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         row_heights=[0.75, 0.25], vertical_spacing=0.03)

    # Candles
    fig2.add_trace(go.Candlestick(
        x=stock_df.index,
        open=stock_df['Open'].squeeze(), high=stock_df['High'].squeeze(),
        low=stock_df['Low'].squeeze(),   close=sc,
        name=selected_stock,
        increasing_line_color="#00e676", decreasing_line_color="#ff5252"
    ), row=1, col=1)

    # EMAs
    fig2.add_trace(go.Scatter(x=stock_df.index, y=sc.ewm(span=20).mean(),  name="EMA20",  line=dict(color="#00e676",width=1.2)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=stock_df.index, y=sc.ewm(span=50).mean(),  name="EMA50",  line=dict(color="#ffaa00",width=1.2)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=stock_df.index, y=sc.ewm(span=200).mean(), name="EMA200", line=dict(color="#ff5252",width=1.2)), row=1, col=1)

    # Volume bars
    vol_colors = ["#00e67655" if c >= o else "#ff525255"
                  for c,o in zip(stock_df['Close'].squeeze(), stock_df['Open'].squeeze())]
    fig2.add_trace(go.Bar(x=stock_df.index, y=sv, name="Volume", marker_color=vol_colors, showlegend=False), row=2, col=1)

    fig2.update_layout(
        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
        font_color="#888", height=520,
        margin=dict(l=0,r=0,t=10,b=0),
        xaxis=dict(gridcolor="#1a1a2e", rangeslider=dict(visible=False)),
        xaxis2=dict(gridcolor="#1a1a2e"),
        yaxis=dict(gridcolor="#1a1a2e"),
        yaxis2=dict(gridcolor="#1a1a2e"),
        legend=dict(bgcolor="#0f0f1a", bordercolor="#1e1e3a", borderwidth=1, font=dict(size=11))
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Mini stats panel
    if selected_stock in scan_df["Stock"].values:
        row = scan_df[scan_df["Stock"]==selected_stock].iloc[0]
        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("Score",   f"{row['Score']}/100")
        m2.metric("Signal",  row["Signal"])
        m3.metric("RSI",     f"{row['RSI']}")
        m4.metric("Vol Surge", f"{row['VolSurge']}x")
        m5.metric("52W High", f"{row['52W%']}%")


# ── Nifty Chart ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🇮🇳 Nifty 50 Overview</div>", unsafe_allow_html=True)

nifty_df = get_ohlcv("^NSEI", "1y")
nc = nifty_df['Close'].squeeze()

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=nifty_df.index, y=nc, name="Nifty", line=dict(color="#00e676", width=1.5), fill="tozeroy", fillcolor="#00e67611"))
fig3.add_trace(go.Scatter(x=nifty_df.index, y=nc.rolling(200).mean(), name="MA200", line=dict(color="#ff5252", dash="dash", width=1)))
fig3.add_trace(go.Scatter(x=nifty_df.index, y=nc.rolling(50).mean(),  name="MA50",  line=dict(color="#ffaa00", dash="dot",  width=1)))
fig3.update_layout(
    plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
    font_color="#888", height=320,
    margin=dict(l=0,r=0,t=10,b=0),
    xaxis=dict(gridcolor="#1a1a2e"),
    yaxis=dict(gridcolor="#1a1a2e"),
    legend=dict(bgcolor="#0f0f1a", bordercolor="#1e1e3a", font=dict(size=11))
)
st.plotly_chart(fig3, use_container_width=True)


# ── Telegram Alert ────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📲 Telegram Alert</div>", unsafe_allow_html=True)

if st.button("🚀 Send Morning Alert"):
    top = sector_df.iloc[0]
    buys   = scan_df[scan_df["Signal"]=="BUY"]["Stock"].tolist()[:5]
    watch  = scan_df[scan_df["Signal"]=="WATCH"]["Stock"].tolist()[:5]
    top5   = scan_df.head(5)["Stock"].tolist()
    msg = (
        f"<b>⚡ MOMENTUM FRENZY Terminal</b>\n"
        f"{datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
        f"<b>Nifty:</b> {nifty_last:,.0f} ({nifty_chg:+.2f}%) | {state}\n"
        f"<b>BankNifty:</b> {bank_last:,.0f} ({bank_chg:+.2f}%)\n"
        f"<b>VIX:</b> {vix_last:.1f}\n\n"
        f"<b>Top Sector:</b> {top['Sector']} ({top['Score']:+.1f})\n\n"
        f"<b>🟢 BUY Signals:</b> {', '.join(buys) or 'None'}\n"
        f"<b>🟡 WATCH:</b> {', '.join(watch) or 'None'}\n"
        f"<b>🏆 Top Scores:</b> {', '.join(top5)}"
    )
    send_telegram(msg)
    st.success("✅ Alert sent to Telegram!")

st.caption(f"Momentum Frenzy Terminal · {datetime.now().strftime('%d %b %Y %H:%M')} IST · Data: Yahoo Finance")
