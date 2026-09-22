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

st.set_page_config(page_title="Sector Tape", layout="wide", page_icon="■", initial_sidebar_state="collapsed")
components.html("<script>setTimeout(function(){window.parent.location.reload();},45000);</script>", height=0, width=0)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}
.stApp{background:#050608;color:#d4d6db}
.block-container{padding:1rem 1.5rem 2rem;max-width:1400px}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
section[data-testid="stSidebar"]{background:#0a0b0e;border-right:1px solid #1c1e24}
.topbar{display:flex;align-items:baseline;gap:1.25rem;flex-wrap:wrap;padding:0 0 1rem;border-bottom:1px solid #1c1e24;margin-bottom:1.25rem}
.topbar-title{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:.95rem;letter-spacing:.12em;text-transform:uppercase;color:#f0f1f3}
.topbar-meta{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#6b6e78}
.pill{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.65rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:3px}
.pill-up{background:#0f2a1c;color:#3ecf8e}.pill-dn{background:#2a0f0f;color:#f07178}.pill-flat{background:#1a1c22;color:#8b8e98}
.strip{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:1.25rem}
.strip-cell{background:#0d0e12;border:1px solid #1c1e24;border-radius:4px;padding:12px 14px}
.strip-label{font-size:.62rem;text-transform:uppercase;letter-spacing:.1em;color:#6b6e78;margin-bottom:4px}
.strip-val{font-family:'JetBrains Mono',monospace;font-size:1.05rem;font-weight:600;color:#f0f1f3}
.strip-sub{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#6b6e78;margin-top:2px}
.up{color:#3ecf8e!important}.dn{color:#f07178!important}
.sec-grid,.agent-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;margin-bottom:1.5rem}
.sec-card,.agent{background:#0d0e12;border:1px solid #1c1e24;border-radius:4px;padding:10px 12px;border-top:2px solid #1c1e24}
.sec-card.bull,.agent.long{border-top-color:#3ecf8e}
.sec-card.weak,.agent.short{border-top-color:#f07178}
.agent.flat{border-top-color:#6b6e78}
.sec-name,.agent-k{font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:#6b6e78;margin-bottom:6px}
.sec-ret,.agent-v{font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:700}
.sec-meta,.agent-c,.agent-why{font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#6b6e78;margin-top:4px;line-height:1.4}
.setup{background:#0d0e12;border:1px solid #1c1e24;border-radius:4px;padding:14px 16px;margin-bottom:10px;display:grid;grid-template-columns:90px 1fr auto auto;gap:14px;align-items:center}
.setup.buy{border-left:3px solid #3ecf8e}.setup.sell{border-left:3px solid #f07178}
.setup-side{font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:700;letter-spacing:.1em}
.setup-side.buy{color:#3ecf8e}.setup-side.sell{color:#f07178}
.setup-name{font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:600;color:#f0f1f3}
.setup-sub{font-size:.72rem;color:#6b6e78;margin-top:2px}
.setup-levels{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#a0a3ab;text-align:right;line-height:1.55}
.setup-levels b{color:#f0f1f3}
.conf{font-family:'JetBrains Mono',monospace;text-align:right}
.conf-n{font-size:1.2rem;font-weight:700}
.conf-l{font-size:.6rem;letter-spacing:.1em;color:#6b6e78;text-transform:uppercase}
.section-h{font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#6b6e78;margin:0 0 10px}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:1px solid #1c1e24;background:transparent}
.stTabs [data-baseweb="tab"]{height:36px;background:transparent;color:#6b6e78;font-family:'JetBrains Mono',monospace;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;border-radius:0;padding:0 16px}
.stTabs [aria-selected="true"]{color:#f0f1f3!important;border-bottom:2px solid #3ecf8e!important;background:transparent!important}
.stSelectbox label{display:none}
.empty{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:#6b6e78;padding:24px;text-align:center;border:1px dashed #1c1e24;border-radius:4px}
.bar{height:4px;background:#1c1e24;border-radius:2px;margin-top:8px;overflow:hidden}
.bar>i{display:block;height:100%;background:#3ecf8e}
.bar.dn>i{background:#f07178}.bar.fl>i{background:#6b6e78}
table.mtx{width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:.72rem;margin-bottom:1.5rem}
table.mtx th{text-align:left;color:#6b6e78;font-weight:500;letter-spacing:.08em;text-transform:uppercase;padding:8px 10px;border-bottom:1px solid #1c1e24}
table.mtx td{padding:9px 10px;border-bottom:1px solid #15171c;color:#d4d6db}
.cell{display:inline-block;min-width:64px;text-align:right;padding:2px 6px;border-radius:3px}
.hi{background:#0f2a1c;color:#3ecf8e}.lo{background:#2a0f0f;color:#f07178}.mid{background:#1a1c22;color:#8b8e98}
@media(max-width:900px){.strip{grid-template-columns:repeat(2,1fr)}.setup{grid-template-columns:1fr 1fr}}
</style>
""", unsafe_allow_html=True)


def sf(val, default=0.0):
    if pd.isna(val) or val in ["", None, "None", "nan"]:
        return default
    try:
        return float(val)
    except Exception:
        return default


def load_json_history(path="performance_history.json"):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        with open(path) as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame()
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            n = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
            pad = {k: (v + [None] * (n - len(v)) if isinstance(v, list) else [v] * n) for k, v in data.items()}
            return pd.DataFrame(pad)
    except Exception:
        pass
    return pd.DataFrame()


def load_market():
    if not os.path.exists("market_data.json"):
        return {}
    try:
        with open("market_data.json") as f:
            raw = json.load(f)
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def load_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def setup_conf(row, nret):
    score, rvol, vs = sf(row.get("Score")), sf(row.get("VolSurge")), sf(row.get("VsSector"))
    sig = str(row.get("Signal", "BUY")).upper()
    orh, orl, entry = sf(row.get("ORHigh")), sf(row.get("ORLow")), sf(row.get("Entry"))
    pts = min(30.0, max(0.0, (score - 70) * 1.5))
    pts += min(20.0, max(0.0, (rvol - 1.2) * 12))
    pts += min(15.0, abs(vs) * 10)
    if entry and orh and orl:
        w = abs(orh - orl) / entry
        pts += 15 if 0.003 <= w <= 0.008 else (8 if w <= 0.012 else 0)
    if sig == "BUY" and nret >= 0.25:
        pts += 20
    elif sig == "SELL" and nret <= -0.25:
        pts += 20
    elif abs(nret) < 0.25:
        pts -= 10
    return int(max(0, min(99, round(pts))))


def ag(name, vote, conf, why):
    return {"name": name, "vote": vote, "conf": int(max(0, min(95, conf))), "why": why}


def free_agents(sec_df, live_df, nret):
    out = []
    an = abs(nret)
    if an < 0.25:
        out.append(ag("Regime", "FLAT", 70 + (0.25 - an) * 80, "Nifty drive %.2f%% inside ±0.25. Stand aside." % nret))
    elif nret >= 0.25:
        out.append(ag("Regime", "LONG", 55 + an * 40, "Nifty open-drive %.2f%%. Longs only." % nret))
    else:
        out.append(ag("Regime", "SHORT", 55 + an * 40, "Nifty open-drive %.2f%%. Shorts only." % nret))

    if sec_df.empty:
        out.append(ag("Breadth", "FLAT", 0, "No sector tape."))
        out.append(ag("RelStr", "FLAT", 0, "No sector tape."))
    else:
        br = sec_df["Breadth"].astype(float)
        vs = sec_df["VsNifty"].astype(float)
        n_bull = int((sec_df["Bias"].astype(str).str.upper() == "BULLISH").sum())
        n_weak = int((sec_df["Bias"].astype(str).str.upper() == "WEAK").sum())
        avg_br = float(br.mean())
        if n_bull >= 2 and avg_br >= 55:
            out.append(ag("Breadth", "LONG", 40 + avg_br * 0.5 + n_bull * 8, "%d bull sectors · avg breadth %.0f%%." % (n_bull, avg_br)))
        elif n_weak >= 2 and avg_br <= 45:
            out.append(ag("Breadth", "SHORT", 40 + (100 - avg_br) * 0.5 + n_weak * 8, "%d weak sectors · avg breadth %.0f%%." % (n_weak, avg_br)))
        else:
            out.append(ag("Breadth", "FLAT", 55, "Split tape · bull %d / weak %d · br %.0f%%." % (n_bull, n_weak, avg_br)))
        lead, lag = float(vs.max()), float(vs.min())
        spread = lead - lag
        if lead >= 0.40 and lead > abs(lag):
            nm = str(sec_df.loc[vs.idxmax(), "Sector"])
            out.append(ag("RelStr", "LONG", 50 + lead * 30, "%s leads vs Nifty %+.2f. Spread %.2f." % (nm, lead, spread)))
        elif lag <= -0.40 and abs(lag) > lead:
            nm = str(sec_df.loc[vs.idxmin(), "Sector"])
            out.append(ag("RelStr", "SHORT", 50 + abs(lag) * 30, "%s lags vs Nifty %+.2f. Spread %.2f." % (nm, lag, spread)))
        else:
            out.append(ag("RelStr", "FLAT", 50, "No sector edge. Best %+.2f / worst %+.2f." % (lead, lag)))

    if live_df.empty:
        out.append(ag("Flow", "FLAT", 40, "No setups · no volume confirmation."))
        out.append(ag("Structure", "FLAT", 40, "No ORB prints."))
        return out

    rvol = float(live_df["VolSurge"].astype(float).mean()) if "VolSurge" in live_df.columns else 0.0
    n_buy = int((live_df["Signal"].astype(str).str.upper() == "BUY").sum()) if "Signal" in live_df.columns else 0
    n_sell = int((live_df["Signal"].astype(str).str.upper() == "SELL").sum()) if "Signal" in live_df.columns else 0
    if rvol >= 1.8 and n_buy > n_sell:
        out.append(ag("Flow", "LONG", 45 + rvol * 12, "RVOL %.1fx on %d long / %d short." % (rvol, n_buy, n_sell)))
    elif rvol >= 1.8 and n_sell > n_buy:
        out.append(ag("Flow", "SHORT", 45 + rvol * 12, "RVOL %.1fx on %d short / %d long." % (rvol, n_sell, n_buy)))
    else:
        out.append(ag("Flow", "FLAT", 30 + rvol * 10, "Weak flow. RVOL %.1fx." % rvol))

    widths, aligned = [], 0
    for _, t in live_df.iterrows():
        e = sf(t.get("Entry"))
        if e:
            widths.append(abs(sf(t.get("ORHigh")) - sf(t.get("ORLow"))) / e)
        sig = str(t.get("Signal", "")).upper()
        if (sig == "BUY" and nret >= 0) or (sig == "SELL" and nret < 0):
            aligned += 1
    avg_w = (sum(widths) / len(widths)) if widths else 0.0
    tight = 0.0025 <= avg_w <= 0.008
    if aligned == len(live_df) and tight:
        vote = "LONG" if n_buy >= n_sell else "SHORT"
        out.append(ag("Structure", vote, 82, "OR width %.2f%% · all setups aligned with Nifty." % (avg_w * 100)))
    elif tight:
        out.append(ag("Structure", "FLAT", 60, "OR width %.2f%% ok, alignment mixed." % (avg_w * 100)))
    else:
        out.append(ag("Structure", "FLAT", 45, "OR too wide/thin (%.2f%%). Fake-break risk." % (avg_w * 100)))
    return out


def consensus(agents):
    longs = [a for a in agents if a["vote"] == "LONG"]
    shorts = [a for a in agents if a["vote"] == "SHORT"]
    flats = [a for a in agents if a["vote"] == "FLAT"]
    if len(longs) >= 3:
        return "LONG", int(sum(a["conf"] for a in longs) / len(longs)), "%d/5 agents long" % len(longs)
    if len(shorts) >= 3:
        return "SHORT", int(sum(a["conf"] for a in shorts) / len(shorts)), "%d/5 agents short" % len(shorts)
    return "FLAT", 40 + len(flats) * 5, "%d/5 agents flat · no trade" % len(flats)


def heat(val, pos=True):
    if (val > 0.25) if pos else (val > 60):
        return "hi"
    if (val < -0.25) if pos else (val < 40):
        return "lo"
    return "mid"


sec_df = load_csv("sector_data.csv")
live_df = load_csv("scanner_data.csv")
mkt = load_market()
nifty, nret = sf(mkt.get("nifty")), sf(mkt.get("nifty_ret"))
mood, as_of = str(mkt.get("mood") or "—"), mkt.get("as_of") or "—"
ret_cls = "up" if nret >= 0 else "dn"
mood_u = mood.upper()
mood_pill = "pill-up" if mood_u == "BULLISH" else ("pill-dn" if mood_u in ("HEAVY", "BEARISH") else "pill-flat")
agents = free_agents(sec_df, live_df, nret)
vote, vote_conf, vote_why = consensus(agents)
vote_pill = "pill-up" if vote == "LONG" else ("pill-dn" if vote == "SHORT" else "pill-flat")
vote_cls = "up" if vote == "LONG" else ("dn" if vote == "SHORT" else "")
n_buy = int((live_df["Signal"].astype(str).str.upper() == "BUY").sum()) if not live_df.empty and "Signal" in live_df.columns else 0
n_sell = int((live_df["Signal"].astype(str).str.upper() == "SELL").sum()) if not live_df.empty and "Signal" in live_df.columns else 0
avg_br = float(sec_df["Breadth"].astype(float).mean()) if not sec_df.empty else 0.0
lead = ""
if not sec_df.empty:
    top = sec_df.sort_values("Score", ascending=False).iloc[0]
    lead = "%s %+.2f%%" % (top["Sector"], sf(top["ReturnPct"]))

with st.sidebar:
    st.markdown("**Risk**")
    fixed_rupee_risk = st.number_input("INR risk / trade", value=400.0, step=100.0, format="%.0f")
    max_trade_capital = st.number_input("INR max margin", value=50000.0, step=5000.0, format="%.0f")
    st.caption("5 free agents · 1R book · max 2 · flat 15:10")
    st.markdown("---")
    st.markdown("**Consensus**  \n`%s` · %d%%" % (vote, vote_conf))
    st.caption(vote_why)

st.markdown("""
<div class="topbar">
  <div class="topbar-title">Sector Tape</div>
  <span class="pill %s">%s</span>
  <span class="pill %s">AGENTS %s %d%%</span>
  <div class="topbar-meta">%s · refresh 45s</div>
</div>
<div class="strip">
  <div class="strip-cell"><div class="strip-label">Nifty</div><div class="strip-val">%s</div><div class="strip-sub %s">%+.2f%%</div></div>
  <div class="strip-cell"><div class="strip-label">Consensus</div><div class="strip-val %s">%s</div><div class="strip-sub">%d%% · %s</div></div>
  <div class="strip-cell"><div class="strip-label">Setups</div><div class="strip-val">%d</div><div class="strip-sub">L %d / S %d</div></div>
  <div class="strip-cell"><div class="strip-label">Avg breadth</div><div class="strip-val">%.0f%%</div><div class="strip-sub">members green</div></div>
  <div class="strip-cell"><div class="strip-label">Lead sector</div><div class="strip-val" style="font-size:.85rem">%s</div><div class="strip-sub">%s</div></div>
  <div class="strip-cell"><div class="strip-label">Weak sector</div><div class="strip-val" style="font-size:.85rem">%s</div><div class="strip-sub">short only if Nifty down</div></div>
</div>
""" % (
    mood_pill, mood, vote_pill, vote, vote_conf, as_of,
    "{:,.0f}".format(nifty), ret_cls, nret,
    vote_cls, vote, vote_conf, vote_why,
    0 if live_df.empty else len(live_df), n_buy, n_sell,
    avg_br, lead or "—", mkt.get("bullish_sectors") or "—",
    mkt.get("weak_sectors") or "—",
), unsafe_allow_html=True)

tab_tape, tab_mtx, tab_hist = st.tabs(["Tape", "Matrix", "History"])

with tab_tape:
    st.markdown('<p class="section-h">Free agents</p>', unsafe_allow_html=True)
    cards = []
    for a in agents:
        cls = "long" if a["vote"] == "LONG" else ("short" if a["vote"] == "SHORT" else "flat")
        bar = "dn" if a["vote"] == "SHORT" else ("fl" if a["vote"] == "FLAT" else "")
        col = "up" if a["vote"] == "LONG" else ("dn" if a["vote"] == "SHORT" else "")
        cards.append(
            '<div class="agent %s"><div class="agent-k">%s agent</div>'
            '<div class="agent-v %s">%s</div><div class="agent-c">%d%% confidence</div>'
            '<div class="bar %s"><i style="width:%d%%"></i></div>'
            '<div class="agent-why">%s</div></div>'
            % (cls, a["name"], col, a["vote"], a["conf"], bar, a["conf"], a["why"])
        )
    st.markdown('<div class="agent-grid">%s</div>' % "".join(cards), unsafe_allow_html=True)

    st.markdown('<p class="section-h">Sector map</p>', unsafe_allow_html=True)
    if sec_df.empty:
        st.markdown('<div class="empty">No sector data — run scanner</div>', unsafe_allow_html=True)
    else:
        scards = []
        for _, r in sec_df.iterrows():
            bias = str(r.get("Bias", "")).upper()
            cls = "bull" if bias == "BULLISH" else ("weak" if bias == "WEAK" else "")
            ret = sf(r.get("ReturnPct"))
            scards.append(
                '<div class="sec-card %s"><div class="sec-name">%s</div>'
                '<div class="sec-ret %s">%+.2f%%</div>'
                '<div class="sec-meta">vsN %+.2f · br %d%%</div>'
                '<div class="sec-meta">%s · sc %d</div></div>'
                % (cls, r.get("Sector"), "up" if ret >= 0 else "dn", ret,
                   sf(r.get("VsNifty")), int(sf(r.get("Breadth"))), bias, int(sf(r.get("Score"))))
            )
        st.markdown('<div class="sec-grid">%s</div>' % "".join(scards), unsafe_allow_html=True)

    st.markdown('<p class="section-h">Setups · long + short</p>', unsafe_allow_html=True)
    if live_df.empty:
        st.markdown('<div class="empty">No setups — stand aside. Agents need 3/5 agreement to trade.</div>', unsafe_allow_html=True)
    else:
        rows_html = []
        for _, t in live_df.iterrows():
            sig = str(t.get("Signal", "BUY")).upper()
            side = "buy" if sig == "BUY" else "sell"
            label = "LONG" if side == "buy" else "SHORT"
            name = str(t.get("Stock", "")).replace(".NS", "")
            conf = setup_conf(t, nret)
            conf_c = "up" if conf >= 70 else ("dn" if conf < 50 else "")
            rows_html.append(
                '<div class="setup %s"><div><div class="setup-side %s">%s</div>'
                '<div class="setup-sub">%s</div></div><div>'
                '<div class="setup-name">%s</div>'
                '<div class="setup-sub">%s · RVOL %s x · score %s</div></div>'
                '<div class="conf"><div class="conf-n %s">%d</div><div class="conf-l">confidence</div></div>'
                '<div class="setup-levels">Entry <b>INR %s</b><br>SL <b>INR %s</b><br>'
                'T1 1R <b>INR %s</b><br>T2 INR %s · qty %d</div></div>'
                % (side, side, label, t.get("Setup"), name, t.get("Sector"), t.get("VolSurge"), t.get("Score"),
                   conf_c, conf, "{:,.2f}".format(sf(t.get("Entry"))), "{:,.2f}".format(sf(t.get("SL"))),
                   "{:,.2f}".format(sf(t.get("Target1"))), "{:,.2f}".format(sf(t.get("Target2"))),
                   int(sf(t.get("Qty"))))
            )
        st.markdown("".join(rows_html), unsafe_allow_html=True)

        st.markdown('<p class="section-h" style="margin-top:1.5rem">Inspect</p>', unsafe_allow_html=True)
        selected = st.selectbox("stock", live_df["Stock"].tolist(), label_visibility="collapsed")
        row = live_df[live_df["Stock"] == selected].iloc[0]
        sig = str(row.get("Signal", "BUY")).upper()
        conf = setup_conf(row, nret)
        col_c, col_t = st.columns([1.6, 1])
        with col_c:
            hist = yf.Ticker(selected).history(period="5d", interval="5m")
            if hist.empty:
                hist = yf.Ticker(selected).history(period="5d")
            if not hist.empty and HAS_PLOTLY:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"],
                    increasing_line_color="#3ecf8e", decreasing_line_color="#f07178",
                    increasing_fillcolor="#3ecf8e", decreasing_fillcolor="#f07178",
                ))
                for y, color, label in [
                    (sf(row.get("Entry")), "#a0a3ab", "Entry"),
                    (sf(row.get("SL")), "#f07178", "SL"),
                    (sf(row.get("Target1")), "#3ecf8e", "T1"),
                    (sf(row.get("Target2")), "#6b6e78", "T2"),
                ]:
                    if y:
                        fig.add_hline(y=y, line_dash="dot", line_color=color, line_width=1,
                                      annotation_text=label, annotation_font_size=10)
                fig.update_layout(
                    template="plotly_dark", plot_bgcolor="#0d0e12", paper_bgcolor="#0d0e12",
                    font=dict(family="JetBrains Mono", size=10, color="#6b6e78"),
                    margin=dict(l=4, r=4, t=8, b=4), height=380,
                    xaxis_rangeslider_visible=False, showlegend=False,
                    xaxis=dict(gridcolor="#15171c"), yaxis=dict(gridcolor="#15171c", side="right"),
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_t:
            e, s = sf(row.get("Entry")), sf(row.get("SL"))
            risk_ps = abs(e - s) if e and s else 0
            qty = max(1, min(int(fixed_rupee_risk / risk_ps), int(max_trade_capital / e))) if risk_ps > 0 else int(sf(row.get("Qty")))
            action = "BUY" if sig == "BUY" else "SELL / SHORT"
            side_cls = "buy" if sig == "BUY" else "sell"
            st.markdown(
                '<div class="setup %s" style="grid-template-columns:1fr;display:block">'
                '<div class="setup-side %s">%s</div>'
                '<div class="setup-name" style="margin:8px 0">%s</div>'
                '<div class="conf-n %s">%d%% confidence</div>'
                '<div class="setup-levels" style="text-align:left;margin-top:10px">'
                'Entry <b>INR %s</b><br>SL <b>INR %s</b><br>T1 1R <b>INR %s</b><br>T2 <b>INR %s</b><br><br>'
                'Size <b>%d</b> sh<br>Margin INR %s<br>Risk INR %s</div>'
                '<div class="setup-sub" style="margin-top:10px">Skip if agents FLAT · book 1R · MIS · flat 15:10</div></div>'
                % (side_cls, side_cls, action, str(selected).replace(".NS", ""),
                   "up" if conf >= 70 else "", conf,
                   "{:,.2f}".format(e), "{:,.2f}".format(s),
                   "{:,.2f}".format(sf(row.get("Target1"))), "{:,.2f}".format(sf(row.get("Target2"))),
                   qty, "{:,.0f}".format(qty * e), "{:,.0f}".format(qty * risk_ps)),
                unsafe_allow_html=True,
            )

with tab_mtx:
    st.markdown('<p class="section-h">Sector matrix</p>', unsafe_allow_html=True)
    if sec_df.empty:
        st.markdown('<div class="empty">No sector matrix</div>', unsafe_allow_html=True)
    else:
        rows = ["<table class='mtx'><thead><tr><th>Sector</th><th>Bias</th><th>Return</th><th>vs Nifty</th><th>Breadth</th><th>Score</th><th>Last</th></tr></thead><tbody>"]
        for _, r in sec_df.sort_values("Score", ascending=False).iterrows():
            ret, vs, br, sc = sf(r.get("ReturnPct")), sf(r.get("VsNifty")), sf(r.get("Breadth")), int(sf(r.get("Score")))
            bias = str(r.get("Bias", "")).upper()
            bcls = "hi" if bias == "BULLISH" else ("lo" if bias == "WEAK" else "mid")
            rows.append(
                "<tr><td>%s</td><td><span class='cell %s'>%s</span></td>"
                "<td><span class='cell %s'>%+.2f%%</span></td>"
                "<td><span class='cell %s'>%+.2f</span></td>"
                "<td><span class='cell %s'>%.0f%%</span></td>"
                "<td>%+d</td><td>%s</td></tr>"
                % (r.get("Sector"), bcls, bias, heat(ret), ret, heat(vs), vs, heat(br, False), br, sc, "{:,.2f}".format(sf(r.get("Last"))))
            )
        rows.append("</tbody></table>")
        st.markdown("".join(rows), unsafe_allow_html=True)

    st.markdown('<p class="section-h">Agent vote board</p>', unsafe_allow_html=True)
    vrows = ["<table class='mtx'><thead><tr><th>Agent</th><th>Vote</th><th>Conf</th><th>Why</th></tr></thead><tbody>"]
    for a in agents:
        cls = "hi" if a["vote"] == "LONG" else ("lo" if a["vote"] == "SHORT" else "mid")
        vrows.append("<tr><td>%s</td><td><span class='cell %s'>%s</span></td><td>%d%%</td><td>%s</td></tr>" % (a["name"], cls, a["vote"], a["conf"], a["why"]))
    ccls = "hi" if vote == "LONG" else ("lo" if vote == "SHORT" else "mid")
    vrows.append("<tr><td><b>CONSENSUS</b></td><td><span class='cell %s'>%s</span></td><td>%d%%</td><td>%s</td></tr></tbody></table>" % (ccls, vote, vote_conf, vote_why))
    st.markdown("".join(vrows), unsafe_allow_html=True)
    st.caption("Free yfinance tape only. Need 3/5 same side to trade.")

raw_history = load_json_history("performance_history.json")
with tab_hist:
    if raw_history.empty:
        st.markdown('<div class="empty">No ledger</div>', unsafe_allow_html=True)
    else:
        valid = raw_history[raw_history["Status"].astype(str).str.contains("ACTIVE|CLOSED|HIT|EXIT", case=False, na=False)]
        st.dataframe(valid, use_container_width=True, height=400, hide_index=True)