import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import numpy as np

BOT_TOKEN = "8651727429:AAHAA9nFtPpUO2npxgdR6MyZkZBMqHLyTRg"
CHAT_ID   = "-1003707574219"

st.set_page_config(
    page_title="Momentum Frenzy — Indian Stock Scanner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state.page = "landing"

if st.session_state.page == "landing":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
    html,body,.stApp{background:#03030a;color:#e0e0f0;font-family:'Inter',sans-serif;}
    .block-container{padding:0!important;max-width:100%!important;}
    header[data-testid="stHeader"]{display:none!important;}
    #MainMenu{display:none!important;}footer{display:none!important;}
    .stButton>button{
      background:linear-gradient(135deg,#3b82f6,#6d28d9)!important;
      color:#fff!important;border:none!important;font-size:15px!important;font-weight:700!important;
      padding:14px 32px!important;border-radius:12px!important;width:100%!important;
      box-shadow:0 0 30px rgba(59,130,246,.4),0 0 60px rgba(59,130,246,.15)!important;
      transition:transform .2s,box-shadow .2s!important;letter-spacing:.3px!important;
    }
    .stButton>button:hover{
      transform:translateY(-3px)!important;
      box-shadow:0 0 40px rgba(59,130,246,.6),0 0 80px rgba(59,130,246,.2)!important;
    }
    /* 3D Canvas bg */
    #mf-canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}
    /* Ticker */
    .tk{position:relative;z-index:100;background:rgba(3,3,10,.95);
      border-bottom:1px solid rgba(59,130,246,.15);height:30px;overflow:hidden;display:flex;align-items:center}
    .tk-inner{display:flex;animation:tkScroll 50s linear infinite;width:max-content}
    .tk-item{display:flex;align-items:center;gap:5px;padding:0 16px;font-size:10px;
      font-family:'JetBrains Mono',monospace;white-space:nowrap;border-right:1px solid rgba(59,130,246,.1)}
    .tk-n{color:#2a2a4a}.tk-v{color:#8080a0;font-weight:500}
    .tk-u{color:#00d97e}.tk-d{color:#ff4560}
    @keyframes tkScroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
    /* Hero */
    .lp-hero{position:relative;z-index:10;min-height:95vh;display:flex;flex-direction:column;
      align-items:center;justify-content:center;text-align:center;padding:60px 20px 50px}
    /* 3D card effect */
    .card-3d{
      background:rgba(10,10,20,.7);
      border:1px solid rgba(59,130,246,.2);
      border-radius:20px;padding:40px 30px;
      backdrop-filter:blur(20px);
      box-shadow:
        0 0 0 1px rgba(59,130,246,.1),
        0 20px 60px rgba(0,0,0,.6),
        0 0 120px rgba(59,130,246,.05),
        inset 0 1px 0 rgba(255,255,255,.05);
      transform:perspective(1000px) rotateX(2deg);
      transition:transform .4s ease,box-shadow .4s ease;
      max-width:700px;margin:0 auto;
    }
    .card-3d:hover{
      transform:perspective(1000px) rotateX(0deg) translateY(-4px);
      box-shadow:
        0 0 0 1px rgba(59,130,246,.25),
        0 30px 80px rgba(0,0,0,.7),
        0 0 160px rgba(59,130,246,.1),
        inset 0 1px 0 rgba(255,255,255,.08);
    }
    .lp-logo{width:80px;height:80px;border-radius:50%;object-fit:cover;
      border:2px solid rgba(255,255,255,.08);margin-bottom:20px;
      box-shadow:0 0 30px rgba(59,130,246,.4),0 0 60px rgba(59,130,246,.15);
      animation:logoGlow 3s ease-in-out infinite;
    }
    @keyframes logoGlow{
      0%,100%{box-shadow:0 0 30px rgba(59,130,246,.4),0 0 60px rgba(59,130,246,.15)}
      50%{box-shadow:0 0 50px rgba(139,92,246,.6),0 0 100px rgba(139,92,246,.2)}
    }
    .lp-name{font-size:clamp(30px,5vw,52px);font-weight:900;letter-spacing:-2px;line-height:1;margin-bottom:6px}
    .lp-grd{background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 50%,#00d97e 100%);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      background-size:200%;animation:grdMove 4s ease infinite}
    @keyframes grdMove{0%,100%{background-position:0%}50%{background-position:100%}}
    .live-pill{display:inline-flex;align-items:center;gap:6px;
      background:rgba(0,217,126,.08);border:1px solid rgba(0,217,126,.25);
      color:#00d97e;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
      padding:5px 14px;border-radius:20px;margin:14px 0 18px;
      animation:pillPulse 2.5s ease-in-out infinite}
    @keyframes pillPulse{0%,100%{box-shadow:0 0 0 rgba(0,217,126,0)}50%{box-shadow:0 0 20px rgba(0,217,126,.2)}}
    .live-d{width:6px;height:6px;border-radius:50%;background:#00d97e;animation:dotBlink 1.5s ease-in-out infinite}
    @keyframes dotBlink{0%,100%{opacity:1;box-shadow:0 0 6px #00d97e}50%{opacity:.2;box-shadow:none}}
    .lp-title{font-size:clamp(32px,6vw,64px);font-weight:900;line-height:1.05;letter-spacing:-2px;margin-bottom:14px}
    .lp-t1{display:block;color:#f0f0ff;
      text-shadow:0 0 80px rgba(59,130,246,.3)}
    .lp-t2{display:block;background:linear-gradient(90deg,#3b82f6,#8b5cf6);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .lp-sub{font-size:clamp(13px,2vw,16px);color:#4a4a66;line-height:1.75;margin-bottom:28px}
    /* Market strip 3D */
    .mkt-3d{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;
      padding:0 20px;max-width:1000px;margin:0 auto;position:relative;z-index:10}
    .mk{background:rgba(10,10,20,.8);
      border:1px solid rgba(59,130,246,.15);border-radius:12px;padding:12px 14px;
      backdrop-filter:blur(12px);cursor:default;
      box-shadow:0 4px 20px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.04);
      transition:transform .3s,box-shadow .3s,border-color .3s;
      animation:mkIn .5s ease both;opacity:0}
    .mk:hover{transform:translateY(-4px) perspective(400px) rotateX(4deg);
      box-shadow:0 12px 40px rgba(0,0,0,.6),0 0 30px rgba(59,130,246,.15),inset 0 1px 0 rgba(255,255,255,.06);
      border-color:rgba(59,130,246,.35)}
    @keyframes mkIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    .mn{font-size:9px;color:#2a2a42;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
    .mv{font-size:14px;font-weight:700;color:#c0c0d8;margin-bottom:2px}
    .mc-up{color:#00d97e;font-size:11px;font-weight:600}
    .mc-dn{color:#ff4560;font-size:11px;font-weight:600}
    /* Stats 3D */
    .stats-3d{display:flex;flex-wrap:wrap;justify-content:center;gap:20px;
      padding:36px 20px;background:rgba(6,6,16,.9);
      border-top:1px solid rgba(59,130,246,.1);border-bottom:1px solid rgba(59,130,246,.1);
      margin:36px 0;position:relative;z-index:10;backdrop-filter:blur(8px)}
    .st{background:rgba(10,10,22,.8);border:1px solid rgba(59,130,246,.15);border-radius:14px;
      padding:20px 28px;text-align:center;min-width:120px;
      box-shadow:0 8px 30px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.04);
      transition:transform .3s,box-shadow .3s;animation:stIn .5s ease both;opacity:0}
    .st:hover{transform:translateY(-5px) perspective(400px) rotateX(5deg);
      box-shadow:0 16px 50px rgba(0,0,0,.5),0 0 40px rgba(59,130,246,.12)}
    @keyframes stIn{from{opacity:0;transform:translateY(10px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}
    .sn{font-size:36px;font-weight:900;background:linear-gradient(135deg,#3b82f6,#8b5cf6);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1}
    .sl{font-size:9px;color:#2a2a42;text-transform:uppercase;letter-spacing:1.5px;margin-top:4px}
    /* Feature cards 3D */
    .feats-3d{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;
      padding:0 20px;max-width:1020px;margin:0 auto 50px;position:relative;z-index:10}
    .fc{background:rgba(10,10,20,.75);
      border:1px solid rgba(59,130,246,.12);border-radius:14px;padding:22px;
      backdrop-filter:blur(10px);
      box-shadow:0 4px 24px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.04);
      transition:transform .3s,box-shadow .3s,border-color .3s;
      animation:fcIn .5s ease both;opacity:0;position:relative;overflow:hidden}
    .fc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
      background:linear-gradient(90deg,transparent,rgba(59,130,246,.6),transparent);
      transform:scaleX(0);transition:transform .4s}
    .fc:hover{transform:translateY(-5px) perspective(500px) rotateX(3deg) rotateY(-1deg);
      border-color:rgba(59,130,246,.3);
      box-shadow:0 16px 50px rgba(0,0,0,.5),0 0 40px rgba(59,130,246,.1),inset 0 1px 0 rgba(255,255,255,.06)}
    .fc:hover::before{transform:scaleX(1)}
    @keyframes fcIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    .fi{font-size:24px;margin-bottom:10px;display:block;transition:transform .3s}
    .fc:hover .fi{transform:scale(1.2) translateY(-2px)}
    .ft{font-size:13px;font-weight:700;color:#d0d0e8;margin-bottom:6px}
    .fd{font-size:11px;color:#2a2a42;line-height:1.65}
    /* CTA */
    .cta-3d{background:rgba(12,8,22,.85);
      border:1px solid rgba(139,92,246,.2);border-radius:18px;padding:36px;
      backdrop-filter:blur(14px);max-width:560px;margin:0 auto 50px;text-align:center;
      position:relative;z-index:10;
      box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 80px rgba(109,40,217,.08),inset 0 1px 0 rgba(255,255,255,.05);
      transition:transform .3s,box-shadow .3s}
    .cta-3d:hover{transform:translateY(-4px);
      box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 100px rgba(109,40,217,.15),inset 0 1px 0 rgba(255,255,255,.07)}
    .ct{font-size:20px;font-weight:800;color:#e8e8f8;margin-bottom:7px}
    .cs{font-size:12px;color:#3a3a56;margin-bottom:16px;line-height:1.6}
    /* Disc + footer */
    .disc{max-width:680px;margin:0 auto 10px;padding:14px 20px;
      background:rgba(6,6,14,.8);border:1px solid rgba(59,130,246,.08);
      border-radius:8px;font-size:10px;color:#1e1e30;text-align:center;position:relative;z-index:10}
    .ftr{position:relative;z-index:10;border-top:1px solid rgba(59,130,246,.08);
      padding:18px;text-align:center;font-size:10px;color:#1a1a2a;letter-spacing:.5px}
    .ftr a{color:#1a1a2a;text-decoration:none}
    </style>
    <canvas id="mf-canvas"></canvas>
    <div class="tk">
      <div class="tk-inner">
        <span class="tk-item"><span class="tk-n">NIFTY</span><span class="tk-v">24,749</span><span class="tk-u">+0.94%</span></span>
        <span class="tk-item"><span class="tk-n">BANKNIFTY</span><span class="tk-v">53,210</span><span class="tk-u">+1.21%</span></span>
        <span class="tk-item"><span class="tk-n">VIX</span><span class="tk-v">12.84</span><span class="tk-d">-5.2%</span></span>
        <span class="tk-item"><span class="tk-n">SENSEX</span><span class="tk-v">81,224</span><span class="tk-u">+0.87%</span></span>
        <span class="tk-item"><span class="tk-n">IT</span><span class="tk-v">35,841</span><span class="tk-d">-0.38%</span></span>
        <span class="tk-item"><span class="tk-n">USD/INR</span><span class="tk-v">83.48</span><span class="tk-d">-0.14%</span></span>
        <span class="tk-item"><span class="tk-n">MIDCAP</span><span class="tk-v">54,103</span><span class="tk-u">+0.72%</span></span>
        <span class="tk-item"><span class="tk-n">GOLD</span><span class="tk-v">71,240</span><span class="tk-u">+0.31%</span></span>
        <span class="tk-item"><span class="tk-n">NIFTY</span><span class="tk-v">24,749</span><span class="tk-u">+0.94%</span></span>
        <span class="tk-item"><span class="tk-n">BANKNIFTY</span><span class="tk-v">53,210</span><span class="tk-u">+1.21%</span></span>
        <span class="tk-item"><span class="tk-n">VIX</span><span class="tk-v">12.84</span><span class="tk-d">-5.2%</span></span>
        <span class="tk-item"><span class="tk-n">SENSEX</span><span class="tk-v">81,224</span><span class="tk-u">+0.87%</span></span>
        <span class="tk-item"><span class="tk-n">IT</span><span class="tk-v">35,841</span><span class="tk-d">-0.38%</span></span>
        <span class="tk-item"><span class="tk-n">USD/INR</span><span class="tk-v">83.48</span><span class="tk-d">-0.14%</span></span>
        <span class="tk-item"><span class="tk-n">MIDCAP</span><span class="tk-v">54,103</span><span class="tk-u">+0.72%</span></span>
        <span class="tk-item"><span class="tk-n">GOLD</span><span class="tk-v">71,240</span><span class="tk-u">+0.31%</span></span>
      </div>
    </div>
    <section class="lp-hero">
      <div class="card-3d">
        <img class="lp-logo" src="https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png" onerror="this.style.display='none'">
        <div class="lp-name">MOMENTUM<br><span class="lp-grd">FRENZY</span></div>
        <div class="live-pill"><span class="live-d"></span>Live Indian Markets</div>
        <h1 class="lp-title">
          <span class="lp-t1">Find Your Next Trade</span>
          <span class="lp-t2">Before the Market Moves</span>
        </h1>
        <p class="lp-sub">Professional momentum scanner for NSE swing traders.<br>Sector rotation · Breakout radar · Daily picks — all free.</p>
      </div>
    </section>
    <div class="mkt-3d">
      <div class="mk" style="animation-delay:.06s"><div class="mn">NIFTY 50</div><div class="mv">24,749</div><div class="mc-up">+0.94%</div></div>
      <div class="mk" style="animation-delay:.12s"><div class="mn">BANK NIFTY</div><div class="mv">53,210</div><div class="mc-up">+1.21%</div></div>
      <div class="mk" style="animation-delay:.18s"><div class="mn">VIX</div><div class="mv">12.84</div><div class="mc-dn">-5.2%</div></div>
      <div class="mk" style="animation-delay:.24s"><div class="mn">USD/INR</div><div class="mv">83.48</div><div class="mc-dn">-0.14%</div></div>
      <div class="mk" style="animation-delay:.30s"><div class="mn">NIFTY IT</div><div class="mv">35,841</div><div class="mc-dn">-0.38%</div></div>
      <div class="mk" style="animation-delay:.36s"><div class="mn">MIDCAP</div><div class="mv">54,103</div><div class="mc-up">+0.72%</div></div>
    </div>
    <div class="stats-3d">
      <div class="st" style="animation-delay:.08s"><div class="sn">500+</div><div class="sl">Stocks Scanned</div></div>
      <div class="st" style="animation-delay:.16s"><div class="sn">14</div><div class="sl">Sectors Tracked</div></div>
      <div class="st" style="animation-delay:.24s"><div class="sn">Free</div><div class="sl">Always</div></div>
      <div class="st" style="animation-delay:.32s"><div class="sn">2x</div><div class="sl">Daily Alerts</div></div>
    </div>
    <div style="text-align:center;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
      color:#1e1e2e;padding:0 20px 16px;position:relative;z-index:10">What you get</div>
    <div class="feats-3d">
      <div class="fc" style="animation-delay:.06s"><span class="fi">🎯</span><div class="ft">Today's top picks</div><div class="fd">Entry, target, stop-loss and risk:reward — ready every morning.</div></div>
      <div class="fc" style="animation-delay:.12s"><span class="fi">📊</span><div class="ft">Sector intelligence</div><div class="fd">4-Quadrant rotation showing which sectors lead, improve or lag.</div></div>
      <div class="fc" style="animation-delay:.18s"><span class="fi">💥</span><div class="ft">Volume punch radar</div><div class="fd">Catch institutional activity before the crowd notices.</div></div>
      <div class="fc" style="animation-delay:.24s"><span class="fi">📈</span><div class="ft">Professional charts</div><div class="fd">Candlestick + EMA 20/50/200 for any Nifty 500 stock.</div></div>
      <div class="fc" style="animation-delay:.30s"><span class="fi">🔍</span><div class="ft">Nifty 500 scanner</div><div class="fd">Momentum Score 0-100. BUY, WATCH, AVOID signals instantly.</div></div>
      <div class="fc" style="animation-delay:.36s"><span class="fi">📲</span><div class="ft">Telegram alerts</div><div class="fd">Auto morning and evening alerts with top picks every market day.</div></div>
    </div>
    <script>
    (function(){
      const c=document.getElementById('mf-canvas');
      if(!c)return;
      const ctx=c.getContext('2d');
      let W,H,pts=[],candles=[];
      function resize(){W=c.width=window.innerWidth;H=c.height=window.innerHeight;}
      resize();window.addEventListener('resize',resize);
      for(let i=0;i<80;i++)pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3,r:Math.random()*1.2+.4,col:[[59,130,246],[139,92,246],[0,217,126]][Math.floor(Math.random()*3)],a:Math.random()*.5+.15});
      for(let i=0;i<16;i++)candles.push({x:50+i*70,h:25+Math.random()*100,w:16,up:Math.random()>.5,wk:10+Math.random()*35,a:.03+Math.random()*.05,sp:.25+Math.random()*.4,t:Math.random()*Math.PI*2});
      function draw(){
        ctx.clearRect(0,0,W,H);
        candles.forEach(cd=>{
          cd.t+=.007*cd.sp;const y=H*.58+Math.sin(cd.t)*18;
          const col=cd.up?'0,217,126':'255,69,96';
          ctx.fillStyle=`rgba(${col},${cd.a})`;ctx.fillRect(cd.x-cd.w/2,y-cd.h/2,cd.w,cd.h);
          ctx.strokeStyle=`rgba(${col},${cd.a})`;ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(cd.x,y-cd.h/2-cd.wk);ctx.lineTo(cd.x,y+cd.h/2+cd.wk);ctx.stroke();
        });
        pts.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(${p.col},${p.a})`;ctx.fill();});
        for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<90){ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.strokeStyle=`rgba(59,130,246,${(1-d/90)*.1})`;ctx.lineWidth=.4;ctx.stroke();}}
        requestAnimationFrame(draw);
      }
      draw();
      const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)';}},{threshold:.1}));
      document.querySelectorAll('.mk,.fc,.st').forEach(el=>{el.style.transition='opacity .5s ease,transform .5s ease';obs.observe(el);});
    })();
    </script>
    <div class="cta-3d">
      <div class="ct">Follow @momentumfrenzy</div>
      <div class="cs">Daily trading ideas, breakout alerts and market insights on Instagram.</div>
      <a href="https://instagram.com/momentumfrenzy" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:700;">Follow Now →</a>
    </div>
    <div class="disc">⚠️ <b>Disclaimer:</b> For educational purposes only. Not financial advice. Consult a SEBI-registered advisor before investing.</div>
    <div style="height:20px;position:relative;z-index:10"></div>
    <div class="ftr">© 2025 Momentum Frenzy · Indian Markets · <a href="https://instagram.com/momentumfrenzy" target="_blank">@momentumfrenzy</a></div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.2,1,1.2])
    with c2:
        if st.button("⚡ Open Terminal — Free", use_container_width=True, type="primary"):
            st.session_state.page="terminal"; st.rerun()
        st.markdown("<p style='text-align:center;color:#1e1e2e;font-size:10px;margin-top:6px;'>No signup · 500+ traders · Updated every 4hrs</p>", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
html,body,.stApp{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;}
.block-container{padding:0 1rem 3rem 1rem;max-width:100%;}
header[data-testid="stHeader"]{display:none;}#MainMenu{display:none;}footer{display:none;}

/* Pulse bar */
.pulse-bar{display:flex;gap:10px;flex-wrap:wrap;background:linear-gradient(90deg,#0f0f1a,#111128);
  border-bottom:1px solid #1e1e3a;padding:8px 16px;margin-bottom:0;position:sticky;top:0;z-index:999;}
.pulse-item{display:flex;flex-direction:column;align-items:center;min-width:80px;}
.pulse-label{font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.08em;}
.pulse-value{font-size:13px;font-weight:700;color:#e0e0e0;}
.pulse-up{color:#00e676!important;}.pulse-down{color:#ff5252!important;}

/* Mood bar */
.mood-bar{padding:10px 16px;display:flex;align-items:center;gap:16px;border-bottom:1px solid #1e1e3a;}

/* Section headers */
.sh{font-size:11px;text-transform:uppercase;letter-spacing:.15em;color:#444;
  border-bottom:1px solid #1e1e3a;padding-bottom:5px;margin:20px 0 12px 0;}

/* Pick cards */
.pick-card{border-radius:10px;padding:16px;margin-bottom:10px;border:1px solid;}
.metric-mini{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:8px 12px;text-align:center;}
.metric-mini-label{font-size:10px;color:#555;text-transform:uppercase;}
.metric-mini-value{font-size:15px;font-weight:700;}

/* Ad slot */
.ad-slot{background:#0a0a0c;border:1px dashed #1e1e3a;border-radius:8px;
  padding:20px;text-align:center;color:#333;font-size:11px;margin:16px 0;}

/* Quad */
.quad-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.quad{border-radius:8px;padding:12px;min-height:100px;}
.quad-leading{background:#00380a22;border:1px solid rgba(0,230,118,.3);}
.quad-improving{background:#1a2a0022;border:1px solid rgba(170,255,0,.3);}
.quad-weakening{background:#2a1a0022;border:1px solid rgba(255,170,0,.3);}
.quad-lagging{background:#2a000022;border:1px solid rgba(255,82,82,.3);}
.quad-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;}
.quad-leading .quad-title{color:#00e676;}.quad-improving .quad-title{color:#aaff00;}
.quad-weakening .quad-title{color:#ffaa00;}.quad-lagging .quad-title{color:#ff5252;}
.quad-stock{font-size:11px;padding:2px 5px;border-radius:3px;display:inline-block;margin:2px;background:#ffffff0d;}

div[data-testid="metric-container"]{background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:8px 12px;}
div[data-testid="metric-container"] label{color:#666;font-size:10px;}
.stDataFrame{border-radius:8px;overflow:hidden;}
</style>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_tg(msg):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"HTML"},timeout=10)
    except: pass

def cv(v): return "pulse-up" if v>=0 else "pulse-down"
def ar(v): return "▲" if v>=0 else "▼"

def style_sig(val):
    if val=="BUY":   return "background-color:#00380a;color:#00e676;font-weight:700"
    if val=="WATCH": return "background-color:#2a2200;color:#ffaa00;font-weight:700"
    if val=="AVOID": return "background-color:#2a0000;color:#ff5252;font-weight:700"
    return ""
def style_sc(val):
    if val>=65: return "color:#00e676;font-weight:700"
    if val>=45: return "color:#ffaa00"
    return "color:#ff5252"

@st.cache_data(ttl=14400)
def get_close(t, p="6mo"):
    for _ in range(2):
        try:
            df=yf.download(t,period=p,interval="1d",progress=False,auto_adjust=True)
            r=df['Close'].squeeze().dropna()
            if len(r)>2: return r
        except: pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=14400)
def get_ohlcv(t, p="6mo"):
    for _ in range(2):
        try:
            df=yf.download(t,period=p,interval="1d",progress=False,auto_adjust=True)
            if len(df)>2: return df
        except: pass
    return pd.DataFrame()

@st.cache_data(ttl=14400)
def get_top_picks(tickers, nifty_1m):
    """Generate top swing trade picks with entry/target/SL/RR"""
    picks=[]
    CHUNK=50
    for i in range(0,len(tickers),CHUNK):
        chunk=list(tickers[i:i+CHUNK])
        try:
            raw=(yf.download(chunk[0],period="6mo",interval="1d",progress=False,auto_adjust=True)
                 if len(chunk)==1
                 else yf.download(chunk,period="6mo",interval="1d",progress=False,auto_adjust=True,group_by="ticker"))
            for t in chunk:
                try:
                    if len(chunk)==1:
                        close=raw['Close'].squeeze().dropna()
                        high =raw['High'].squeeze().dropna()
                        low  =raw['Low'].squeeze().dropna()
                        vol  =raw['Volume'].squeeze().dropna()
                    else:
                        close=raw[t]['Close'].squeeze().dropna()
                        high =raw[t]['High'].squeeze().dropna()
                        low  =raw[t]['Low'].squeeze().dropna()
                        vol  =raw[t]['Volume'].squeeze().dropna()
                    if len(close)<50: continue

                    price =float(close.iloc[-1])
                    ema20 =float(close.ewm(span=20).mean().iloc[-1])
                    ema50 =float(close.ewm(span=50).mean().iloc[-1])
                    ema200=float(close.ewm(span=200).mean().iloc[-1])
                    atr   =float((high-low).rolling(14).mean().iloc[-1])

                    delta=close.diff()
                    gain=delta.clip(lower=0).rolling(14).mean()
                    loss=-delta.clip(upper=0).rolling(14).mean()
                    rsi=float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))

                    w52h=float(close.rolling(min(252,len(close))).max().iloc[-1])
                    pfh=round((price/w52h-1)*100,1)

                    va=float(vol.rolling(20).mean().iloc[-1])
                    vs=round(float(vol.iloc[-1])/va,1) if va>0 else 0

                    s1m=float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                    rs=round(s1m-nifty_1m,1)

                    stage2=price>ema20>ema50>ema200
                    vcp=sum([stage2,pfh>-10,vs>=1.5,rs>0])
                    sc=round(min(
                        min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                        min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))

                    if sc<55 or not stage2: continue

                    # Entry / Target / SL calculation
                    entry     = round(price * 1.001, 1)          # slight above current
                    sl        = round(max(ema20 * 0.99, price - atr * 1.5), 1)
                    target1   = round(price + atr * 2, 1)         # 1st target
                    target2   = round(price + atr * 3.5, 1)       # 2nd target
                    risk      = round(entry - sl, 1)
                    reward    = round(target1 - entry, 1)
                    rr        = round(reward / risk, 1) if risk > 0 else 0

                    if rr < 1.5: continue  # only good RR setups

                    setup=("Breakout" if pfh>-3 and vs>=1.5 else
                           "Pullback" if 40<=rsi<=55 else
                           "Vol Surge" if vs>=2 else "Trend")

                    picks.append({
                        "Stock":t.replace(".NS",""),"Price":round(price,1),
                        "Setup":setup,"Score":sc,"RSI":round(rsi,1),
                        "VolSurge":vs,"RS":rs,"52W%":pfh,
                        "Entry":entry,"Target1":target1,"Target2":target2,
                        "SL":sl,"RR":rr,"ATR":round(atr,1)
                    })
                except: pass
        except: pass
    return sorted(picks,key=lambda x:x["Score"],reverse=True)[:10]

@st.cache_data(ttl=14400)
def batch_scan(tickers, nifty_1m):
    all_rows=[]; CHUNK=50
    for i in range(0,len(tickers),CHUNK):
        chunk=list(tickers[i:i+CHUNK])
        try:
            raw=(yf.download(chunk[0],period="6mo",interval="1d",progress=False,auto_adjust=True)
                 if len(chunk)==1
                 else yf.download(chunk,period="6mo",interval="1d",progress=False,auto_adjust=True,group_by="ticker"))
            for t in chunk:
                try:
                    if len(chunk)==1:
                        close=raw['Close'].squeeze().dropna(); vol=raw['Volume'].squeeze().dropna()
                    else:
                        close=raw[t]['Close'].squeeze().dropna(); vol=raw[t]['Volume'].squeeze().dropna()
                    if len(close)<50: continue
                    ema20=float(close.ewm(span=20).mean().iloc[-1])
                    ema50=float(close.ewm(span=50).mean().iloc[-1])
                    ema200=float(close.ewm(span=200).mean().iloc[-1])
                    price=float(close.iloc[-1])
                    delta=close.diff()
                    gain=delta.clip(lower=0).rolling(14).mean()
                    loss=-delta.clip(upper=0).rolling(14).mean()
                    rsi=float(100-(100/(1+gain.iloc[-1]/(loss.iloc[-1]+1e-9))))
                    w52h=float(close.rolling(min(252,len(close))).max().iloc[-1])
                    pfh=round((price/w52h-1)*100,1)
                    va=float(vol.rolling(20).mean().iloc[-1])
                    vs=round(float(vol.iloc[-1])/va,1) if va>0 else 0
                    s1m=float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                    rs=round(s1m-nifty_1m,1)
                    stage2=price>ema20>ema50>ema200
                    vcp=sum([stage2,pfh>-10,vs>=1.5,rs>0])
                    sc=round(min(
                        min(max((rsi-40)/30*25,0),25)+min(max(rs/10*20,0),20)+
                        min(max((vs-1)/2*20,0),20)+vcp/4*25+min(max((10+pfh)/10*10,0),10),100))
                    sig="BUY" if sc>=65 and stage2 else ("WATCH" if sc>=45 else "AVOID")
                    setup=("Breakout" if stage2 and pfh>-3 and vs>=1.5 else
                           "Pullback" if stage2 and 40<=rsi<=55 else
                           "Oversold" if rsi<35 else
                           "Vol Surge" if stage2 and vs>=2 else
                           "Trend" if stage2 else "Base")
                    risk_r=["Low","Medium","High"][min(sum([vs>3,pfh<-20,rsi>75]),2)]
                    all_rows.append({"Stock":t.replace(".NS",""),"Price":round(price,1),
                        "Setup":setup,"Score":sc,"Signal":sig,"RSI":round(rsi,1),
                        "RS":rs,"VolSurge":vs,"52W%":pfh,"Risk":risk_r,
                        "Stage2":"✅" if stage2 else "❌"})
                except: pass
        except: pass
    if not all_rows: return pd.DataFrame()
    return pd.DataFrame(all_rows).sort_values("Score",ascending=False).reset_index(drop=True)

@st.cache_data(ttl=7200)
def get_sector_vol_punch(sectors):
    rows=[]
    for name,ticker in sectors.items():
        try:
            df=yf.download(ticker,period="3mo",interval="1d",progress=False,auto_adjust=True)
            if len(df)<20: continue
            vol=df['Volume'].squeeze().dropna()
            avg20=float(vol.rolling(20).mean().iloc[-1])
            today=float(vol.iloc[-1])
            punch=round(today/avg20,2) if avg20>0 else 1.0
            avg5=float(vol.rolling(5).mean().iloc[-1])
            punch5=round(avg5/avg20,2) if avg20>0 else 1.0
            close=df['Close'].squeeze().dropna()
            pct=float((close.iloc[-1]/close.iloc[-2]-1)*100) if len(close)>=2 else 0
            recent_vol=vol.iloc[-30:]
            recent_avg=float(vol.iloc[-50:-30].mean()) if len(vol)>=50 else avg20
            vol_ratios=(recent_vol/recent_avg).round(2).tolist()
            dates=[str(d.date()) for d in recent_vol.index]
            rows.append({"Sector":name,"Punch":punch,"Punch5":punch5,
                         "PctToday":round(pct,2),"Dates":dates,"VolRatios":vol_ratios})
        except: pass
    return sorted(rows,key=lambda x:x["Punch"],reverse=True)


NIFTY500=[
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS",
    "SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","ITC.NS",
    "BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS",
    "NESTLEIND.NS","WIPRO.NS","ULTRACEMCO.NS","TECHM.NS","HCLTECH.NS","ONGC.NS",
    "NTPC.NS","POWERGRID.NS","COALINDIA.NS","BAJAJFINSV.NS","DIVISLAB.NS",
    "DRREDDY.NS","ADANIENT.NS","ADANIPORTS.NS","AMBUJACEM.NS","APOLLOHOSP.NS",
    "BAJAJ-AUTO.NS","BANKBARODA.NS","BEL.NS","BPCL.NS","BRITANNIA.NS","CANBK.NS",
    "CHOLAFIN.NS","CIPLA.NS","DABUR.NS","DLF.NS","DIXON.NS","EICHERMOT.NS",
    "GAIL.NS","GODREJCP.NS","GRASIM.NS","HAVELLS.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDPETRO.NS","INDUSINDBK.NS","IOC.NS","IRCTC.NS","JSWSTEEL.NS","LTIM.NS",
    "LUPIN.NS","M&M.NS","MOTHERSON.NS","MUTHOOTFIN.NS","NAUKRI.NS","PIDILITIND.NS",
    "PNB.NS","SAIL.NS","SHREECEM.NS","SIEMENS.NS","SRF.NS","TATAPOWER.NS",
    "TATASTEEL.NS","TORNTPHARM.NS","TRENT.NS","VEDL.NS","VOLTAS.NS","ZOMATO.NS",
    "ABB.NS","ABCAPITAL.NS","ACC.NS","APLAPOLLO.NS","AUBANK.NS","AUROPHARMA.NS",
    "BALKRISIND.NS","BANDHANBNK.NS","BERGEPAINT.NS","BIOCON.NS","BOSCHLTD.NS",
    "COFORGE.NS","CROMPTON.NS","CUMMINSIND.NS","DALBHARAT.NS","DEEPAKNTR.NS",
    "ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","FORTIS.NS","GLENMARK.NS",
    "GMRINFRA.NS","HAL.NS","HDFCAMC.NS","HDFCLIFE.NS","IDFCFIRSTB.NS",
    "IEX.NS","INDIANB.NS","INDHOTEL.NS","INDUSTOWER.NS","IRFC.NS","JKCEMENT.NS",
    "JSWENERGY.NS","JUBLFOOD.NS","KEI.NS","LALPATHLAB.NS","LICHSGFIN.NS",
    "LICI.NS","MANAPPURAM.NS","MARICO.NS","MAXHEALTH.NS","MCX.NS","MPHASIS.NS",
    "MRF.NS","NMDC.NS","OBEROIRLTY.NS","OIL.NS","PAGEIND.NS","PERSISTENT.NS",
    "PETRONET.NS","PHOENIX.NS","POLYCAB.NS","PRESTIGE.NS","PVRINOX.NS",
    "RAMCOCEM.NS","RVNL.NS","RECLTD.NS","SBICARD.NS","SBILIFE.NS","SOBHA.NS",
    "SONACOMS.NS","SUPREMEIND.NS","SYNGENE.NS","TATACOMM.NS","TATACHEM.NS",
    "TATACONSUM.NS","TATAELXSI.NS","TATAMOTORS.NS","TATATECH.NS","TIINDIA.NS",
    "TORNTPOWER.NS","TRIDENT.NS","UPL.NS","UTIAMC.NS","VGUARD.NS","ZYDUSLIFE.NS"
]

SECTORS={
    "IT":"^CNXIT","Pvt Bank":"^CNXPVTBANK","PSU Bank":"^CNXPSUBANK",
    "Auto":"^CNXAUTO","Pharma":"^CNXPHARMA","FMCG":"^CNXFMCG",
    "Metal":"^CNXMETAL","Energy":"^CNXENERGY","Realty":"^CNXREALTY",
    "Infra":"^CNXINFRA","Cons Dur":"^CNXCONSUM","PSE":"^CNXPSE",
    "MNC":"^CNXMNC","Media":"^CNXMEDIA"
}


# ── Market Data ───────────────────────────────────────────────────────────────
with st.spinner(""):
    nifty_c=get_close("^NSEI","1y")
    bank_c=get_close("^NSEBANK")
    vix_c=get_close("^INDIAVIX","1mo")

if len(nifty_c)<2 or len(bank_c)<2:
    st.error("⚠️ Data unavailable. Refresh in 1-2 minutes."); st.stop()

nl=float(nifty_c.iloc[-1]); np_=float(nifty_c.iloc[-2]); nchg=(nl/np_-1)*100
bl=float(bank_c.iloc[-1]); bp=float(bank_c.iloc[-2]); bchg=(bl/bp-1)*100
vl=float(vix_c.iloc[-1]) if len(vix_c)>1 else 0
vc_=float(vix_c.iloc[-2]) if len(vix_c)>1 else 0
vchg=(vl/vc_-1)*100 if vc_>0 else 0
ma200=float(nifty_c.rolling(min(200,len(nifty_c))).mean().iloc[-1])
ma50=float(nifty_c.rolling(min(50,len(nifty_c))).mean().iloc[-1])
state="BULL" if nl>ma200 else "BEAR"
sc_={"BULL":"#00e676","BEAR":"#ff5252"}[state]
nifty_1m=float((nifty_c.iloc[-1]/nifty_c.iloc[max(-21,-len(nifty_c))]-1)*100)
nifty_1w=float((nifty_c.iloc[-1]/nifty_c.iloc[max(-5,-len(nifty_c))]-1)*100)

# Market Mood Score
mood_score=0
mood_score += 30 if nl>ma200 else 0
mood_score += 20 if nl>ma50 else 0
mood_score += 15 if nifty_1m>0 else 0
mood_score += 15 if nifty_1w>0 else 0
mood_score += 10 if nchg>0 else 0
mood_score += 10 if vl<15 else (5 if vl<20 else 0)

if mood_score>=70:   mood,mood_c,mood_e="BULLISH","#00e676","🟢"
elif mood_score>=45: mood,mood_c,mood_e="NEUTRAL","#ffaa00","🟡"
else:                mood,mood_c,mood_e="BEARISH","#ff5252","🔴"


# ── PULSE BAR ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pulse-bar">
  <div class="pulse-item"><span class="pulse-label">Nifty 50</span>
    <span class="pulse-value {cv(nchg)}">{nl:,.0f} {ar(nchg)}{abs(nchg):.1f}%</span></div>
  <div class="pulse-item"><span class="pulse-label">BankNifty</span>
    <span class="pulse-value {cv(bchg)}">{bl:,.0f} {ar(bchg)}{abs(bchg):.1f}%</span></div>
  <div class="pulse-item"><span class="pulse-label">VIX</span>
    <span class="pulse-value {cv(-vchg)}">{vl:.1f}</span></div>
  <div class="pulse-item"><span class="pulse-label">MA200</span>
    <span class="pulse-value">{ma200:,.0f}</span></div>
  <div class="pulse-item"><span class="pulse-label">Regime</span>
    <span class="pulse-value" style="color:{sc_};">{state}</span></div>
  <div class="pulse-item"><span class="pulse-label">Mood</span>
    <span class="pulse-value" style="color:{mood_c};">{mood_e} {mood}</span></div>
  <div class="pulse-item" style="margin-left:auto"><span class="pulse-label">Updated</span>
    <span class="pulse-value" style="font-size:10px;color:#444;">{datetime.now().strftime('%d %b %H:%M')}</span></div>
</div>""", unsafe_allow_html=True)

# Header
hc1,hc2,hc3=st.columns([1,8,2])
with hc1: st.image("https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png",width=55)
with hc2:
    st.markdown("<h2 style='color:#00e676;margin:8px 0 2px;font-size:18px;letter-spacing:.04em;'>⚡ MOMENTUM FRENZY TERMINAL</h2>",unsafe_allow_html=True)
    st.markdown("<p style='color:#444;font-size:11px;margin:0;'>Indian Markets · Swing Trading Scanner · Free</p>",unsafe_allow_html=True)
with hc3:
    st.markdown(f"""
    <div style='text-align:right;padding-top:8px;'>
      <a href='https://instagram.com/momentumfrenzy' target='_blank'
         style='color:#00e676;font-size:12px;text-decoration:none;border:1px solid #00e67655;padding:4px 10px;border-radius:4px;'>
        📸 @momentumfrenzy
      </a>
    </div>""", unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3=st.tabs(["🎯 Today's Picks & Scanner","📈 Charts","📊 Sector Intelligence"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PICKS & SCANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Market Mood Banner ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{mood_c}11,#0a0a0f);border:1px solid {mood_c}33;
      border-radius:10px;padding:14px 20px;margin:12px 0;display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
      <div>
        <div style='font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.1em;'>Market Mood Today</div>
        <div style='font-size:28px;font-weight:800;color:{mood_c};'>{mood_e} {mood}</div>
        <div style='font-size:12px;color:#666;margin-top:2px;'>Score: {mood_score}/100</div>
      </div>
      <div style='flex:1;min-width:200px;'>
        <div style='background:#1e1e3a;height:8px;border-radius:4px;margin-bottom:8px;'>
          <div style='background:{mood_c};height:8px;border-radius:4px;width:{mood_score}%;'></div>
        </div>
        <div style='font-size:12px;color:#888;'>
          {"✅ Above MA200 · " if nl>ma200 else "❌ Below MA200 · "}
          {"✅ Above MA50 · " if nl>ma50 else "❌ Below MA50 · "}
          {"✅ VIX low" if vl<15 else "⚠️ VIX elevated" if vl<20 else "🔴 VIX high"}
        </div>
        <div style='font-size:11px;color:#555;margin-top:4px;'>
          {"💡 Good day to look for BUY setups. Momentum is on your side." if mood=="BULLISH" else
           "💡 Selective trades only. Wait for clear setups before entering." if mood=="NEUTRAL" else
           "💡 Caution. Avoid fresh longs. Focus on capital protection."}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── AD SLOT 1 ─────────────────────────────────────────────────────────────
    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    # ── TODAY'S TOP PICKS ─────────────────────────────────────────────────────
    st.markdown("<div class='sh'>🎯 Today's Top Swing Trade Picks</div>", unsafe_allow_html=True)

    with st.spinner("⚡ Finding today's best setups…"):
        picks = get_top_picks(tuple(NIFTY500[:100]), nifty_1m)

    if picks:
        # Top 3 featured picks
        featured = picks[:3]
        pc1,pc2,pc3 = st.columns(3)
        for col,(i,pk) in zip([pc1,pc2,pc3],enumerate(featured)):
            rr_color = "#00e676" if pk["RR"]>=2 else "#ffaa00" if pk["RR"]>=1.5 else "#ff5252"
            setup_emoji = {"Breakout":"🚀","Pullback":"📉","Vol Surge":"💥","Trend":"📈"}.get(pk["Setup"],"📊")
            with col:
                st.markdown(f"""
                <div style='background:#0f0f1a;border:1px solid #00e67633;border-radius:12px;padding:16px;'>
                  <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
                    <div>
                      <div style='font-size:18px;font-weight:800;color:#e0e0e0;'>{pk["Stock"]}</div>
                      <div style='font-size:11px;color:#888;'>{setup_emoji} {pk["Setup"]} · Score: {pk["Score"]}/100</div>
                    </div>
                    <div style='background:#00380a;color:#00e676;font-size:11px;font-weight:700;
                      padding:3px 8px;border-radius:4px;border:1px solid #00e67655;'>BUY</div>
                  </div>
                  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;'>
                    <div style='background:#0a0a0f;border-radius:6px;padding:8px;text-align:center;'>
                      <div style='font-size:9px;color:#555;text-transform:uppercase;'>Entry</div>
                      <div style='font-size:14px;font-weight:700;color:#e0e0e0;'>₹{pk["Entry"]}</div>
                    </div>
                    <div style='background:#0a0a0f;border-radius:6px;padding:8px;text-align:center;'>
                      <div style='font-size:9px;color:#555;text-transform:uppercase;'>Stop Loss</div>
                      <div style='font-size:14px;font-weight:700;color:#ff5252;'>₹{pk["SL"]}</div>
                    </div>
                    <div style='background:#0a0a0f;border-radius:6px;padding:8px;text-align:center;'>
                      <div style='font-size:9px;color:#555;text-transform:uppercase;'>Target 1</div>
                      <div style='font-size:14px;font-weight:700;color:#00e676;'>₹{pk["Target1"]}</div>
                    </div>
                    <div style='background:#0a0a0f;border-radius:6px;padding:8px;text-align:center;'>
                      <div style='font-size:9px;color:#555;text-transform:uppercase;'>Target 2</div>
                      <div style='font-size:14px;font-weight:700;color:#aaff00;'>₹{pk["Target2"]}</div>
                    </div>
                  </div>
                  <div style='display:flex;justify-content:space-between;padding:8px 0;
                    border-top:1px solid #1e1e3a;font-size:12px;'>
                    <span style='color:#888;'>Risk:Reward</span>
                    <span style='color:{rr_color};font-weight:700;'>1 : {pk["RR"]}</span>
                  </div>
                  <div style='display:flex;justify-content:space-between;font-size:11px;color:#555;'>
                    <span>RSI: {pk["RSI"]}</span>
                    <span>Vol: {pk["VolSurge"]}x</span>
                    <span>RS: {pk["RS"]:+.1f}%</span>
                  </div>
                </div>""", unsafe_allow_html=True)

        # More picks table
        if len(picks)>3:
            st.markdown("<div class='sh' style='margin-top:16px;'>📋 More Setups</div>", unsafe_allow_html=True)
            more_df=pd.DataFrame(picks[3:]).rename(columns={
                "Stock":"Stock","Price":"CMP","Setup":"Setup","Score":"Score",
                "Entry":"Entry ₹","SL":"SL ₹","Target1":"T1 ₹","Target2":"T2 ₹","RR":"R:R"
            })[["Stock","CMP","Setup","Score","Entry ₹","SL ₹","T1 ₹","T2 ₹","R:R","RSI","VolSurge"]]
            st.dataframe(more_df.style.map(style_sc,subset=["Score"])
                .format({"CMP":"{:.1f}","Entry ₹":"{:.1f}","SL ₹":"{:.1f}","T1 ₹":"{:.1f}","T2 ₹":"{:.1f}","R:R":"{:.1f}","RSI":"{:.1f}","VolSurge":"{:.1f}x"}),
                use_container_width=True, height=280)
    else:
        st.info("No high-quality setups found today. Market may be in consolidation — wait for better opportunities.")

    st.markdown("<p style='font-size:10px;color:#333;text-align:right;margin-top:4px;'>⚠️ Educational only. Not financial advice. Do your own research.</p>", unsafe_allow_html=True)

    # ── AD SLOT 2 ─────────────────────────────────────────────────────────────
    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    # ── FULL SCANNER ─────────────────────────────────────────────────────────
    st.markdown("<div class='sh'>🔍 Full Momentum Scanner</div>", unsafe_allow_html=True)

    fc1,fc2,fc3,fc4=st.columns(4)
    with fc1: sf=st.selectbox("Signal",["All","BUY","WATCH","AVOID"])
    with fc2: rf=st.selectbox("Risk",["All","Low","Medium","High"])
    with fc3: setupf=st.selectbox("Setup",["All","Breakout","Pullback","Vol Surge","Trend","Oversold","Base"])
    with fc4: tn=st.selectbox("Universe",["Top 50","Top 100","Top 150"],index=0)

    tm={"Top 50":50,"Top 100":100,"Top 150":150}
    with st.spinner(f"Scanning {tm[tn]} stocks…"):
        scan_df=batch_scan(tuple(NIFTY500[:tm[tn]]),nifty_1m)

    if len(scan_df)>0:
        filt=scan_df.copy()
        if sf!="All": filt=filt[filt["Signal"]==sf]
        if rf!="All": filt=filt[filt["Risk"]==rf]
        if setupf!="All": filt=filt[filt["Setup"]==setupf]
        st.dataframe(filt.style.map(style_sig,subset=["Signal"]).map(style_sc,subset=["Score"])
            .format({"Price":"{:.1f}","RSI":"{:.1f}","RS":"{:+.1f}","VolSurge":"{:.1f}x","52W%":"{:.1f}%","Score":"{:.0f}"}),
            use_container_width=True, height=360)
        st.caption(f"Showing {len(filt)} of {len(scan_df)} stocks · Data: Yahoo Finance · Cached 4hrs")
    else:
        st.warning("No data. Try refreshing.")

    # ── AD SLOT 3 ─────────────────────────────────────────────────────────────
    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

    # ── INSTAGRAM CTA ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0f0f1a,#1a0f2a);border:1px solid #00e67633;
      border-radius:12px;padding:20px;text-align:center;margin:16px 0;'>
      <div style='font-size:20px;margin-bottom:8px;'>📸</div>
      <div style='font-size:16px;font-weight:700;color:#e0e0e0;margin-bottom:6px;'>Follow @momentumfrenzy on Instagram</div>
      <div style='font-size:13px;color:#666;margin-bottom:12px;'>Daily trading ideas, breakout alerts and market analysis</div>
      <a href='https://instagram.com/momentumfrenzy' target='_blank'
         style='background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:#fff;
         padding:8px 24px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;'>
        Follow Now
      </a>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='sh'>📈 Stock Chart Viewer</div>", unsafe_allow_html=True)
    cc1,cc2,cc3=st.columns([2,1,1])
    with cc1: sel=st.selectbox("Stock",[t.replace(".NS","") for t in NIFTY500])
    with cc2: per=st.selectbox("Period",["3mo","6mo","1y"])
    with cc3: ctype=st.selectbox("Type",["Candles","Line"])

    sdf=get_ohlcv(sel+".NS",per)
    if len(sdf)>0:
        sc2_=sdf['Close'].squeeze(); sv_=sdf['Volume'].squeeze()
        fig2=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.75,0.25],vertical_spacing=0.03)
        if ctype=="Candles":
            fig2.add_trace(go.Candlestick(x=sdf.index,open=sdf['Open'].squeeze(),
                high=sdf['High'].squeeze(),low=sdf['Low'].squeeze(),close=sc2_,name=sel,
                increasing_line_color="#00e676",decreasing_line_color="#ff5252"),row=1,col=1)
        else:
            fig2.add_trace(go.Scatter(x=sdf.index,y=sc2_,name=sel,line=dict(color="#00e676",width=1.5)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc2_.ewm(span=20).mean(),name="EMA20",line=dict(color="#00e676",width=1.2)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc2_.ewm(span=50).mean(),name="EMA50",line=dict(color="#ffaa00",width=1.2)),row=1,col=1)
        fig2.add_trace(go.Scatter(x=sdf.index,y=sc2_.ewm(span=200).mean(),name="EMA200",line=dict(color="#ff5252",width=1.2)),row=1,col=1)
        vc2=["rgba(0,230,118,0.4)" if c>=o else "rgba(255,82,82,0.4)"
             for c,o in zip(sdf['Close'].squeeze(),sdf['Open'].squeeze())]
        fig2.add_trace(go.Bar(x=sdf.index,y=sv_,marker_color=vc2,showlegend=False),row=2,col=1)
        fig2.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",height=500,
            margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#1a1a2e",rangeslider=dict(visible=False)),
            xaxis2=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"),yaxis2=dict(gridcolor="#1a1a2e"),
            legend=dict(bgcolor="#0f0f1a",bordercolor="#1e1e3a",font=dict(size=11)))
        st.plotly_chart(fig2,use_container_width=True)

        # Show pick data if available
        if picks and sel in [p["Stock"] for p in picks]:
            pk=[p for p in picks if p["Stock"]==sel][0]
            m1,m2,m3,m4,m5,m6=st.columns(6)
            m1.metric("Entry",f"₹{pk['Entry']}")
            m2.metric("Target 1",f"₹{pk['Target1']}")
            m3.metric("Target 2",f"₹{pk['Target2']}")
            m4.metric("Stop Loss",f"₹{pk['SL']}")
            m5.metric("R:R",f"1:{pk['RR']}")
            m6.metric("Score",f"{pk['Score']}/100")

    st.markdown("<div class='sh' style='margin-top:16px;'>🇮🇳 Nifty 50 — 1 Year</div>", unsafe_allow_html=True)
    ndf=get_ohlcv("^NSEI","1y")
    if len(ndf)>0:
        nc_=ndf['Close'].squeeze()
        fig3=go.Figure()
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_,name="Nifty",
            line=dict(color="#00e676",width=1.5),fill="tozeroy",fillcolor="rgba(0,230,118,0.07)"))
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_.rolling(200).mean(),name="MA200",line=dict(color="#ff5252",dash="dash",width=1)))
        fig3.add_trace(go.Scatter(x=ndf.index,y=nc_.rolling(50).mean(),name="MA50",line=dict(color="#ffaa00",dash="dot",width=1)))
        fig3.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",height=300,
            margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e"),
            legend=dict(bgcolor="#0f0f1a",bordercolor="#1e1e3a",font=dict(size=11)))
        st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECTOR INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='sh'>📊 Sector Rotation — 4 Quadrant</div>", unsafe_allow_html=True)

    with st.spinner("Loading sectors…"):
        rows=[]
        for name,ticker in SECTORS.items():
            try:
                close=get_close(ticker,"3mo")
                if len(close)<20: continue
                r1m=float((close.iloc[-1]/close.iloc[max(-21,-len(close))]-1)*100)
                r3m=float((close.iloc[-1]/close.iloc[0]-1)*100)
                rows.append({"Sector":name,"1M%":round(r1m,2),"3M%":round(r3m,2),"Score":round(r1m*.6+r3m*.4,2)})
            except: pass

    sector_df=pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)
    if len(sector_df)>0:
        med1=sector_df["1M%"].median(); med3=sector_df["3M%"].median()
        leading=sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]>=med3)]["Sector"].tolist()
        improving=sector_df[(sector_df["1M%"]>=med1)&(sector_df["3M%"]<med3)]["Sector"].tolist()
        weakening=sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]>=med3)]["Sector"].tolist()
        lagging=sector_df[(sector_df["1M%"]<med1)&(sector_df["3M%"]<med3)]["Sector"].tolist()

        def qs(lst):
            out=""
            for s in lst:
                r=sector_df[sector_df["Sector"]==s].iloc[0]
                out+=f'<span class="quad-stock">{s} <b>{r["1M%"]:+.1f}%</b></span>'
            return out or "<span style='color:#444'>—</span>"

        ql,qr=st.columns([1.2,1])
        with ql:
            st.markdown(f"""<div class="quad-grid">
              <div class="quad quad-leading"><div class="quad-title">🚀 Leading</div>{qs(leading)}</div>
              <div class="quad quad-improving"><div class="quad-title">📈 Improving</div>{qs(improving)}</div>
              <div class="quad quad-weakening"><div class="quad-title">⚠️ Weakening</div>{qs(weakening)}</div>
              <div class="quad quad-lagging"><div class="quad-title">📉 Lagging</div>{qs(lagging)}</div>
            </div>""",unsafe_allow_html=True)
        with qr:
            fig_s=go.Figure(go.Bar(x=sector_df["Sector"],y=sector_df["Score"],
                marker_color=["#00e676" if s>0 else "#ff5252" for s in sector_df["Score"]],
                text=[f"{s:+.1f}" for s in sector_df["Score"]],textposition="outside"))
            fig_s.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
                height=280,margin=dict(l=0,r=0,t=10,b=0),
                yaxis=dict(gridcolor="#1a1a2e"),xaxis=dict(gridcolor="#1a1a2e"))
            st.plotly_chart(fig_s,use_container_width=True)

    # Volume Punch
    st.markdown("<div class='sh'>💥 Sector Volume Punch</div>", unsafe_allow_html=True)
    with st.spinner("Analyzing volume…"):
        vp=get_sector_vol_punch(SECTORS)

    if vp:
        vp1,vp2,vp3=st.columns(3)
        for col,item in zip([vp1,vp2,vp3],vp[:3]):
            bc="#ff5252" if item["Punch"]>=3 else "#ffaa00" if item["Punch"]>=2 else "#aaff00" if item["Punch"]>=1.5 else "#888"
            pc2="#00e676" if item["PctToday"]>=0 else "#ff5252"
            with col:
                st.markdown(f"""
                <div style='background:#0f0f1a;border:1px solid {bc}33;border-radius:10px;padding:14px;'>
                  <div style='font-size:14px;font-weight:700;color:#e0e0e0;margin-bottom:4px;'>{item["Sector"]}</div>
                  <div style='font-size:24px;font-weight:800;color:{bc};'>{item["Punch"]}x</div>
                  <div style='font-size:11px;color:#888;'>Today: <span style='color:{pc2};font-weight:600;'>{item["PctToday"]:+.2f}%</span></div>
                </div>""", unsafe_allow_html=True)

        sec_names=[d["Sector"] for d in vp]
        vol_ratios=[d["Punch"] for d in vp]
        fig_vp=go.Figure()
        fig_vp.add_trace(go.Bar(x=sec_names,y=vol_ratios,
            marker_color=["#ff5252" if v>=3 else "#ffaa00" if v>=2 else "#aaff00" if v>=1.5 else "#333" for v in vol_ratios],
            text=[f"{v:.1f}x" for v in vol_ratios],textposition="outside"))
        fig_vp.add_hline(y=1.0,line_color="#555",line_dash="dot")
        fig_vp.add_hline(y=2.0,line_color="rgba(255,170,0,0.4)",line_dash="dash")
        fig_vp.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
            height=300,margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#1a1a2e"),yaxis=dict(gridcolor="#1a1a2e",title="Vol Ratio vs 20D Avg"))
        st.plotly_chart(fig_vp,use_container_width=True)

        sel_sec=st.selectbox("Sector History",[d["Sector"] for d in vp])
        sd=next((d for d in vp if d["Sector"]==sel_sec),None)
        if sd and sd["VolRatios"]:
            fig_h=go.Figure(go.Bar(
                x=sd["Dates"],y=sd["VolRatios"],
                marker_color=["#ff5252" if v>=3 else "#ffaa00" if v>=2 else "#00e676" if v>=1.5 else "#333" for v in sd["VolRatios"]]))
            fig_h.add_hline(y=1.0,line_color="#555",line_dash="dot")
            fig_h.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="#0a0a0f",font_color="#888",
                height=250,margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="#1a1a2e",tickangle=-45),yaxis=dict(gridcolor="#1a1a2e"))
            st.plotly_chart(fig_h,use_container_width=True)

    st.markdown("<div class='ad-slot'>[ Advertisement ]</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style='text-align:center;padding:20px;border-top:1px solid #1e1e3a;margin-top:20px;'>
  <p style='color:#333;font-size:11px;margin:0;'>
    ⚠️ For educational purposes only. Not financial advice. Always DYOR.<br>
    © 2025 Momentum Frenzy · <a href='https://instagram.com/momentumfrenzy' style='color:#00e676;'>@momentumfrenzy</a> ·
    Data: Yahoo Finance · {datetime.now().strftime('%d %b %Y')}
  </p>
</div>""", unsafe_allow_html=True)
