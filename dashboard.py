<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Momentum Frenzy — Indian Market Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--green:#00d97e;--red:#ff4560;--blue:#3b82f6;--purple:#8b5cf6;--gold:#f59e0b;--bg:#060609;--bg2:#0d0d14;--border:#1a1a26}
body{background:var(--bg);color:#e0e0f0;font-family:'Inter',sans-serif;overflow-x:hidden}

/* ── Animated canvas background ── */
#bg-canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:.45}

/* ── Ticker ── */
.ticker{position:relative;z-index:10;background:rgba(8,8,14,.95);border-bottom:1px solid var(--border);height:32px;overflow:hidden;display:flex;align-items:center}
.ticker-track{display:flex;animation:scroll 45s linear infinite;width:max-content}
.ti{display:flex;align-items:center;gap:6px;padding:0 18px;font-size:10px;font-family:'JetBrains Mono',monospace;white-space:nowrap;border-right:1px solid #1a1a26}
.tn{color:#333350}.tv{color:#b0b0c8;font-weight:500}.tu{color:var(--green)}.td{color:var(--red)}
@keyframes scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* ── Hero ── */
.hero{position:relative;z-index:10;min-height:90vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 20px 48px;overflow:hidden}

/* Floating orbs */
.orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:.12;animation:floatOrb 12s ease-in-out infinite;pointer-events:none}
.orb1{width:500px;height:500px;background:var(--blue);top:-100px;left:-150px;animation-delay:0s}
.orb2{width:400px;height:400px;background:var(--purple);top:50%;right:-120px;animation-delay:-4s}
.orb3{width:350px;height:350px;background:var(--green);bottom:-80px;left:30%;animation-delay:-8s}
@keyframes floatOrb{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-20px) scale(1.05)}66%{transform:translate(-20px,30px) scale(.97)}}

/* Grid lines */
.grid-lines{position:absolute;inset:0;background-image:linear-gradient(rgba(59,130,246,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,.04) 1px,transparent 1px);background-size:60px 60px;mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 30%,transparent 100%)}

