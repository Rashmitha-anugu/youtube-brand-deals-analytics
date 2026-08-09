"""
dashboard_template.py
---------------------
Renders a single self-contained HTML dashboard (no external JS/CSS, no build step)
from the aggregates computed in analysis.py. Charts are vanilla SVG with hover
tooltips; palette + dark mode follow a validated data-viz color system.
"""

import json


def render(results):
    data_json = json.dumps(results)
    return TEMPLATE.replace("__DATA__", data_json)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YouTube Brand Deals — GTM Analytics Dashboard</title>
<style>
  :root{
    --plane:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e;
    --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
    --series1:#2a78d6; --series2:#eb6834; --good:#0ca30c; --critical:#d03b3b;
    --seq400:#3987e5; --seq250:#86b6ef;
  }
  @media (prefers-color-scheme: dark){
    :root:where(:not([data-theme="light"])){
      --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7;
      --muted:#898781; --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
      --series1:#3987e5; --series2:#d95926; --good:#0ca30c; --critical:#d03b3b;
      --seq400:#3987e5; --seq250:#184f95;
    }
  }
  :root[data-theme="dark"]{
    --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7;
    --muted:#898781; --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
    --series1:#3987e5; --series2:#d95926; --seq400:#3987e5; --seq250:#184f95;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--plane);color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.5}
  .wrap{max-width:1080px;margin:0 auto;padding:32px 24px 64px}
  header h1{font-size:22px;margin:0 0 4px}
  header p{margin:0;color:var(--ink2);font-size:14px}
  .synthetic{display:inline-block;margin-top:10px;padding:4px 10px;border:1px solid var(--border);
    border-radius:999px;font-size:12px;color:var(--ink2);background:var(--surface)}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0 8px}
  .tile{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px}
  .tile .lab{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
  .tile .val{font-size:26px;font-weight:600;margin-top:6px;font-variant-numeric:tabular-nums}
  .tile .sub{font-size:12px;color:var(--ink2);margin-top:2px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:22px}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px}
  .card h2{font-size:15px;margin:0 0 2px}
  .card .cap{font-size:12px;color:var(--ink2);margin:0 0 14px}
  svg{display:block;width:100%;overflow:visible}
  .axislab{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
  .vallab{fill:var(--ink2);font-size:11px;font-variant-numeric:tabular-nums}
  .catlab{fill:var(--ink);font-size:12px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--grid)}
  th{color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.03em}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .tip{position:fixed;pointer-events:none;background:var(--surface);color:var(--ink);
    border:1px solid var(--border);border-radius:8px;padding:8px 10px;font-size:12px;
    box-shadow:0 4px 16px rgba(0,0,0,.12);opacity:0;transition:opacity .08s;z-index:10;max-width:240px}
  .toggle{float:right;font-size:12px;color:var(--ink2);cursor:pointer;border:1px solid var(--border);
    background:var(--surface);border-radius:8px;padding:4px 10px}
  .foot{margin-top:28px;font-size:12px;color:var(--muted)}
  @media(max-width:820px){.kpis{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <button class="toggle" id="themeBtn">◐ theme</button>
    <h1>YouTube Brand Deals — GTM Analytics Dashboard</h1>
    <p>Campaign efficiency, format mix, and seasonality for the Brand Deals business.</p>
    <span class="synthetic">Synthetic demo data — reproducible, no real/proprietary data</span>
  </header>

  <section class="kpis" id="kpis"></section>

  <div class="grid2">
    <div class="card"><h2>Return on investment by category</h2>
      <p class="cap">Attributed revenue ÷ media spend. Finance leads; Food returns below break-even (0.88x).</p>
      <div id="catChart"></div></div>
    <div class="card"><h2>ROI efficiency by format</h2>
      <p class="cap">Shorts return the most per dollar (lowest placement cost); dedicated videos cost more per return.</p>
      <div id="fmtChart"></div></div>
  </div>

  <div class="grid2">
    <div class="card"><h2>Attributed revenue by month</h2>
      <p class="cap">Monthly attributed revenue. Volatility reflects campaign timing; Q4 windows tend to run above trend.</p>
      <div id="monthChart"></div></div>
    <div class="card"><h2>Where at-risk spend concentrates</h2>
      <p class="cap">Campaigns returning below 1.0x ROI, by category & format.</p>
      <div id="riskTable"></div></div>
  </div>

  <div class="card" style="margin-top:18px"><h2>Top creators by attributed revenue</h2>
    <p class="cap">Creators with 3+ campaigns, ranked by revenue driven.</p>
    <div id="topTable"></div></div>

  <p class="foot">Source: synthetic dataset generated by <code>data/generate_data.py</code> (seeded).
     Built to demonstrate GTM analytics methodology, not to report real YouTube performance.</p>
</div>

<div class="tip" id="tip"></div>
<script>
const DATA = __DATA__;
const tip = document.getElementById('tip');
const fmtUSD = v => '$' + Math.round(v).toLocaleString();
const fmtShort = v => v>=1e6? '$'+(v/1e6).toFixed(1)+'M' : v>=1e3? '$'+(v/1e3).toFixed(0)+'k' : '$'+v;
function showTip(html,e){tip.innerHTML=html;tip.style.opacity=1;
  tip.style.left=Math.min(e.clientX+14,window.innerWidth-250)+'px';
  tip.style.top=(e.clientY+14)+'px';}
function hideTip(){tip.style.opacity=0;}

// ---- KPI tiles ----
(function(){
  const k=DATA.kpis, el=document.getElementById('kpis');
  const tiles=[
    ['Media spend', fmtShort(k.spend), k.campaigns+' campaigns'],
    ['Attributed revenue', fmtShort(k.revenue), k.creators+' creators'],
    ['Blended ROI', k.blended_roi+'x', 'revenue ÷ spend'],
    ['At-risk spend', k.pct_at_risk+'%', 'campaigns under 1.0x'],
  ];
  el.innerHTML=tiles.map(t=>`<div class="tile"><div class="lab">${t[0]}</div>
    <div class="val">${t[1]}</div><div class="sub">${t[2]}</div></div>`).join('');
})();

// ---- Horizontal bar chart (single series, direct value labels + hover) ----
function hbar(elId, rows, labelKey, valKey, opts={}){
  const w=460, rowH=34, padL=96, padR=54, padT=6;
  const h=padT + rows.length*rowH + 6;
  const max=Math.max(...rows.map(r=>r[valKey]))*1.08;
  const x=v=> padL + (v/max)*(w-padL-padR);
  const color = opts.color || 'var(--series1)';
  let s=`<svg viewBox="0 0 ${w} ${h}" role="img">`;
  rows.forEach((r,i)=>{
    const cy=padT+i*rowH, bh=16, by=cy+rowH/2-bh/2;
    const xv=x(r[valKey]);
    s+=`<text class="catlab" x="0" y="${cy+rowH/2+4}">${r[labelKey]}</text>`;
    s+=`<rect x="${padL}" y="${by}" width="${(w-padL-padR)}" height="${bh}" rx="4" fill="var(--grid)" opacity=".5"></rect>`;
    s+=`<rect class="bar" data-i="${i}" x="${padL}" y="${by}" width="${Math.max(2,xv-padL)}" height="${bh}" rx="4" fill="${color}"></rect>`;
    s+=`<text class="vallab" x="${xv+6}" y="${by+bh-3}">${opts.fmt?opts.fmt(r[valKey]):r[valKey]}</text>`;
  });
  s+=`</svg>`;
  const box=document.getElementById(elId); box.innerHTML=s;
  box.querySelectorAll('.bar').forEach(b=>{
    const r=rows[+b.dataset.i];
    b.addEventListener('mousemove',e=>showTip(
      `<b>${r[labelKey]}</b><br>${opts.tip? opts.tip(r): (valKey+': '+r[valKey])}`,e));
    b.addEventListener('mouseleave',hideTip);
  });
}

hbar('catChart', DATA.roi_by_category, 'category', 'roi', {
  fmt:v=>v+'x',
  tip:r=>`ROI <b>${r.roi}x</b><br>Spend ${fmtUSD(r.spend)}<br>Revenue ${fmtUSD(r.revenue)}<br>${r.campaigns} campaigns`});

hbar('fmtChart', DATA.roi_by_format, 'format', 'roi', {
  color:'var(--series1)', fmt:v=>v+'x',
  tip:r=>`ROI <b>${r.roi}x</b><br>Avg view ${r.avg_view_pct}%<br>${r.campaigns} campaigns`});

// ---- Line chart: revenue by month (crosshair + hover) ----
(function(){
  const rows=DATA.revenue_by_month, w=460, h=210, padL=48, padR=14, padT=12, padB=34;
  const max=Math.max(...rows.map(r=>r.revenue))*1.1;
  const X=i=> padL + i*(w-padL-padR)/(rows.length-1);
  const Y=v=> padT + (1-v/max)*(h-padT-padB);
  let grid='', ticks=4;
  for(let t=0;t<=ticks;t++){const v=max*t/ticks, y=Y(v);
    grid+=`<line x1="${padL}" y1="${y}" x2="${w-padR}" y2="${y}" stroke="var(--grid)"></line>`+
          `<text class="axislab" x="${padL-6}" y="${y+3}" text-anchor="end">${fmtShort(v)}</text>`;}
  let path=rows.map((r,i)=>`${i?'L':'M'}${X(i).toFixed(1)},${Y(r.revenue).toFixed(1)}`).join(' ');
  let xlab='';
  rows.forEach((r,i)=>{ if(i%3===0) xlab+=`<text class="axislab" x="${X(i)}" y="${h-14}" text-anchor="middle">${r.month.slice(2)}</text>`;});
  let dots=rows.map((r,i)=>`<circle class="pt" data-i="${i}" cx="${X(i)}" cy="${Y(r.revenue)}" r="8" fill="transparent"></circle>`).join('');
  let vis=rows.map((r,i)=>`<circle cx="${X(i)}" cy="${Y(r.revenue)}" r="2.5" fill="var(--series1)"></circle>`).join('');
  const svg=`<svg viewBox="0 0 ${w} ${h}" role="img">${grid}
     <path d="${path}" fill="none" stroke="var(--series1)" stroke-width="2"></path>
     ${vis}${dots}<line id="cross" y1="${padT}" y2="${h-padB}" stroke="var(--axis)" opacity="0"></line>${xlab}</svg>`;
  const box=document.getElementById('monthChart'); box.innerHTML=svg;
  const cross=box.querySelector('#cross');
  box.querySelectorAll('.pt').forEach(c=>{
    const r=rows[+c.dataset.i];
    c.addEventListener('mousemove',e=>{cross.setAttribute('x1',c.getAttribute('cx'));
      cross.setAttribute('x2',c.getAttribute('cx'));cross.setAttribute('opacity','1');
      showTip(`<b>${r.month}</b><br>Revenue ${fmtUSD(r.revenue)}<br>Spend ${fmtUSD(r.spend)}`,e);});
    c.addEventListener('mouseleave',()=>{cross.setAttribute('opacity','0');hideTip();});
  });
})();

// ---- Tables ----
(function(){
  const rows=DATA.top_creators;
  let h=`<table><thead><tr><th>Creator</th><th>Category</th><th class="num">Subs</th>
     <th class="num">Campaigns</th><th class="num">Revenue</th><th class="num">ROI</th></tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr><td>${r.creator_name}</td><td>${r.category}</td>
     <td class="num">${(r.subscribers/1000).toFixed(0)}k</td><td class="num">${r.campaigns}</td>
     <td class="num">${fmtUSD(r.revenue)}</td><td class="num">${r.roi}x</td></tr>`;});
  document.getElementById('topTable').innerHTML=h+'</tbody></table>';
})();
(function(){
  const rows=DATA.at_risk;
  let h=`<table><thead><tr><th>Category</th><th>Format</th><th class="num">Campaigns</th>
     <th class="num">Spend at risk</th></tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr><td>${r.category}</td><td>${r.format}</td>
     <td class="num">${r.campaigns}</td><td class="num">${fmtUSD(r.spend_at_risk)}</td></tr>`;});
  document.getElementById('riskTable').innerHTML=h+'</tbody></table>';
})();

// ---- Theme toggle ----
document.getElementById('themeBtn').addEventListener('click',()=>{
  const root=document.documentElement;
  const cur=root.getAttribute('data-theme');
  root.setAttribute('data-theme', cur==='dark'?'light':'dark');
});
</script>
</body>
</html>
"""
