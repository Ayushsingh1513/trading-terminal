import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings("ignore")

print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Data Engine (500+ Stocks & 18 Sectors)...")

# ══════════════════════════════════════════════════════════════════════════════
# UNIVERSE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
# 500+ Nifty/NSE Stocks Universe
NIFTY500 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS",
    "AXISBANK.NS","ITC.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","NESTLEIND.NS","WIPRO.NS","ULTRACEMCO.NS",
    "TECHM.NS","HCLTECH.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","BAJAJFINSV.NS","DIVISLAB.NS","DRREDDY.NS","ADANIENT.NS",
    "ADANIPORTS.NS","AMBUJACEM.NS","APOLLOHOSP.NS","BAJAJ-AUTO.NS","BANKBARODA.NS","BEL.NS","BPCL.NS","BRITANNIA.NS","CANBK.NS","CHOLAFIN.NS",
    "CIPLA.NS","DABUR.NS","DLF.NS","DIXON.NS","EICHERMOT.NS","GAIL.NS","GODREJCP.NS","GRASIM.NS","HAVELLS.NS","HEROMOTOCO.NS",
    "HINDALCO.NS","HINDPETRO.NS","INDUSINDBK.NS","IOC.NS","IRCTC.NS","JSWSTEEL.NS","LTIM.NS","LUPIN.NS","M&M.NS","MOTHERSON.NS",
    "MUTHOOTFIN.NS","NAUKRI.NS","PIDILITIND.NS","PNB.NS","SAIL.NS","SHREECEM.NS","SIEMENS.NS","SRF.NS","TATAPOWER.NS","TATASTEEL.NS",
    "TORNTPHARM.NS","TRENT.NS","VEDL.NS","VOLTAS.NS","ZOMATO.NS","ABB.NS","ABCAPITAL.NS","ACC.NS","APLAPOLLO.NS","AUBANK.NS",
    "AUROPHARMA.NS","BALKRISIND.NS","BANDHANBNK.NS","BERGEPAINT.NS","BIOCON.NS","BOSCHLTD.NS","COFORGE.NS","CROMPTON.NS","CUMMINSIND.NS","DALBHARAT.NS",
    "DEEPAKNTR.NS","ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","FORTIS.NS","GLENMARK.NS","GMRINFRA.NS","HAL.NS","HDFCAMC.NS","HDFCLIFE.NS",
    "IDFCFIRSTB.NS","IEX.NS","INDIANB.NS","INDHOTEL.NS","INDUSTOWER.NS","IRFC.NS","JKCEMENT.NS","JSWENERGY.NS","JUBLFOOD.NS","KEI.NS",
    "LALPATHLAB.NS","LICHSGFIN.NS","LICI.NS","MANAPPURAM.NS","MARICO.NS","MAXHEALTH.NS","MCX.NS","MPHASIS.NS","MRF.NS","NMDC.NS",
    "OBEROIRLTY.NS","OIL.NS","PAGEIND.NS","PERSISTENT.NS","PETRONET.NS","PHOENIX.NS","POLYCAB.NS","PRESTIGE.NS","PVRINOX.NS","RAMCOCEM.NS",
    "RVNL.NS","RECLTD.NS","SBICARD.NS","SBILIFE.NS","SOBHA.NS","SONACOMS.NS","SUPREMEIND.NS","SYNGENE.NS","TATACOMM.NS","TATACHEM.NS",
    "TATACONSUM.NS","TATAELXSI.NS","TATAMOTORS.NS","TATATECH.NS","TIINDIA.NS","TORNTPOWER.NS","TRIDENT.NS","UPL.NS","UTIAMC.NS","VGUARD.NS",
    "ZYDUSLIFE.NS","AARTIIND.NS","ABFRL.NS","ADANIENSOL.NS","ADANIGREEN.NS","ADANIPOWER.NS","ADANITOTAL.NS","AETHER.NS","AFFLE.NS","AJANTPHARM.NS",
    "ALOKINDS.NS","ALKYLAMINE.NS","ALLCARGO.NS","ANGELONE.NS","ANURAS.NS","APARINDS.NS","APOLLOTYRE.NS","APTUS.NS","ARE&M.NS","ASTERDM.NS",
    "ASTRAZEN.NS","ASTRAL.NS","ATUL.NS","AIAENG.NS","AWL.NS","BALAMINES.NS","BALRAMCHIN.NS","BATAINDIA.NS","BBNL.NS","BDL.NS",
    "BEML.NS","BHARATFORG.NS","BHEL.NS","BIKAJI.NS","BIRLACORPN.NS","BSOFT.NS","CAMPUS.NS","CANFINHOME.NS","CASTROLIND.NS","CDSL.NS",
    "CENTURYPLY.NS","CENTURYTEX.NS","CERA.NS","CESC.NS","CGPOWER.NS","CHAMBLFERT.NS","CLEAN.NS","COCHINSHIP.NS","COFFEEDAY.NS","CONCOR.NS",
    "COROMANDEL.NS","CREDITACC.NS","CYIENT.NS","DATAPATTNS.NS","DELHIVERY.NS","DEVYANI.NS","ECLERX.NS","EIDPARRY.NS","EIHOTEL.NS","ELGIEQUIP.NS",
    "EMAMILTD.NS","ENDURANCE.NS","ENGINERSIN.NS","EQUITASBNK.NS","ERIS.NS","FACT.NS","FIVESTAR.NS","FINEORG.NS","FINPIPE.NS","FSN.NS",
    "GMRAIRPORT.NS","GNFC.NS","GODREJPROP.NS","GRANULES.NS","GRAPHITE.NS","GSFC.NS","GSPL.NS","GUJGASLTD.NS","HFCL.NS","HLEGLAS.NS",
    "HAPPSTMNDS.NS","HEG.NS","HEMIPROP.NS","HOMFIRST.NS","HONASA.NS","HONAUT.NS","HUDCO.NS","IBREALEST.NS","IBULHSGFIN.NS","IDBI.NS",
    "IDEA.NS","IDFC.NS","IIFL.NS","IRB.NS","IRCON.NS","ITI.NS","INDIGO.NS","INDOCO.NS","INFIBEAM.NS","INOXWIND.NS",
    "INTELLECT.NS","IOB.NS","IPCALAB.NS","JBCHEPHARM.NS","JBMA.NS","JKTYRE.NS","JMFINANCIL.NS","JSL.NS","JSWINFRA.NS","JTPLL.NS",
    "JUBLPHARMA.NS","JUBLINGREA.NS","JUSTDIAL.NS","KALYANKJIL.NS","KFINTECH.NS","KNRCON.NS","KPITTECH.NS","KPRMILL.NS","KRBL.NS","KSB.NS",
    "KAJARIACER.NS","KPIL.NS","KARURVYSYA.NS","KEC.NS","KIRLOSENG.NS","LATENTVIEW.NS","LAURUSLABS.NS","LEMONTREE.NS","LINDEINDIA.NS","LLOYDSME.NS",
    "LXCHEM.NS","MGL.NS","MAPMYINDIA.NS","MAHDSC.NS","MAHSEAMLES.NS","MAHMGFIN.NS","MAHLIFE.NS","MANINFRA.NS","MASFIN.NS","MAZDOCK.NS",
    "MEDPLUS.NS","METROPOLIS.NS","MFSL.NS","MHRIL.NS","MINDACORP.NS","MSUMI.NS","MOTILALOFS.NS","MRPL.NS","MTARTECH.NS","NAM-INDIA.NS",
    "NATCOPHARM.NS","NATIONALUM.NS","NAVINFLUOR.NS","NBCC.NS","NCC.NS","NHPC.NS","NLCINDIA.NS","NUVAMA.NS","NYKAA.NS","OLECTRA.NS",
    "PAYTM.NS","PCBL.NS","PNCINFRA.NS","POLICYBZR.NS","PRAJIND.NS","PRINCEPIPE.NS","PNBHOUSING.NS","QUESS.NS","RBLBANK.NS","RCF.NS",
    "RELEXO.NS","RHIM.NS","RITES.NS","RKFORGE.NS","RPOWER.NS","SJVN.NS","SKFINDIA.NS","SAMHI.NS","SANSERA.NS","SAPPHIRE.NS",
    "SAREGAMA.NS","SCHAEFFLER.NS","SCHNEIDER.NS","SCI.NS","SHOPERSTOP.NS","SHYAMMETL.NS","SNET.NS","SOLARINDS.NS","SANGHVIMOV.NS","SONATSOFTW.NS",
    "STARHEALTH.NS","SUMICHEM.NS","SUNDARMFIN.NS","SUNDRMFAST.NS","SUNTECK.NS","SUNTV.NS","SUVENPHAR.NS","SUZLON.NS","SWANENERGY.NS","SYRMA.NS",
    "TMB.NS","TIRUMALCHM.NS","TITAGARH.NS","TORNTPOWER.NS","Triveni.NS","TRITURBINE.NS","TTKPRESTIG.NS","TV18BRDCST.NS","TVSMOTOR.NS","UCOBANK.NS",
    "UFOOTWEAR.NS","UNIONBANK.NS","UJJIVANSFB.NS","UNICHEMLAB.NS","UNOMINDA.NS","UPL.NS","USHAMART.NS","VAKRANGEE.NS","VALIANTORG.NS","VARROC.NS",
    "VBL.NS","VEDANTFASH.NS","VIJAYA.NS","VINATIORGA.NS","VIPIND.NS","WELCORP.NS","WELSPUNLIV.NS","WESTLIFE.NS","WHIRLPOOL.NS","WINDSOR.NS",
    "WOCKPHARMA.NS","YESBANK.NS","ZENSARTECH.NS","ZFSTEERING.NS","ZYDUSWELL.NS"
]