.logo-wrap{display:flex;align-items:center;gap:14px;margin-bottom:24px;animation:fadeDown .7s ease both}
.logo-img{width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,.08);transition:transform .4s,box-shadow .4s}
.logo-img:hover{transform:scale(1.1) rotate(3deg);box-shadow:0 0 32px rgba(59,130,246,.4)}
.logo-text{font-size:clamp(32px,5vw,52px);font-weight:900;letter-spacing:-2px;line-height:1}
.logo-grd{background:linear-gradient(135deg,#3b82f6,#8b5cf6,#00d97e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;background-size:200%;animation:gradShift 5s ease infinite}
@keyframes gradShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

@keyframes fadeDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

.live-badge{display:inline-flex;align-items:center;gap:7px;background:rgba(0,217,126,.08);border:1px solid rgba(0,217,126,.25);color:var(--green);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;padding:5px 16px;border-radius:20px;margin-bottom:20px;animation:fadeDown .7s .1s ease both;opacity:0}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:pulseDot 1.8s ease-in-out infinite}
@keyframes pulseDot{0%,100%{opacity:1;box-shadow:0 0 8px var(--green)}50%{opacity:.3;box-shadow:0 0 2px var(--green)}}

.hero-title{font-size:clamp(36px,7vw,72px);font-weight:900;line-height:1.08;letter-spacing:-2px;margin-bottom:18px;animation:fadeUp .8s .18s ease both;opacity:0}
.hero-title .line1{display:block;color:#f0f0ff}
.hero-title .line2{display:block;background:linear-gradient(90deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

.hero-sub{font-size:clamp(14px,2.2vw,18px);color:#5a5a78;max-width:540px;margin:0 auto 36px;line-height:1.75;animation:fadeUp .8s .26s ease both;opacity:0}

.hero-btns{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;animation:fadeUp .8s .34s ease both;opacity:0}
.btn-primary{position:relative;overflow:hidden;background:linear-gradient(135deg,#3b82f6,#6d28d9);color:#fff;border:none;font-size:14px;font-weight:700;padding:14px 32px;border-radius:10px;cursor:pointer;font-family:inherit;letter-spacing:.3px;transition:transform .25s,box-shadow .25s}
.btn-primary::after{content:'';position:absolute;inset:0;background:linear-gradient(135deg,transparent 40%,rgba(255,255,255,.15));opacity:0;transition:opacity .3s}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(59,130,246,.45)}
.btn-primary:hover::after{opacity:1}
.btn-primary:active{transform:translateY(-1px)}
.btn-insta{background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:#fff;border:none;font-size:13px;font-weight:700;padding:14px 24px;border-radius:10px;cursor:pointer;font-family:inherit;transition:transform .25s,box-shadow .25s}
.btn-insta:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(131,58,180,.4)}

/* Scroll indicator */
.scroll-ind{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:6px;animation:fadeIn 1s .8s ease both;opacity:0}
.scroll-ind span{font-size:9px;color:#333350;letter-spacing:2px;text-transform:uppercase}
.scroll-arrow{width:20px;height:20px;border-right:2px solid #2a2a40;border-bottom:2px solid #2a2a40;transform:rotate(45deg);animation:bounce 1.6s ease-in-out infinite}
@keyframes bounce{0%,100%{transform:rotate(45deg) translateY(0)}50%{transform:rotate(45deg) translateY(6px)}}

/* ── Market strip ── */
.mkt-wrap{position:relative;z-index:10;padding:0 20px;max-width:1040px;margin:-20px auto 0}
.mkt-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}
.mkt-card{background:rgba(13,13,20,.9);border:1px solid #1e1e2c;border-radius:10px;padding:12px 14px;backdrop-filter:blur(10px);transition:border-color .3s,transform .3s,box-shadow .3s;cursor:default;animation:fadeUp .5s ease both;opacity:0}
.mkt-card:hover{border-color:#2e2e46;transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.5)}
.mn{font-size:9px;color:#33334a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.mv{font-size:15px;font-weight:700;color:#d0d0e8;margin-bottom:2px}
.mc{font-size:11px;font-weight:600}
.up{color:var(--green)}.dn{color:var(--red)}

/* ── Stats ── */
.stats-wrap{position:relative;z-index:10;background:rgba(10,10,16,.8);border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin:40px 0;padding:36px 20px;backdrop-filter:blur(8px)}
.stats{display:flex;flex-wrap:wrap;justify-content:center;gap:40px;max-width:800px;margin:0 auto}
.stat{text-align:center}
.stat-n{font-size:40px;font-weight:900;line-height:1;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:countUp .6s ease both;opacity:0}
.stat-l{font-size:10px;color:#333350;text-transform:uppercase;letter-spacing:1.5px;margin-top:5px}
@keyframes countUp{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}}

/* ── Features ── */
.feats-wrap{position:relative;z-index:10;padding:0 20px 50px;max-width:1040px;margin:0 auto}
.feats-title{font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#33334a;margin-bottom:20px;display:flex;align-items:center;gap:12px}
.feats-title::after{content:'';flex:1;height:1px;background:linear-gradient(to right,var(--border),transparent)}
.feats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.feat{background:rgba(13,13,20,.85);border:1px solid #1e1e2c;border-radius:12px;padding:20px;backdrop-filter:blur(6px);transition:border-color .3s,transform .3s,box-shadow .3s;animation:fadeUp .5s ease both;opacity:0;position:relative;overflow:hidden}
.feat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,.4),transparent);transform:scaleX(0);transition:transform .4s}
.feat:hover{border-color:#2e2e46;transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.5)}
.feat:hover::before{transform:scaleX(1)}
.fi{font-size:24px;margin-bottom:10px;display:block;transition:transform .3s}
.feat:hover .fi{transform:scale(1.15)}
.ft{font-size:13px;font-weight:700;color:#d0d0e8;margin-bottom:6px}
.fd{font-size:11px;color:#3a3a56;line-height:1.65}

/* ── Ad slot ── */
.ad-wrap{position:relative;z-index:10;padding:0 20px;max-width:1040px;margin:0 auto 20px}
.ad-slot{background:rgba(10,10,16,.6);border:1px dashed #1e1e2c;border-radius:8px;height:72px;display:flex;align-items:center;justify-content:center;color:#1e1e2c;font-size:10px;letter-spacing:1.5px;text-transform:uppercase}

/* ── Nav ── */
.news-nav{position:relative;z-index:10;background:rgba(10,10,16,.9);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:0 20px;display:flex;align-items:center;gap:5px;height:46px;flex-wrap:wrap;overflow:hidden;backdrop-filter:blur(8px)}
.nf{background:transparent;border:1px solid transparent;color:#33334a;font-family:inherit;font-size:11px;padding:4px 12px;border-radius:4px;cursor:pointer;font-weight:500;transition:all .2s}
.nf:hover{border-color:#2a2a3e;color:#9090b0}
.nf.active{border-color:rgba(59,130,246,.4);background:rgba(59,130,246,.1);color:var(--blue)}
.ref-btn{margin-left:auto;background:transparent;border:1px solid rgba(0,217,126,.2);color:var(--green);font-size:11px;padding:4px 12px;border-radius:4px;cursor:pointer;display:flex;align-items:center;gap:5px;font-family:inherit;font-weight:500;transition:all .2s}
.ref-btn:hover{background:rgba(0,217,126,.06)}
.ref-btn:disabled{opacity:.35;cursor:not-allowed}
.spin{display:inline-block;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── News ── */
.news-wrap{position:relative;z-index:10;padding:20px 20px 60px;max-width:1040px;margin:0 auto}
.news-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.news-card{background:rgba(13,13,20,.9);border:1px solid #1e1e2c;border-radius:11px;padding:15px;display:flex;flex-direction:column;gap:8px;backdrop-filter:blur(6px);transition:border-color .3s,transform .3s,box-shadow .3s;animation:fadeUp .5s ease both;opacity:0;cursor:default;position:relative;overflow:hidden}
.news-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--acc,#3b82f6);transform:scaleX(.3);transform-origin:left;transition:transform .4s}
.news-card:hover{border-color:#2a2a40;transform:translateY(-3px);box-shadow:0 8px 28px rgba(0,0,0,.5)}
.news-card:hover::before{transform:scaleX(1)}
.nc-top{display:flex;justify-content:space-between}
.nc-src{font-size:9px;color:#2a2a42;text-transform:uppercase;letter-spacing:.5px}
.nc-time{font-size:9px;color:#22223a}
.nc-hl{font-size:13px;font-weight:700;color:#d8d8f0;line-height:1.35}
.nc-ft{display:flex;align-items:center;gap:6px;margin-top:2px}
.nc-tag{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:2px 7px;border-radius:3px}
.nc-link{font-size:10px;color:var(--blue);text-decoration:none;margin-left:auto;opacity:0;transition:opacity .2s}
.news-card:hover .nc-link{opacity:1}
.shim{background:rgba(13,13,20,.9);border:1px solid #1e1e2c;border-radius:11px;padding:15px;min-height:120px}
.sl{height:9px;border-radius:4px;margin-bottom:8px;background:linear-gradient(90deg,#111118 25%,#17171f 50%,#111118 75%);background-size:200%;animation:shim 1.5s infinite}
.sl.s{width:36%}.sl.m{width:58%}
@keyframes shim{to{background-position:-200% 0}}
.err{grid-column:1/-1;background:rgba(18,6,6,.8);border:1px solid rgba(255,69,96,.15);border-radius:11px;padding:24px;text-align:center;font-size:12px;color:#ff8095}
.err button{margin-top:10px;background:transparent;border:1px solid rgba(255,69,96,.3);color:var(--red);padding:5px 14px;border-radius:4px;cursor:pointer;font-family:inherit;font-size:11px}

/* ── CTA ── */
.cta-wrap{position:relative;z-index:10;padding:20px 20px 60px;max-width:600px;margin:0 auto;text-align:center}
.cta-box{background:rgba(13,8,22,.85);border:1px solid rgba(139,92,246,.2);border-radius:16px;padding:36px;backdrop-filter:blur(10px);transition:border-color .3s,box-shadow .3s}
.cta-box:hover{border-color:rgba(139,92,246,.45);box-shadow:0 12px 40px rgba(109,40,217,.2)}
.cta-title{font-size:22px;font-weight:800;color:#e0e0f8;margin-bottom:8px}
.cta-sub{font-size:13px;color:#4a4a66;margin-bottom:20px;line-height:1.6}

/* ── Footer ── */
.footer{position:relative;z-index:10;border-top:1px solid var(--border);padding:20px;text-align:center;font-size:10px;color:#22223a;letter-spacing:.5px}
.footer a{color:#22223a;text-decoration:none}
</style>
</head>
<body>

<canvas id="bg-canvas"></canvas>

<!-- Ticker -->
<div class="ticker">
  <div class="ticker-track" id="ticker"></div>
</div>

<!-- Hero -->
<section class="hero">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
  <div class="grid-lines"></div>

  <div class="logo-wrap">
    <img class="logo-img" src="https://raw.githubusercontent.com/sonuravi2705-creator/trading-terminal/main/logo.png" alt="MF" onerror="this.style.display='none'">
    <div class="logo-text">MOMENTUM<br><span class="logo-grd">FRENZY</span></div>
  </div>

  <div class="live-badge"><span class="live-dot"></span> Live Indian Markets</div>

  <h1 class="hero-title">
    <span class="line1">Find your next trade</span>
    <span class="line2">before the market moves</span>
  </h1>
  <p class="hero-sub">Professional momentum scanner for NSE swing traders. Sector rotation, breakout radar and daily picks — all free.</p>
  <div class="hero-btns">
    <button class="btn-primary" onclick="window.open('https://momentumfrenzy.online')">⚡ Open Terminal — Free</button>
    <button class="btn-insta" onclick="window.open('https://instagram.com/momentumfrenzy')">📸 @momentumfrenzy</button>
  </div>

  <div class="scroll-ind">
    <span>Scroll</span>
    <div class="scroll-arrow"></div>
  </div>
</section>

<!-- Market strip -->
<div class="mkt-wrap">
  <div class="mkt-strip" id="mkt-strip"></div>
</div>

<!-- Stats -->
<div class="stats-wrap">
  <div class="stats">
    <div class="stat"><div class="stat-n" style="animation-delay:.1s">500+</div><div class="stat-l">Stocks Scanned</div></div>
    <div class="stat"><div class="stat-n" style="animation-delay:.2s">14</div><div class="stat-l">Sectors Tracked</div></div>
    <div class="stat"><div class="stat-n" style="animation-delay:.3s">Free</div><div class="stat-l">Always</div></div>
    <div class="stat"><div class="stat-n" style="animation-delay:.4s">2×</div><div class="stat-l">Daily Alerts</div></div>
  </div>
</div>

<!-- Features -->
<div class="feats-wrap">
  <div class="feats-title">What you get</div>
  <div class="feats-grid" id="feats-grid"></div>
</div>

<!-- Ad -->
<div class="ad-wrap"><div class="ad-slot">Advertisement</div></div>

<!-- Nav -->
<div class="news-nav" id="news-nav"></div>

<!-- News -->
<div class="news-wrap">
  <div class="news-grid" id="news-grid"></div>
</div>

<!-- Ad -->
<div class="ad-wrap"><div class="ad-slot">Advertisement</div></div>

<!-- CTA -->
<div class="cta-wrap">
  <div class="cta-box">
    <div class="cta-title">Follow @momentumfrenzy</div>
    <div class="cta-sub">Daily trading ideas, breakout alerts and market insights on Instagram. Join 10,000+ traders.</div>
    <button class="btn-insta" onclick="window.open('https://instagram.com/momentumfrenzy')">Follow Now →</button>
  </div>
</div>

<!-- Footer -->
<div class="footer">© 2025 MOMENTUMFRENZY · For informational purposes only. Not SEBI-registered investment advice. · <a href="https://instagram.com/momentumfrenzy" target="_blank">@momentumfrenzy</a></div>

<script>
// ── Animated canvas background ──────────────────────────────────────────────
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let W, H, particles = [], lines = [];

function resize(){
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

class Particle {
  constructor(){this.reset()}
  reset(){
    this.x = Math.random()*W; this.y = Math.random()*H;
    this.vx = (Math.random()-.5)*.35; this.vy = (Math.random()-.5)*.35;
    this.r = Math.random()*1.5+.5;
    const c = [[59,130,246],[139,92,246],[0,217,126]][Math.floor(Math.random()*3)];
    this.color = c; this.alpha = Math.random()*.6+.2;
  }
  update(){
    this.x += this.vx; this.y += this.vy;
    if(this.x<0||this.x>W||this.y<0||this.y>H) this.reset();
  }
  draw(){
    ctx.beginPath();
    ctx.arc(this.x,this.y,this.r,0,Math.PI*2);
    ctx.fillStyle = `rgba(${this.color},${this.alpha})`;
    ctx.fill();
  }
}

for(let i=0;i<120;i++) particles.push(new Particle());

function drawLines(){
  const maxDist = 100;
  for(let i=0;i<particles.length;i++){
    for(let j=i+1;j<particles.length;j++){
      const dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
      const dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<maxDist){
        const a=(1-dist/maxDist)*.15;
        ctx.beginPath();
        ctx.moveTo(particles[i].x,particles[i].y);
        ctx.lineTo(particles[j].x,particles[j].y);
        ctx.strokeStyle=`rgba(59,130,246,${a})`;
        ctx.lineWidth=.5;
        ctx.stroke();
      }
    }
  }
}

// Candlestick animation
const candles = [];
for(let i=0;i<20;i++){
  candles.push({
    x: 60+i*60, baseY: H*.6,
    h: 30+Math.random()*120,
    w: 18, up: Math.random()>.5,
    wick: 15+Math.random()*40,
    alpha: .04+Math.random()*.06,
    speed: .3+Math.random()*.5, t: Math.random()*Math.PI*2
  });
}

function drawCandles(){
  candles.forEach(c=>{
    c.t += .008*c.speed;
    const y = c.baseY + Math.sin(c.t)*20;
    const color = c.up ? '0,217,126' : '255,69,96';
    ctx.fillStyle = `rgba(${color},${c.alpha})`;
    ctx.fillRect(c.x-c.w/2, y-c.h/2, c.w, c.h);
    ctx.strokeStyle = `rgba(${color},${c.alpha})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(c.x, y-c.h/2-c.wick);
    ctx.lineTo(c.x, y+c.h/2+c.wick);
    ctx.stroke();
  });
}

function animate(){
  ctx.clearRect(0,0,W,H);
  drawCandles();
  particles.forEach(p=>{p.update();p.draw();});
  drawLines();
  requestAnimationFrame(animate);
}
animate();


// ── Ticker ──────────────────────────────────────────────────────────────────
const INDICES=[
  {n:'NIFTY 50',v:'24,749',c:'+0.94%',up:true},{n:'BANK NIFTY',v:'53,210',c:'+1.21%',up:true},
  {n:'VIX',v:'12.84',c:'-5.2%',up:false},{n:'SENSEX',v:'81,224',c:'+0.87%',up:true},
  {n:'NIFTY IT',v:'35,841',c:'-0.38%',up:false},{n:'USD/INR',v:'83.48',c:'-0.14%',up:false},
  {n:'MIDCAP',v:'54,103',c:'+0.72%',up:true},{n:'GOLD',v:'₹71,240',c:'+0.31%',up:true},
  {n:'CRUDE',v:'$78.42',c:'-0.82%',up:false},{n:'NIFTY MID',v:'54,103',c:'+0.72%',up:true},
];
const tickerEl=document.getElementById('ticker');
[...INDICES,...INDICES].forEach(x=>{
  tickerEl.innerHTML+=`<span class="ti"><span class="tn">${x.n}</span><span class="tv">${x.v}</span><span class="${x.up?'tu':'td'}">${x.c}</span></span>`;
});


// ── Market strip ─────────────────────────────────────────────────────────────
const MKT=[
  {n:'NIFTY 50',v:'24,749',c:'+0.94%',up:true},{n:'BANK NIFTY',v:'53,210',c:'+1.21%',up:true},
  {n:'VIX',v:'12.84',c:'-5.2%',up:false},{n:'USD/INR',v:'83.48',c:'-0.14%',up:false},
  {n:'NIFTY IT',v:'35,841',c:'-0.38%',up:false},{n:'MIDCAP',v:'54,103',c:'+0.72%',up:true},
];
const mktEl=document.getElementById('mkt-strip');
MKT.forEach((m,i)=>{
  mktEl.innerHTML+=`<div class="mkt-card" style="animation-delay:${i*.08}s">
    <div class="mn">${m.n}</div><div class="mv">${m.v}</div>
    <div class="mc ${m.up?'up':'dn'}">${m.c}</div></div>`;
});


// ── Features ─────────────────────────────────────────────────────────────────
const FEATS=[
  {i:'🎯',t:"Today's top picks",d:'Entry, target, stop-loss and risk:reward — ready every morning.'},
  {i:'📊',t:'Sector intelligence',d:'4-Quadrant rotation showing which sectors lead, improve or lag.'},
  {i:'💥',t:'Volume punch radar',d:'Catch institutional activity before the crowd notices.'},
  {i:'📈',t:'Professional charts',d:'Candlestick + EMA 20/50/200 for any Nifty 500 stock.'},
  {i:'🔍',t:'Nifty 500 scanner',d:'Momentum Score 0–100. BUY, WATCH, AVOID signals instantly.'},
  {i:'📲',t:'Telegram alerts',d:'Auto morning and evening alerts with top picks every market day.'},
];
const featsEl=document.getElementById('feats-grid');
FEATS.forEach((f,i)=>{
  featsEl.innerHTML+=`<div class="feat" style="animation-delay:${i*.08}s">
    <span class="fi">${f.i}</span><div class="ft">${f.t}</div><div class="fd">${f.d}</div></div>`;
});


// ── News ──────────────────────────────────────────────────────────────────────
const RAPIDAPI_KEY='389cd79c39msh1f83b8b416e31c1p151ee2jsnb635fc398a55';
const CATS=[
  {id:'all',label:'All News'},
  {id:'nifty',label:'Nifty Stocks',q:'NSE Nifty India stocks 2026'},
  {id:'macro',label:'Macro India',q:'India economy RBI policy 2026'},
  {id:'ipo',label:'IPO / Results',q:'India IPO earnings results 2026'},
  {id:'fii',label:'FII / DII',q:'FII DII India foreign investment 2026'},
];
const TAGS={0:'NIFTY',1:'MACRO',2:'IPO',3:'FII/DII'};
const CAT_MAP={0:'nifty',1:'macro',2:'ipo',3:'fii'};
const ACCENTS={nifty:'#3b82f6',macro:'#00d97e',ipo:'#f59e0b',fii:'#8b5cf6'};
let currentFilter='all', allNews=[];

function timeAgo(d){
  if(!d)return'Recently';
  try{const m=Math.floor((Date.now()-new Date(d))/60000);
    if(m<1)return'Just now';if(m<60)return m+'m ago';
    if(m<1440)return Math.floor(m/60)+'h ago';return Math.floor(m/1440)+'d ago';}
  catch{return'Recently';}
}
function extractSrc(url){
  if(!url)return'News';
  try{const h=new URL(url).hostname.replace('www.','');
    if(h.includes('economictimes'))return'Economic Times';
    if(h.includes('businessstandard'))return'Business Standard';
    if(h.includes('livemint')||h.includes('mint'))return'Mint';
    if(h.includes('moneycontrol'))return'Moneycontrol';
    if(h.includes('bloomberg'))return'Bloomberg';
    if(h.includes('reuters'))return'Reuters';
    if(h.includes('ndtv'))return'NDTV';
    return h.split('.')[0].toUpperCase();}
  catch{return'News';}
}

function buildNav(){
  const navEl=document.getElementById('news-nav');
  navEl.innerHTML='';
  CATS.forEach(c=>{
    const btn=document.createElement('button');
    btn.className='nf'+(currentFilter===c.id?' active':'');
    btn.textContent=c.label;
    btn.onclick=()=>{currentFilter=c.id;fetchNews();};
    navEl.appendChild(btn);
  });
  const ref=document.createElement('button');
  ref.className='ref-btn';ref.id='ref-btn';ref.innerHTML='⟳ Refresh';
  ref.onclick=()=>fetchNews();
  navEl.appendChild(ref);
}

function showShimmers(){
  const g=document.getElementById('news-grid');
  g.innerHTML=Array.from({length:6}).map(()=>`<div class="shim"><div class="sl s"></div><div class="sl"></div><div class="sl m"></div></div>`).join('');
}

function renderNews(news){
  const g=document.getElementById('news-grid');
  if(!news.length){g.innerHTML='<div class="err">No news found. Click Refresh.</div>';return;}
  g.innerHTML=news.map((item,i)=>{
    const acc=ACCENTS[item.category]||'#3b82f6';
    return `<article class="news-card" style="--acc:${acc};animation-delay:${i*45}ms">
      <div class="nc-top"><span class="nc-src">${extractSrc(item.url)}</span><span class="nc-time">${timeAgo(item.date||item.published_date)}</span></div>
      <div class="nc-hl">${item.title||''}</div>
      <div class="nc-ft">
        <span class="nc-tag" style="background:${acc}18;color:${acc};border:1px solid ${acc}30">${item.tag||'MARKETS'}</span>
        ${item.url?`<a class="nc-link" href="${item.url}" target="_blank" rel="noopener">Read →</a>`:''}
      </div>
    </article>`;
  }).join('');
}

async function fetchNews(){
  const btn=document.getElementById('ref-btn');
  if(btn){btn.disabled=true;btn.innerHTML='<span class="spin">⟳</span> Loading';}
  showShimmers();

  const queries=currentFilter==='all'
    ?['NSE Nifty India stock market 2026','India economy RBI policy news 2026','India IPO earnings 2026','FII DII India investment 2026']
    :[CATS.find(c=>c.id===currentFilter)?.q||'India stock market 2026'];

  try{
    const results=await Promise.allSettled(queries.map((q,i)=>
      fetch(`https://real-time-web-search.p.rapidapi.com/search?q=${encodeURIComponent(q)}&limit=6`,{
        headers:{'X-RapidAPI-Key':RAPIDAPI_KEY,'X-RapidAPI-Host':'real-time-web-search.p.rapidapi.com'}
      }).then(r=>r.json()).then(d=>({data:d.data||[],idx:i}))
    ));
    allNews=[];
    results.forEach(r=>{
      if(r.status==='fulfilled'&&r.value.data){
        allNews=[...allNews,...r.value.data.map(x=>({...x,tag:TAGS[r.value.idx]||'MARKETS',category:CAT_MAP[r.value.idx]||'nifty'}))];
      }
    });
    if(!allNews.length){
      document.getElementById('news-grid').innerHTML=`<div class="err">⚠️ Could not fetch live news. Rate limit reached.<br><button onclick="fetchNews()">Try Again</button></div>`;
    }else{
      const filtered=currentFilter==='all'?allNews:allNews.filter(n=>n.category===currentFilter);
      renderNews(filtered);
    }
  }catch(ex){
    document.getElementById('news-grid').innerHTML=`<div class="err">⚠️ Network error: ${ex.message}<br><button onclick="fetchNews()">Try Again</button></div>`;
  }finally{
    if(btn){btn.disabled=false;btn.innerHTML='⟳ Refresh';}
    buildNav();
  }
}

// ── Intersection observer for scroll animations ─────────────────────────────
const observer=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)';}});
},{threshold:.1});

document.querySelectorAll('.feat,.mkt-card,.stat-n').forEach(el=>{
  el.style.opacity='0';
  el.style.transform='translateY(16px)';
  el.style.transition='opacity .5s ease, transform .5s ease';
  observer.observe(el);
});

buildNav();
fetchNews();
</script>
</body>
</html>
