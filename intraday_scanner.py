"""
Intraday sector-first scanner for NSE cash.

Flow:
  1. Score sector indices vs Nifty using the 09:15–09:45 opening range.
  2. Keep only BULLISH sectors (long-only).
  3. Inside those sectors, keep liquid names that lead the sector,
     hold VWAP, and break/tag the opening-range high.
  4. SL = opening-range low. T1 = 2R, T2 = 3R.
  5. Size at 0.4% of corpus, max 2 names, 1 per sector.

Run: python intraday_scanner.py
"""
from __future__ import annotations

import os
from datetime import datetime

import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

IST = pytz.timezone("Asia/Kolkata")

TOTAL_CORPUS = 100_000.0
MAX_TRADE_CAPITAL = 50_000.0
RISK_PCT = 0.004  # 0.4% per trade
MAX_TRADES = 2
MAX_OR_WIDTH = 0.012  # skip if opening range > 1.2% of price
MIN_RVOL = 1.2
MIN_BREADTH = 0.55

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Official-ish NSE groups with liquid names. Index first, ETF fallback.
SECTORS = {
    "Bank": {
        "index": "^NSEBANK",
        "etf": "BANKBEES.NS",
        "names": [
            "HDFCBANK.NS",
            "ICICIBANK.NS",
            "SBIN.NS",
            "AXISBANK.NS",
            "KOTAKBANK.NS",
            "INDUSINDBK.NS",
            "FEDERALBNK.NS",
            "BANKBARODA.NS",
        ],
    },
    "IT": {
        "index": "^CNXIT",
        "etf": "ITBEES.NS",
        "names": [
            "TCS.NS",
            "INFY.NS",
            "HCLTECH.NS",
            "WIPRO.NS",
            "TECHM.NS",
            "PERSISTENT.NS",
            "COFORGE.NS",
            "MPHASIS.NS",
        ],
    },
    "Auto": {
        "index": "^CNXAUTO",
        "etf": "AUTOBEES.NS",
        "names": [
            "MARUTI.NS",
            "M&M.NS",
            "BAJAJ-AUTO.NS",
            "EICHERMOT.NS",
            "HEROMOTOCO.NS",
            "TVSMOTOR.NS",
            "ASHOKLEY.NS",
        ],
    },
    "Pharma": {
        "index": "^CNXPHARMA",
        "etf": "PHARMABEES.NS",
        "names": [
            "SUNPHARMA.NS",
            "DRREDDY.NS",
            "CIPLA.NS",
            "DIVISLAB.NS",
            "APOLLOHOSP.NS",
            "LAURUSLABS.NS",
            "AUROPHARMA.NS",
            "MAXHEALTH.NS",
        ],
    },
    "FMCG": {
        "index": "^CNXFMCG",
        "etf": "CONSUMBEES.NS",
        "names": [
            "HINDUNILVR.NS",
            "ITC.NS",
            "NESTLEIND.NS",
            "BRITANNIA.NS",
            "TATACONSUM.NS",
            "DABUR.NS",
            "GODREJCP.NS",
            "MARICO.NS",
        ],
    },
    "Metal": {
        "index": "^CNXMETAL",
        "etf": "TATASTEEL.NS",
        "names": [
            "TATASTEEL.NS",
            "JSWSTEEL.NS",
            "HINDALCO.NS",
            "VEDL.NS",
            "JINDALSTEL.NS",
            "NATIONALUM.NS",
            "HINDZINC.NS",
            "SAIL.NS",
        ],
    },
    "Energy": {
        "index": "^CNXENERGY",
        "etf": "RELIANCE.NS",
        "names": [
            "RELIANCE.NS",
            "ONGC.NS",
            "NTPC.NS",
            "POWERGRID.NS",
            "COALINDIA.NS",
            "BPCL.NS",
            "IOC.NS",
            "ADANIGREEN.NS",
        ],
    },
    "Infra": {
        "index": "^CNXINFRA",
        "etf": "INFRABEES.NS",
        "names": [
            "LT.NS",
            "ADANIPORTS.NS",
            "ULTRACEMCO.NS",
            "GRASIM.NS",
            "SIEMENS.NS",
            "ABB.NS",
            "BEL.NS",
            "HAL.NS",
        ],
    },
}

NIFTY = "^NSEI"