# 18 Major Sectors
SECTORS = {
    "IT": "^CNXIT", "Pvt Bank": "^CNXPVTBANK", "PSU Bank": "^CNXPSUBANK",
    "Fin Service": "^CNXFINANCE", "Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA",
    "FMCG": "^CNXFMCG", "Metal": "^CNXMETAL", "Energy": "^CNXENERGY",
    "Oil & Gas": "^CNXOILGAS", "Healthcare": "^CNXHEALTHCARE", "Realty": "^CNXREALTY",
    "Infra": "^CNXINFRA", "Cons Dur": "^CNXCONSUM", "Media": "^CNXMEDIA",
    "PSE": "^CNXPSE", "MNC": "^CNXMNC", "Commodities": "^CNXCOMMODITIES"
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def fetch_market_data():
    print("Fetching Market Indices...")
    data = yf.download(["^NSEI", "^NSEBANK", "^INDIAVIX"], period="1y", interval="1d", progress=False)['Close']
    
    nifty = data['^NSEI'].dropna()
    bank = data['^NSEBANK'].dropna()
    vix = data['^INDIAVIX'].dropna()

    nl = float(nifty.iloc[-1]); np_ = float(nifty.iloc[-2]); nchg = round((nl/np_-1)*100, 2)
    bl = float(bank.iloc[-1]); bp = float(bank.iloc[-2]); bchg = round((bl/bp-1)*100, 2)
    vl = float(vix.iloc[-1]); vc_ = float(vix.iloc[-2]); vchg = round((vl/vc_-1)*100, 2)
    
    ma200 = float(nifty.rolling(200).mean().iloc[-1])
    ma50 = float(nifty.rolling(50).mean().iloc[-1])
    nifty_1m = float((nl/nifty.iloc[max(-21,-len(nifty))]-1)*100)
    nifty_1w = float((nl/nifty.iloc[max(-5,-len(nifty))]-1)*100)

    mood_score = 0
    mood_score += 30 if nl > ma200 else 0
    mood_score += 20 if nl > ma50  else 0
    mood_score += 15 if nifty_1m > 0 else 0
    mood_score += 15 if nifty_1w > 0 else 0
    mood_score += 10 if nchg > 0 else 0
    mood_score += 10 if vl < 15 else (5 if vl < 20 else 0)
    
    mood = "BULLISH" if mood_score >= 70 else "NEUTRAL" if mood_score >= 45 else "BEARISH"

    return {
        "nifty": nl, "nifty_chg": nchg, "bank": bl, "bank_chg": bchg, "vix": round(vl, 2), "vix_chg": vchg,
        "ma200": round(ma200, 2), "ma50": round(ma50, 2), "mood": mood, "mood_score": mood_score,
        "nifty_1m_return": nifty_1m,
        "timestamp": (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime('%d %b %Y %H:%M IST')
    }

def scan_stocks(nifty_1m):
    print("Scanning 500+ Nifty Universe...")
    all_rows = []
    chunk_size = 50
    for i in range(0, len(NIFTY500), chunk_size):
        chunk = NIFTY500[i:i+chunk_size]
        raw = yf.download(chunk, period="6mo", interval="1d", progress=False, group_by="ticker")
        
        for t in chunk:
            try:
                df = raw[t] if len(chunk) > 1 else raw
                close = df['Close'].squeeze().dropna(); high = df['High'].squeeze().dropna()
                low = df['Low'].squeeze().dropna(); vol = df['Volume'].squeeze().dropna()
                if len(close) < 50: continue
                
                price = float(close.iloc[-1])
                ema20 = float(close.ewm(span=20).mean().iloc[-1])
                ema50 = float(close.ewm(span=50).mean().iloc[-1])
                ema200 = float(close.ewm(span=200).mean().iloc[-1])
                atr = float((high-low).rolling(14).mean().iloc[-1])
                
                delta = close.diff(); gain = delta.clip(lower=0).rolling(14).mean()
                loss = -delta.clip(upper=0).rolling(14).mean()
                rsi = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
                
                w52h = float(close.rolling(min(252,len(close))).max().iloc[-1])
                pfh = round((price/w52h-1)*100, 1)
                
                va = float(vol.rolling(20).mean().iloc[-1])
                vs = round(float(vol.iloc[-1])/va, 1) if va > 0 else 0
                s1m = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                rs = round(s1m-nifty_1m, 1)
                
                stage2 = price > ema20 > ema50 > ema200
                vcp = sum([stage2, pfh>-10, vs>=1.5, rs>0])
                sc = round(min(min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                         min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))
                
                sig = "BUY" if sc>=65 and stage2 else ("WATCH" if sc>=45 else "AVOID")
                setup = "Breakout" if stage2 and pfh>-3 and vs>=1.5 else "Pullback" if stage2 and 40<=rsi<=55 else "Vol Surge" if stage2 and vs>=2 else "Trend" if stage2 else "Base"
                risk_r = ["Low","Medium","High"][min(sum([vs>3, pfh<-20, rsi>75]),2)]
                
                entry = round(price * 1.001, 1)
                sl = round(max(ema20 * 0.99, price - atr * 1.5), 1)
                target1 = round(price + atr * 2, 1)
                target2 = round(price + atr * 3.5, 1)
                risk = round(entry - sl, 1)
                rr = round((target1 - entry) / risk, 1) if risk > 0 else 0

                all_rows.append({
                    "Stock": t.replace(".NS",""), "Price": round(price,1), "Setup": setup, "Score": sc, 
                    "Signal": sig, "RSI": round(rsi,1), "RS": rs, "VolSurge": vs, "52W%": pfh, "Risk": risk_r,
                    "Entry": entry, "SL": sl, "Target1": target1, "Target2": target2, "RR": rr,
                    "Stage2": "✅" if stage2 else "❌"
                })
            except Exception as e:
                pass
                
    df = pd.DataFrame(all_rows).sort_values("Score", ascending=False).reset_index(drop=True)
    return df

def scan_sectors():
    print("Analyzing 18 Sectors...")
    rows = []
    for name, ticker in SECTORS.items():
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
            if len(df) < 30: continue
            close = df['Close'].squeeze().dropna(); vol = df['Volume'].squeeze().dropna()
            
            price = float(close.iloc[-1]); prev = float(close.iloc[-2])
            pct_today = round((price/prev - 1)*100, 2)
            r1m = float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
            r3m = float((close.iloc[-1]/close.iloc[0]-1)*100)
            
            delta = close.diff(); gain = delta.clip(lower=0).rolling(14).mean(); loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
            pfh = round((price/float(close.rolling(min(252,len(close))).max().iloc[-1])-1)*100, 1)
            
            avg20 = float(vol.rolling(20).mean().iloc[-1]) if len(vol)>=20 else 1.0
            punch = round(float(vol.iloc[-1])/avg20, 2) if avg20 > 0 else 1.0
            score = round(r1m*0.4 + r3m*0.3 + (rsi/100)*20 + (10+pfh)*1, 2)
            
            rows.append({
                "Sector": name, "Today%": pct_today, "1M%": round(r1m,2), "3M%": round(r3m,2),
                "RSI": round(rsi,1), "52W%": pfh, "VolPunch": punch, "Score": score
            })
        except: pass
    return pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXECUTION & ATOMIC SAVE (SAFE OVERWRITE)
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        # 1. Fetch Market Data
        market_data = fetch_market_data()
        with open("market_data_temp.json", "w") as f:
            json.dump(market_data, f)
        os.replace("market_data_temp.json", "market_data.json")

        # 2. Fetch Scanner Data
        scanner_df = scan_stocks(market_data["nifty_1m_return"])
        scanner_df.to_csv("scanner_data_temp.csv", index=False)
        os.replace("scanner_data_temp.csv", "scanner_data.csv")

        # 3. Fetch Sector Data
        sector_df = scan_sectors()
        sector_df.to_csv("sector_data_temp.csv", index=False)
        os.replace("sector_data_temp.csv", "sector_data.csv")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Success: Engine generated all files securely.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
