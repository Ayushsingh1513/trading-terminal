import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests

BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID = "-4037707574219"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except:
        pass

def get_close(ticker, period="1y"):
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    close = df['Close']
    if isinstance(close.columns if hasattr(close, 'columns') else [], pd.Index):
        close = close.squeeze()
    return close.dropna()

st.set_page_config(page_title="India Trading Terminal", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0d0d0d; color: #00ff88; }
div[data-testid="metric-container"] {
    background-color: #1a1a2e; border: 1px solid #00ff88;
    border-radius: 8px; padding: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("IN India Trading Terminal")

nifty_close = get_close("^NSEI")
ma200 = float(nifty_close.rolling(200).mean().iloc[-1])
ma50 = float(nifty_close.rolling(50).mean().iloc[-1])
last_close = float(nifty_close.iloc[-1])
state = "BULL" if last_close > ma200 else "BEAR"
nifty_1m_ret = float((nifty_close.iloc[-1] / nifty_close.iloc[-21] - 1) * 100)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Nifty 50", f"{last_close:,.0f}")
col2.metric("MA200", f"{ma200:,.0f}")
col3.metric("MA50", f"{ma50:,.0f}")
col4.metric("Market State", state)

st.divider()
st.subheader("Sector Rotation")

sectors = {
    "IT": "^CNXIT", "Bank": "^NSEBANK", "Auto": "^CNXAUTO",
    "Pharma": "^CNXPHARMA", "FMCG": "^CNXFMCG", "Metal": "^CNXMETAL",
    "Energy": "^CNXENERGY", "Realty": "^CNXREALTY"
}
rows = []
for name, ticker in sectors.items():
    try:
        close = get_close(ticker, period="3mo")
        if len(close) < 20:
            continue
        ret_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100)
        ret_3m = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
        score = round((ret_1m * 0.6 + ret_3m * 0.4), 2)
        rows.append({"Sector": name, "1M%": round(ret_1m, 2), "3M%": round(ret_3m, 2), "Score": score})
    except:
        pass

sector_df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
fig_s = go.Figure(go.Bar(
    x=sector_df["Sector"], y=sector_df["Score"],
    marker_color=["#00ff88" if s > 0 else "#ff4444" for s in sector_df["Score"]]))
fig_s.update_layout(plot_bgcolor="#0d0d0d", paper_bgcolor="#0d0d0d", font_color="#00ff88", height=280)
st.plotly_chart(fig_s, use_container_width=True)
st.dataframe(sector_df, use_container_width=True)

st.divider()
st.subheader("Stock Scanner - Momentum Burst")

watchlist = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "SBIN.NS","WIPRO.NS","AXISBANK.NS","LT.NS","BAJFINANCE.NS",
    "MARUTI.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS",
    "TITAN.NS","HINDUNILVR.NS","TECHM.NS","HCLTECH.NS",
    "POWERGRID.NS","NTPC.NS","COALINDIA.NS","TATAPOWER.NS",
    "DIXON.NS","HAL.NS","BEL.NS"
]

rows2 = []
for t in watchlist:
    try:
        df = yf.download(t, period="1y", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 50:
            continue
        close = df['Close'].squeeze().dropna()
        volume = df['Volume'].squeeze().dropna()

        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1])
        ema200 = float(close.ewm(span=200).mean().iloc[-1])
        price = float(close.iloc[-1])

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rsi = float(100 - (100 / (1 + gain.iloc[-1] / loss.iloc[-1])))

        week52_high = float(close.rolling(min(252, len(close))).max().iloc[-1])
        pct_from_high = round((price / week52_high - 1) * 100, 1)

        vol_avg20 = float(volume.rolling(20).mean().iloc[-1])
        vol_today = float(volume.iloc[-1])
        vol_surge = round(vol_today / vol_avg20, 1) if vol_avg20 > 0 else 0

        stock_1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100)
        rs = round(stock_1m - nifty_1m_ret, 1)

        stage2 = price > ema20 > ema50 > ema200
        near_52w = pct_from_high > -10
        vol_ok = vol_surge >= 1.5
        rs_ok = rs > 0
        vcp_score = sum([stage2, near_52w, vol_ok, rs_ok])
        signal = "Oversold" if rsi < 30 else ("Overbought" if rsi > 70 else "Neutral")

        rows2.append({
            "Stock": t.replace(".NS", ""),
            "Price": round(price, 1),
            "RSI": round(rsi, 1),
            "RS": rs,
            "VolSurge": vol_surge,
            "52W%": pct_from_high,
            "Stage2": "YES" if stage2 else "NO",
            "VCP": f"{vcp_score}/4",
            "Signal": signal
        })
    except:
        pass

scan_df = pd.DataFrame(rows2).sort_values("VCP", ascending=False)
st.dataframe(scan_df, use_container_width=True)

st.divider()
st.subheader("Nifty Chart")
nifty_df = yf.download("^NSEI", period="1y", interval="1d", progress=False, auto_adjust=True)
nc = nifty_df['Close'].squeeze()
fig = go.Figure()
fig.add_trace(go.Scatter(x=nifty_df.index, y=nc, name="Nifty", line=dict(color="#00ff88")))
fig.add_trace(go.Scatter(x=nifty_df.index, y=nc.rolling(200).mean(), name="MA200", line=dict(color="#ff4444", dash="dash")))
fig.add_trace(go.Scatter(x=nifty_df.index, y=nc.rolling(50).mean(), name="MA50", line=dict(color="#ffaa00", dash="dot")))
fig.update_layout(plot_bgcolor="#0d0d0d", paper_bgcolor="#0d0d0d", font_color="#00ff88", height=400)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Send Telegram Alert")
if st.button("Send Morning Alert"):
    top = sector_df.iloc[0]
    vcp4 = scan_df[scan_df['VCP'] == '4/4']['Stock'].tolist()
    vcp3 = scan_df[scan_df['VCP'] == '3/4']['Stock'].tolist()
    oversold = scan_df[scan_df['Signal'] == 'Oversold']['Stock'].tolist()
    msg = (
        f"<b>India Trading Terminal</b>\n"
        f"{datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
        f"<b>Nifty:</b> {last_close:,.0f} | {state}\n"
        f"<b>Top Sector:</b> {top['Sector']} ({top['Score']})\n\n"
        f"<b>VCP 4/4:</b> {', '.join(vcp4) or 'None'}\n"
        f"<b>VCP 3/4:</b> {', '.join(vcp3) or 'None'}\n"
        f"<b>Oversold:</b> {', '.join(oversold) or 'None'}"
    )
    send_telegram(msg)
    st.success("Sent to Telegram!")

st.caption("Last updated: " + datetime.now().strftime("%d %b %Y %H:%M") + " IST")