def now_ist() -> datetime:
    return datetime.now(IST)


def send_telegram(message: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram secrets missing — skip alert.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
        if r.status_code != 200:
            print(f"Telegram error {r.status_code}: {r.text}")
    except Exception as exc:
        print(f"Telegram failed: {exc}")


def to_ist(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    if not isinstance(out.index, pd.DatetimeIndex):
        return pd.DataFrame()
    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    out.index = out.index.tz_convert(IST)
    out.columns = [str(c).title() if str(c).lower() in {"open", "high", "low", "close", "volume"} else c for c in out.columns]
    return out


def last_session(df: pd.DataFrame) -> pd.DataFrame:
    df = to_ist(df)
    if df.empty:
        return df
    day = df.index[-1].date()
    sess = df[df.index.date == day]
    return sess.between_time("09:15", "15:30")


def bars_of(raw: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        if symbol not in set(raw.columns.get_level_values(0)):
            return pd.DataFrame()
        piece = raw[symbol]
    else:
        piece = raw
    return piece.dropna(how="all")


def slice_symbol(raw: pd.DataFrame, symbol: str) -> pd.DataFrame:
    return last_session(bars_of(raw, symbol))


def opening_range(session: pd.DataFrame) -> tuple[float, float, pd.DataFrame]:
    or_bars = session.between_time("09:15", "09:44")
    if or_bars.empty:
        or_bars = session.iloc[:6]
    if or_bars.empty:
        return np.nan, np.nan, or_bars
    return float(or_bars["High"].max()), float(or_bars["Low"].min()), or_bars


def vwap(session: pd.DataFrame) -> float:
    if session.empty or "Volume" not in session.columns:
        return np.nan
    vol = session["Volume"].fillna(0)
    if vol.sum() <= 0:
        return float(session["Close"].iloc[-1])
    tp = (session["High"] + session["Low"] + session["Close"]) / 3.0
    return float((tp * vol).sum() / vol.sum())


def ret_pct(session: pd.DataFrame) -> float:
    if session.empty or len(session) < 1:
        return np.nan
    o = float(session["Open"].iloc[0])
    c = float(session["Close"].iloc[-1])
    if o <= 0:
        return np.nan
    return (c - o) / o * 100.0


def download_bundle(tickers: list[str], interval: str, period: str) -> pd.DataFrame:
    uniq = list(dict.fromkeys(tickers))
    try:
        return yf.download(
            uniq,
            period=period,
            interval=interval,
            group_by="ticker",
            threads=True,
            progress=False,
            auto_adjust=True,
        )
    except Exception as exc:
        print(f"download failed {interval}: {exc}")
        return pd.DataFrame()


def position_size(entry: float, sl: float) -> int:
    if entry <= 0 or sl >= entry:
        return 0
    risk_ps = entry - sl
    qty_risk = int((TOTAL_CORPUS * RISK_PCT) / risk_ps)
    qty_cap = int(MAX_TRADE_CAPITAL / entry)
    return max(0, min(qty_risk, qty_cap))


def score_sector(session: pd.DataFrame, nifty_ret: float, members: list[pd.DataFrame]) -> dict:
    last = float(session["Close"].iloc[-1])
    r = ret_pct(session)
    vs = r - nifty_ret if pd.notna(r) and pd.notna(nifty_ret) else 0.0
    vw = vwap(session)
    green = 0
    counted = 0
    for m in members:
        if m.empty:
            continue
        counted += 1
        if float(m["Close"].iloc[-1]) > float(m["Open"].iloc[0]):
            green += 1
    breadth = (green / counted) if counted else 0.5
    score = 0
    if vs >= 0.15:
        score += 2
    elif vs <= -0.15:
        score -= 2
    if breadth >= MIN_BREADTH:
        score += 2
    elif breadth <= 0.40:
        score -= 2
    if pd.notna(r) and r >= 0.20:
        score += 1
    elif pd.notna(r) and r <= -0.20:
        score -= 1
    if pd.notna(vw) and last > vw:
        score += 1
    else:
        score -= 1
    if score >= 3:
        bias = "BULLISH"
    elif score <= -3:
        bias = "WEAK"
    else:
        bias = "CHOP"
    return {
        "ReturnPct": round(float(r) if pd.notna(r) else 0.0, 2),
        "VsNifty": round(float(vs), 2),
        "Breadth": round(breadth * 100, 0),
        "Score": score,
        "Bias": bias,
        "Last": round(last, 2),
        "VWAP": round(float(vw) if pd.notna(vw) else last, 2),
    }


def evaluate_stock(symbol: str, session: pd.DataFrame, daily: pd.DataFrame, sector_ret: float, sector: str) -> dict | None:
    if session is None or session.empty or len(session) < 4:
        return None
    or_high, or_low, or_bars = opening_range(session)
    if pd.isna(or_high) or pd.isna(or_low) or or_high <= or_low:
        return None
    last = float(session["Close"].iloc[-1])
    if last < 50:
        return None
    width = (or_high - or_low) / last
    if width > MAX_OR_WIDTH or width < 0.002:
        return None
    vw = vwap(session)
    if pd.isna(vw) or last < vw:
        return None
    stock_ret = ret_pct(session)
    if pd.isna(stock_ret) or stock_ret < sector_ret:
        return None
    sess_vol = float(session["Volume"].fillna(0).sum())
    adv = np.nan
    if daily is not None and not daily.empty and "Volume" in daily.columns:
        adv = float(daily["Volume"].tail(20).mean())
    elapsed_frac = max(0.08, min(0.25, len(session) / 75.0))
    rvol = (sess_vol / (adv * elapsed_frac)) if adv and adv > 0 else 0.0
    if rvol < MIN_RVOL:
        return None
    broke = last >= or_high * 0.999
    tagged = last >= or_high * 0.997
    if not (broke or tagged):
        return None
    setup = "ORB break" if broke else "OR tag"
    entry = round(last, 2)
    sl = round(or_low, 2)
    risk = entry - sl
    if risk <= 0:
        return None
    t1 = round(entry + 2 * risk, 2)
    t2 = round(entry + 3 * risk, 2)
    qty = position_size(entry, sl)
    if qty < 1:
        return None
    rs = stock_ret - sector_ret
    score = int(min(99, 70 + rs * 8 + min(rvol, 3) * 6))
    return {
        "Stock": symbol,
        "Signal": "BUY",
        "Setup": setup,
        "Sector": sector,
        "SectorBias": "BULLISH",
        "WeeklyTrend": "INTRADAY",
        "MTF": "Opening range",
        "Price": entry,
        "Score": score,
        "RSI": round(stock_ret, 1),
        "VolSurge": round(rvol, 2),
        "Entry": entry,
        "SL": sl,
        "Target1": t1,
        "Target2": t2,
        "RR": 2.0,
        "ORHigh": round(or_high, 2),
        "ORLow": round(or_low, 2),
        "VsSector": round(rs, 2),
        "Qty": qty,
        "Margin": round(qty * entry, 2),
        "RiskRs": round(qty * risk, 2),
    }


def run_intraday() -> tuple[pd.DataFrame, pd.DataFrame]:
    stamp = now_ist().strftime("%Y-%m-%d %H:%M IST")
    print(f"[{stamp}] Intraday sector scan")

    all_names = [n for spec in SECTORS.values() for n in spec["names"]]
    proxies = [spec["index"] for spec in SECTORS.values()] + [spec["etf"] for spec in SECTORS.values()] + [NIFTY]
    five_min_tickers = list(dict.fromkeys(all_names + proxies))
    daily_tickers = list(dict.fromkeys(all_names))

    intra_raw = download_bundle(five_min_tickers, "5m", "5d")
    daily_raw = download_bundle(daily_tickers, "1d", "1mo")

    nifty_sess = slice_symbol(intra_raw, NIFTY)
    nifty_ret = ret_pct(nifty_sess) if not nifty_sess.empty else 0.0
    print(f"Nifty open-drive: {nifty_ret:.2f}%")

    sector_rows = []
    bullish: dict[str, float] = {}
    member_cache: dict[str, pd.DataFrame] = {}

    for name in all_names:
        member_cache[name] = slice_symbol(intra_raw, name)

    for sector, spec in SECTORS.items():
        sess = slice_symbol(intra_raw, spec["index"])
        if sess.empty or len(sess) < 3:
            sess = slice_symbol(intra_raw, spec["etf"])
        if sess.empty or len(sess) < 3:
            print(f"skip {sector}: no bars")
            continue
        members = [member_cache[n] for n in spec["names"] if n in member_cache]
        scored = score_sector(sess, nifty_ret, members)
        scored["Sector"] = sector
        sector_rows.append(scored)
        print(f"  {sector:8} {scored['Bias']:8} ret={scored['ReturnPct']:+.2f} vsNifty={scored['VsNifty']:+.2f} breadth={scored['Breadth']:.0f}%")
        if scored["Bias"] == "BULLISH":
            bullish[sector] = scored["ReturnPct"]

    sector_df = pd.DataFrame(sector_rows)
    if not sector_df.empty:
        sector_df = sector_df[
            ["Sector", "Bias", "ReturnPct", "VsNifty", "Breadth", "Score", "Last", "VWAP"]
        ].sort_values("Score", ascending=False)
    sector_df.to_csv("sector_data.csv", index=False)

    setups: list[dict] = []
    if not bullish:
        print("No bullish sector — stand aside.")
    else:
        for sector, sector_ret in bullish.items():
            names = SECTORS[sector]["names"]
            best_for_sector = None
            for symbol in names:
                sess = member_cache.get(symbol, pd.DataFrame())
                daily = to_ist(bars_of(daily_raw, symbol))
                row = evaluate_stock(symbol, sess, daily, sector_ret, sector)
                if row is None:
                    continue
                if best_for_sector is None or row["Score"] > best_for_sector["Score"]:
                    best_for_sector = row
            if best_for_sector:
                setups.append(best_for_sector)

    scan_df = pd.DataFrame(setups)
    if not scan_df.empty:
        scan_df = scan_df.sort_values(["Score", "VolSurge"], ascending=False).head(MAX_TRADES)
    else:
        scan_df = pd.DataFrame(
            columns=[
                "Stock",
                "Signal",
                "Setup",
                "Sector",
                "SectorBias",
                "WeeklyTrend",
                "MTF",
                "Price",
                "Score",
                "RSI",
                "VolSurge",
                "Entry",
                "SL",
                "Target1",
                "Target2",
                "RR",
                "ORHigh",
                "ORLow",
                "VsSector",
                "Qty",
                "Margin",
                "RiskRs",
            ]
        )
    scan_df.to_csv("scanner_data.csv", index=False)

    market_blob = {
        "nifty": float(nifty_sess["Close"].iloc[-1]) if not nifty_sess.empty else 0.0,
        "nifty_ret": round(float(nifty_ret) if pd.notna(nifty_ret) else 0.0, 2),
        "mood": "BULLISH" if (nifty_ret or 0) >= 0 else "HEAVY",
        "as_of": stamp,
        "bullish_sectors": ",".join(bullish.keys()),
        "weak_sectors": ",".join(sector_df.loc[sector_df["Bias"] == "WEAK", "Sector"].tolist()) if not sector_df.empty else "",
    }
    pd.Series(market_blob).to_json("market_data.json")

    lines = [
        f"INTRADAY TAPE  {stamp}",
        f"Nifty {market_blob['nifty']:.0f}  open-drive {market_blob['nifty_ret']:+.2f}%",
        "",
    ]
    if not sector_df.empty:
        for _, r in sector_df.iterrows():
            lines.append(
                f"{r['Bias']:8}  {r['Sector']:8}  {r['ReturnPct']:+.2f}%  vsNifty {r['VsNifty']:+.2f}  breadth {int(r['Breadth'])}%"
            )
    lines.append("")
    if scan_df.empty:
        lines.append("No long setups. Stand aside.")
    else:
        lines.append(f"SETUPS  (max {MAX_TRADES}, 1 per sector, 0.4% risk)")
        for _, t in scan_df.iterrows():
            lines.append(
                f"{t['Stock']}  {t['Setup']}  {t['Sector']}\n"
                f"  Entry {t['Entry']}  SL {t['SL']}  T1 {t['Target1']}  T2 {t['Target2']}\n"
                f"  Qty {int(t['Qty'])}  risk Rs {t['RiskRs']}  RVOL {t['VolSurge']}x"
            )
        lines.append("Fill is live / next 5-min bar. Flat by 15:10. Skip if price gaps through SL.")
    send_telegram("\n".join(lines))
    print("Wrote sector_data.csv, scanner_data.csv, market_data.json")
    return scan_df, sector_df


if __name__ == "__main__":
    run_intraday()