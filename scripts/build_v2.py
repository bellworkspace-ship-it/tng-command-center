#!/usr/bin/env python3
"""TNG Leadership Command Center v2 — dashboard builder (light/luxury theme)."""
import json, sys, os
from datetime import datetime

data_path = sys.argv[1] if len(sys.argv) > 1 else "dashboard_data.json"
out_path = sys.argv[2] if len(sys.argv) > 2 else "index.html"
DATA = json.load(open(data_path))
plans_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(data_path)), "plans.json")
PLANS = json.load(open(plans_path)) if os.path.exists(plans_path) else []

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,nofollow">
<title>TNG Leadership Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#f7f7f4; --card:#ffffff; --ink:#1d2826; --muted:#68776f; --line:#e6e9e4;
  --teal:#076261; --teal2:#119090; --tint:#eef4f3; --gold:#b5985a;
  --red:#b3402f; --redbg:#faeeec; --amber:#c0841a; --amberbg:#faf3e4;
  --green:#2f7d4f; --greenbg:#ecf5ef;
  --shadow:0 1px 2px rgba(29,40,38,.05),0 8px 24px -12px rgba(29,40,38,.08);
  --r:16px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:'Inter',sans-serif;font-size:14px;-webkit-font-smoothing:antialiased}
a{color:var(--teal);text-decoration:none}
a:hover{text-decoration:underline}
.serif{font-family:'Cormorant Garamond',serif}

/* header */
header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50}
.hwrap{max-width:1280px;margin:0 auto;padding:0 28px}
.hrow{display:flex;align-items:center;justify-content:space-between;height:72px}
.brand{display:flex;align-items:center;gap:14px}
.brand img{height:40px}
.brand .t1{font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:600;letter-spacing:.02em}
.brand .t2{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted)}
.updated{font-size:11px;color:var(--muted);letter-spacing:.06em}
nav{display:flex;gap:4px;overflow-x:auto;padding-bottom:0}
nav button{appearance:none;border:0;background:none;font:inherit;cursor:pointer;
  padding:14px 16px;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
  border-bottom:2px solid transparent;white-space:nowrap}
nav button.on{color:var(--teal);border-color:var(--teal);font-weight:600}
nav button:hover{color:var(--ink)}

/* layout */
main{max-width:1280px;margin:0 auto;padding:28px}
.page{display:none}
.page.on{display:block;animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
h2.sec{font-family:'Cormorant Garamond',serif;font-size:26px;font-weight:600;margin:34px 0 14px}
h2.sec:first-child{margin-top:0}
.sub{color:var(--muted);font-size:13px;margin:-8px 0 16px}

/* range chips */
.rangebar{display:flex;align-items:center;gap:10px;margin-bottom:24px;flex-wrap:wrap}
.rangebar .lbl{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
.chips{display:flex;background:#fff;border:1px solid var(--line);border-radius:999px;padding:3px;box-shadow:var(--shadow)}
.chips button{appearance:none;border:0;background:none;font:inherit;cursor:pointer;border-radius:999px;
  padding:7px 16px;font-size:12px;font-weight:500;color:var(--muted)}
.chips button.on{background:var(--teal);color:#fff;font-weight:600}

/* cards & grids */
.grid{display:grid;gap:16px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);padding:20px}
.kpi .lbl{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.kpi .val{font-family:'Cormorant Garamond',serif;font-size:40px;font-weight:500;line-height:1}
.kpi .dim{font-size:24px;color:var(--muted)}
.kpi .delta{font-size:12px;margin-top:6px;font-weight:500}
.kpi .delta.up{color:var(--green)} .kpi .delta.dn{color:var(--red)} .kpi .delta.fl{color:var(--muted)}
.kpi svg{margin-top:10px;width:100%;height:30px}

.two{grid-template-columns:1fr 1fr} .three{grid-template-columns:2fr 1fr}
@media(max-width:900px){.two,.three{grid-template-columns:1fr}}

/* tables */
table{width:100%;border-collapse:collapse}
th{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);text-align:left;
  padding:10px 12px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
th.num,td.num{text-align:right}
th .arr{opacity:.5}
td{padding:11px 12px;border-bottom:1px solid var(--line);font-size:13px;vertical-align:middle}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--tint)}
.agname{font-weight:600;white-space:nowrap}
.money{font-variant-numeric:tabular-nums;font-weight:600;color:var(--teal)}
.mini{font-size:11.5px;color:var(--muted)}

/* badges */
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap}
.b-teal{background:var(--tint);color:var(--teal)}
.b-red{background:var(--redbg);color:var(--red)}
.b-amber{background:var(--amberbg);color:var(--amber)}
.b-green{background:var(--greenbg);color:var(--green)}
.b-grey{background:#f0f1ee;color:var(--muted)}

/* heat bar */
.heat{height:6px;border-radius:3px;background:#edeeea;overflow:hidden;min-width:60px}
.heat i{display:block;height:100%;border-radius:3px}

/* filters */
.filters{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;align-items:center}
.filters select,.filters input{font:inherit;font-size:13px;padding:8px 12px;border:1px solid var(--line);
  border-radius:10px;background:#fff;color:var(--ink)}
.count{font-size:12px;color:var(--muted);margin-left:auto}

/* agent cards */
.agrid{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.acard{cursor:pointer;transition:transform .15s ease, box-shadow .15s ease}
.acard:hover{transform:translateY(-2px);box-shadow:0 4px 8px rgba(29,40,38,.08),0 16px 36px -16px rgba(29,40,38,.16)}
.ahead{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.av{width:44px;height:44px;border-radius:50%;background:var(--tint);color:var(--teal);display:flex;align-items:center;
  justify-content:center;font-weight:700;font-size:15px;overflow:hidden;flex-shrink:0}
.av img{width:100%;height:100%;object-fit:cover}
.astats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center}
.astats .n{font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:600}
.astats .l{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}

/* detail panel */
.back{display:inline-flex;align-items:center;gap:6px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);cursor:pointer;margin-bottom:16px}
.back:hover{color:var(--teal)}
.dethead{display:flex;align-items:center;gap:18px;margin-bottom:22px}
.dethead .av{width:64px;height:64px;font-size:22px}
.dethead h1{font-family:'Cormorant Garamond',serif;font-size:34px;font-weight:600}
.dethead .mini{margin-top:2px}

.chartbox{position:relative;height:280px}
.chartbox.tall{height:330px}
canvas{max-width:100%}

.alert{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:12px;margin-bottom:10px;font-size:13px}
.alert.red{background:var(--redbg)} .alert.amber{background:var(--amberbg)} .alert.teal{background:var(--tint)}
.alert b{font-weight:600}
.alert .ic{font-size:16px;line-height:1.3}

footer{text-align:center;color:var(--muted);font-size:11px;letter-spacing:.1em;padding:30px 0 50px}
@media(max-width:768px){
  main{padding:16px} .hwrap{padding:0 16px}
  .kpi .val{font-size:32px}
  .hrow{height:60px} .brand img{height:32px} .brand .t1{font-size:18px}
  td,th{padding:8px 8px}
}
</style>
</head>
<body>
<header>
  <div class="hwrap">
    <div class="hrow">
      <div class="brand">
        <img src="https://media-production.lp-cdn.com/cdn-cgi/image/format=auto,quality=85,fit=scale-down,width=400/https://media-production.lp-cdn.com/media/1abc07f7-edce-49cb-b4ce-ec2cd52a4508" alt="TNG">
        <div><div class="t1">Leadership Command Center</div><div class="t2">The Newcomer Group</div></div>
      </div>
      <div class="updated" id="updated"></div>
    </div>
    <nav id="nav">
      <button data-p="overview" class="on">Overview</button>
      <button data-p="scoreboard">Scoreboard</button>
      <button data-p="leadflow">Lead Flow</button>
      <button data-p="sources">Sources</button>
      <button data-p="deals">Deals</button>
      <button data-p="bottlenecks">Bottlenecks</button>
      <button data-p="plans">Plans</button>
      <button data-p="agents">Agents</button>
    </nav>
  </div>
</header>
<main>
  <div class="rangebar">
    <span class="lbl">Time frame</span>
    <div class="chips" id="chips"></div>
  </div>
  <div class="page on" id="p-overview"></div>
  <div class="page" id="p-scoreboard"></div>
  <div class="page" id="p-leadflow"></div>
  <div class="page" id="p-sources"></div>
  <div class="page" id="p-deals"></div>
  <div class="page" id="p-bottlenecks"></div>
  <div class="page" id="p-plans"></div>
  <div class="page" id="p-agents"></div>
</main>
<footer>THE NEWCOMER GROUP · LEADERSHIP USE ONLY</footer>
<script>
const DATA = __DATA__;
const PLANS = __PLANS__;
/* ============ helpers ============ */
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const fmt=n=>n==null?"—":n.toLocaleString();
const money=n=>n==null?"—":"$"+Math.round(n).toLocaleString();
const moneyK=n=>n>=1e6?"$"+(n/1e6).toFixed(2)+"M":n>=1e3?"$"+Math.round(n/1e3)+"K":"$"+Math.round(n);
const pct=n=>isFinite(n)?Math.round(n)+"%":"—";
const esc=s=>(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fub=id=>`https://thenewcomergroup.followupboss.com/2/people/view/${id}`;
const initials=n=>(n||"?").split(" ").map(w=>w[0]).slice(0,2).join("").toUpperCase();
const TEAL="#076261", TEAL2="#119090", GOLD="#b5985a", RED="#b3402f", AMBER="#c0841a", GREEN="#2f7d4f", MUTED="#68776f";
const PALETTE=[TEAL,GOLD,TEAL2,"#7a9e9b","#3b5b58",AMBER,"#94785a",GREEN,"#5d7370",RED,"#1d2826","#a9b8b0"];
Chart.defaults.font.family="'Inter',sans-serif"; Chart.defaults.color=MUTED; Chart.defaults.font.size=11;

const AG = DATA.agents.slice().sort((a,b)=>a.name.localeCompare(b.name));
const AGI = Object.fromEntries(AG.map(a=>[a.id,a]));
const NOW = new Date(DATA.generatedAt);
const DAY = 864e5;
const dstr=d=>d.toISOString().slice(0,10);

const RANGES=[["7D",7],["14D",14],["30D",30],["60D",60],["90D",90],["YTD",0]];
const QP=new URLSearchParams(location.search);
let range = QP.get("range")||localStorage.getItem("tngRange")||"30D";
if(!RANGES.some(r=>r[0]===range)) range="30D";
let charts = [];

function rangeDays(r){ if(r!=="YTD") return RANGES.find(x=>x[0]===r)[1];
  return Math.max(1,Math.ceil((NOW - new Date(DATA.ytdStart))/DAY)); }
function dateList(days,offset=0){ const out=[]; for(let i=days-1+offset;i>=offset;i--) out.push(dstr(new Date(NOW-i*DAY))); return out; }

/* sum metric for agent over date list */
function sumA(aid,key,dates){ const s=DATA.series[aid]; if(!s) return 0;
  let n=0; for(const d of dates){ const e=s[d]; if(e&&e[key]) n+=e[key]; } return n; }
function seriesA(aid,key,dates){ const s=DATA.series[aid]||{};
  return dates.map(d=>(s[d]&&s[d][key])||0); }

/* deals helpers */
function gciClosed(aid,dates){ const ds=new Set(dates);
  return DATA.deals.filter(d=>d.agentId===aid&&d.closeDate&&ds.has(d.closeDate)).reduce((s,d)=>s+(d.gci||0),0); }
function gciClosedAll(dates){ const ds=new Set(dates);
  return DATA.deals.filter(d=>d.closeDate&&ds.has(d.closeDate)).reduce((s,d)=>s+(d.gci||0),0); }
function pendingGci(aid){ return DATA.deals.filter(d=>d.agentId===aid&&/pending/i.test(d.stage)).reduce((s,d)=>s+(d.gci||0),0); }
function dealsClosedIn(aid,dates){ const ds=new Set(dates);
  return DATA.deals.filter(d=>d.agentId===aid&&d.closeDate&&ds.has(d.closeDate)).length; }

/* agent metrics over range */
function metrics(aid,dates){
  const m={ calls:sumA(aid,"c",dates), conn:sumA(aid,"cc",dates), newLeads:sumA(aid,"nl",dates),
            appts:sumA(aid,"a",dates), tasks:sumA(aid,"t",dates) };
  m.gci=gciClosed(aid,dates); m.pending=pendingGci(aid); m.closedDeals=dealsClosedIn(aid,dates);
  const b=AGI[aid].book; m.book=b.total; m.active=b.active;
  m.touch = b.active? Math.min(100,100*b.touched30/b.active) : 0;  // fixed 30-day coverage window
  m.effortRaw = m.calls + m.conn*1.5 + m.appts*8 + m.tasks*2;
  return m;
}

/* sparkline svg */
function nurtureOf(a){ return Object.entries(a.book.stages||{}).filter(([s])=>/nurture|pond/i.test(s)).reduce((n,[,v])=>n+v,0); }
function spark(vals,color=TEAL){ const w=140,h=30,max=Math.max(...vals,1);
  const pts=vals.map((v,i)=>`${(i/(vals.length-1||1)*w).toFixed(1)},${(h-2-(v/max)*(h-6)).toFixed(1)}`).join(" ");
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" opacity=".9"/></svg>`; }
function bucket(vals,n=28){ if(vals.length<=n) return vals; const out=[],sz=vals.length/n;
  for(let i=0;i<n;i++){ out.push(vals.slice(Math.floor(i*sz),Math.floor((i+1)*sz)).reduce((a,b)=>a+b,0)); } return out; }
function bucketLabels(dates,n=28){ if(dates.length<=n) return dates.map(d=>d.slice(5));
  const out=[],sz=dates.length/n; for(let i=0;i<n;i++) out.push(dates[Math.floor(i*sz)].slice(5)); return out; }
function delta(cur,prev){ if(prev===0&&cur===0) return `<span class="delta fl">—</span>`;
  if(prev===0) return `<span class="delta up">new</span>`;
  const p=Math.round(100*(cur-prev)/prev);
  return `<span class="delta ${p>0?"up":p<0?"dn":"fl"}">${p>0?"▲":p<0?"▼":"•"} ${Math.abs(p)}% vs prior</span>`; }

function destroyCharts(){ charts.forEach(c=>c.destroy()); charts=[]; }
function mkChart(ctx,cfg){ const c=new Chart(ctx,cfg); charts.push(c); return c; }
const gridless={grid:{display:false},border:{display:false}};
const ax=(t)=>({display:true,text:t,font:{size:9,weight:'600'},color:'#9aa6a0'});
const softGrid={grid:{color:"#eef0ec"},border:{display:false},ticks:{maxTicksLimit:5}};

/* ============ state & render ============ */
let page="overview", detailAgent=null, scoreMetric="effort";

function render(){
  destroyCharts();
  const days=rangeDays(range), dates=dateList(days), prev=dateList(days,days);
  $("#updated").textContent="Updated "+NOW.toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});
  renderOverview(dates,prev); renderScoreboard(dates,prev); renderLeadflow(dates);
  renderSources(dates); renderDeals(dates); renderBottlenecks(); renderPlans(); renderAgents(dates,prev);
}

/* ---------- OVERVIEW ---------- */
function renderOverview(dates,prev){
  const tot=k=>AG.reduce((s,a)=>s+sumA(a.id,k,dates),0);
  const totPrev=k=>AG.reduce((s,a)=>s+sumA(a.id,k,prev),0);
  const teamSpark=k=>bucket(dates.map(d=>AG.reduce((s,a)=>{const e=(DATA.series[a.id]||{})[d];return s+((e&&e[k])||0);},0)));
  const gci=gciClosedAll(dates), gciP=gciClosedAll(prev);
  const pend=DATA.deals.filter(d=>/pending/i.test(d.stage)).reduce((s,d)=>s+(d.gci||0),0);
  const pendN=DATA.deals.filter(d=>/pending/i.test(d.stage)).length;
  const noContact=DATA.watch.filter(w=>w.status==="no_contact").length;
  const underWorked=DATA.watch.filter(w=>w.status==="under_worked").length;
  const stalled15=DATA.leads15.filter(l=>l.movement==="stalled").length;
  const redis=DATA.leads15.filter(l=>l.movement==="redistributed").length;

  const kpi=(lbl,val,d,sp,color)=>`<div class="card kpi"><div class="lbl">${lbl}</div>
    <div class="val">${val}</div>${d||""}${sp?spark(sp,color||TEAL):""}</div>`;

  let alerts="";
  if(noContact>0) alerts+=`<div class="alert red"><span class="ic">📞</span><div><b>${noContact} new lead${noContact>1?"s":""} with ZERO outreach</b> — leads from the last 7 days that nobody has called, texted, or emailed. <a href="#" onclick="goBottlenecks('no_contact');return false">See who they are →</a></div></div>`;
  if(underWorked>0) alerts+=`<div class="alert amber"><span class="ic">⚠️</span><div><b>${underWorked} new lead${underWorked>1?"s":""} being under-worked</b> — getting some touches but below the 3-a-day standard. <a href="#" onclick="goBottlenecks('under_worked');return false">Review →</a></div></div>`;
  const worstStuck=DATA.stuck.slice(0,3);
  if(worstStuck.length) alerts+=`<div class="alert teal"><span class="ic">🧊</span><div><b>${fmt(DATA.stuck.length)} leads sitting idle past stage thresholds.</b> Longest: ${worstStuck.map(s=>`<a href="${fub(s.id)}" target="_blank">${esc(s.name)}</a> (${s.dsa}d, ${esc(s.agent.split(" ")[0])})`).join(" · ")}. <a href="#" onclick="goBottlenecks('');return false">Open bottleneck finder →</a></div></div>`;

  const lowTouch=AG.map(a=>({a,m:metrics(a.id,dates)})).filter(x=>x.m.active>20&&x.m.touch<40)
      .sort((x,y)=>x.m.touch-y.m.touch).slice(0,3);
  if(lowTouch.length) alerts+=`<div class="alert amber"><span class="ic">🪫</span><div><b>Low book coverage:</b> ${lowTouch.map(x=>`${esc(x.a.name)} (${pct(x.m.touch)} of ${x.m.active} active leads touched)`).join(" · ")}</div></div>`;

  /* top agents mini-scoreboard */
  const ranked=AG.map(a=>({a,m:metrics(a.id,dates)})).sort((x,y)=>y.m.effortRaw-x.m.effortRaw).slice(0,5);
  const topRows=ranked.map((x,i)=>`<tr onclick="openAgent(${x.a.id})" style="cursor:pointer">
    <td class="mini">${i+1}</td><td class="agname">${esc(x.a.name)}</td>
    <td class="num">${fmt(x.m.calls)}</td><td class="num">${fmt(x.m.appts)}</td>
    <td class="num money">${moneyK(x.m.gci)}</td></tr>`).join("");

  $("#p-overview").innerHTML=`
    <div class="grid kpis">
      ${kpi("New Leads",fmt(tot("nl")),delta(tot("nl"),totPrev("nl")),teamSpark("nl"))}
      ${kpi("Outbound Calls",fmt(tot("c")),delta(tot("c"),totPrev("c")),teamSpark("c"))}
      ${kpi("Conversations",fmt(tot("cc")),delta(tot("cc"),totPrev("cc")),teamSpark("cc"),TEAL2)}
      ${kpi("Appointments",fmt(tot("a")),delta(tot("a"),totPrev("a")),teamSpark("a"),GOLD)}
      ${kpi("GCI Closed",moneyK(gci),delta(gci,gciP),null)}
      ${kpi("Pending GCI",moneyK(pend),`<span class="delta fl">${pendN} deals under contract</span>`,null)}
    </div>
    <h2 class="sec">Where your eyes should be</h2>
    ${alerts||'<div class="alert teal"><span class="ic">✅</span><div>No critical alerts right now.</div></div>'}
    <div class="grid two" style="margin-top:24px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Team activity — ${range}</h2>
        <div class="sub">Daily outbound calls and new leads</div>
        <div class="chartbox"><canvas id="ovChart"></canvas></div></div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Top effort this ${range==="YTD"?"year":range.toLowerCase()}</h2>
        <div class="sub">Ranked by activity (calls, conversations, appointments, tasks)</div>
        <table><thead><tr><th></th><th>Agent</th><th class="num">Calls</th><th class="num">Appts</th><th class="num">GCI</th></tr></thead>
        <tbody>${topRows}</tbody></table>
        <div class="mini" style="margin-top:10px">15-day lead pulse: <b>${stalled15}</b> stalled · <b>${redis}</b> redistributed / pond</div></div>
    </div>`;

  mkChart($("#ovChart"),{type:"bar",
    data:{labels:bucketLabels(dates),
      datasets:[
       {type:"bar",label:"Calls",data:bucket(dates.map(d=>AG.reduce((s,a)=>{const e=(DATA.series[a.id]||{})[d];return s+((e&&e.c)||0);},0))),backgroundColor:"rgba(7,98,97,.25)",borderRadius:4},
       {type:"line",label:"New leads",data:bucket(dates.map(d=>AG.reduce((s,a)=>{const e=(DATA.series[a.id]||{})[d];return s+((e&&e.nl)||0);},0))),borderColor:GOLD,backgroundColor:GOLD,tension:.4,pointRadius:0,borderWidth:2,yAxisID:"y1"}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{boxWidth:10,boxHeight:10}}},
      scales:{x:{...gridless,ticks:{maxTicksLimit:10},title:ax("DATE")},y:{...softGrid,title:ax("CALLS / DAY")},y1:{position:"right",...gridless,ticks:{maxTicksLimit:5},title:ax("NEW LEADS / DAY")}}}});
}

/* ---------- SCOREBOARD ---------- */
let sortKey="effort", sortDir=-1;
function renderScoreboard(dates,prev){
  const rows=AG.map(a=>{ const m=metrics(a.id,dates); return {a,m}; });
  const maxEffort=Math.max(...rows.map(r=>r.m.effortRaw),1);
  rows.forEach(r=>r.m.effort=Math.round(100*r.m.effortRaw/maxEffort));
  const key=r=>({effort:r.m.effort,calls:r.m.calls,conn:r.m.conn,newLeads:r.m.newLeads,appts:r.m.appts,
    touch:r.m.touch,gci:r.m.gci,pending:r.m.pending,book:r.m.active,name:r.a.name})[sortKey];
  rows.sort((x,y)=>{const a=key(x),b=key(y); return (typeof a==="string"? a.localeCompare(b): a-b)*sortDir;});

  const hd=(k,l,num=1)=>`<th class="${num?"num":""}" onclick="setSort('${k}')">${l} ${sortKey===k?`<span class="arr">${sortDir<0?"↓":"↑"}</span>`:""}</th>`;
  const body=rows.map((r,i)=>{
    const m=r.m;
    return `<tr onclick="openAgent(${r.a.id})" style="cursor:pointer">
      <td class="mini">${i+1}</td>
      <td class="agname">${esc(r.a.name)}</td>
      <td class="num">${fmt(m.newLeads)}</td>
      <td class="num">${fmt(m.calls)}</td>
      <td class="num">${fmt(m.conn)}</td>
      <td class="num">${fmt(m.appts)}</td>
      <td><div class="heat" title="${pct(m.touch)} of their working book has logged activity in the last 30 days (calls, texts, emails incl. automated)"><i style="width:${Math.min(100,m.touch)}%;background:${m.touch>=60?GREEN:m.touch>=35?AMBER:RED}"></i></div><span class="mini">${pct(m.touch)}</span></td>
      <td class="num money">${moneyK(m.gci)}</td>
      <td class="num mini">${moneyK(m.pending)}</td>
      <td class="num">${fmt(m.active)}</td>
      <td><div class="heat"><i style="width:${m.effort}%;background:linear-gradient(90deg,${TEAL2},${TEAL})"></i></div><span class="mini">${m.effort}</span></td>
    </tr>`;}).join("");

  $("#p-scoreboard").innerHTML=`
    <h2 class="sec">Agent Performance Scoreboard</h2>
    <div class="sub">Every metric below reflects the selected time frame (${range}). Click any column to re-rank, any row for the agent's full book.</div>
    <div class="card" style="padding:6px 6px 2px;overflow-x:auto">
      <table id="scoretab"><thead><tr>
        <th></th>${hd("name","Agent",0)}${hd("newLeads","New Leads")}${hd("calls","Calls")}${hd("conn","Convos")}
        ${hd("appts","Appts")}${hd("touch","Coverage 30d",0)}${hd("gci","GCI Closed")}${hd("pending","Pending GCI")}
        ${hd("book","Working Book")}${hd("effort","Effort",0)}
      </tr></thead><tbody>${body}</tbody></table>
    </div>
    <div class="card" style="margin-top:14px;padding:14px 18px">
      <div class="mini" style="line-height:1.7"><b>How to read this:</b>
      <b>New Leads</b> = leads assigned in the window · <b>Calls</b> = outbound dials · <b>Convos</b> = calls connected &gt;10s ·
      <b>Appts</b> = appointments created · <b>Coverage 30d</b> = share of the working book with any logged activity in the last 30 days (fixed window — doesn't change with the time-frame selector; automated drips count, so low numbers are a real red flag) ·
      <b>GCI Closed</b> = commission on deals closed inside the window · <b>Pending GCI</b> = commission on current under-contract deals (point-in-time) ·
      <b>Working Book</b> = leads in actionable stages today (Lead → Under Contract; nurture &amp; closed excluded) ·
      <b>Effort</b> = calls + 1.5×convos + 8×appts + 2×tasks done, scaled so the top agent in the window = 100.</div>
    </div>
    <div class="grid two" style="margin-top:20px">
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <h2 class="sec serif" style="font-size:20px;margin:0">Agents plotted</h2>
          <select id="plotMetric" onchange="scoreMetric=this.value;render()">
            <option value="effort" ${scoreMetric==="effort"?"selected":""}>Effort score</option>
            <option value="calls" ${scoreMetric==="calls"?"selected":""}>Outbound calls</option>
            <option value="conn" ${scoreMetric==="conn"?"selected":""}>Conversations</option>
            <option value="appts" ${scoreMetric==="appts"?"selected":""}>Appointments</option>
            <option value="newLeads" ${scoreMetric==="newLeads"?"selected":""}>New leads</option>
            <option value="gci" ${scoreMetric==="gci"?"selected":""}>GCI closed</option>
            <option value="touch" ${scoreMetric==="touch"?"selected":""}>Book touch %</option>
          </select>
        </div>
        <div class="chartbox tall"><canvas id="scoreBar"></canvas></div>
      </div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Does the effort pay? <span class="mini" style="font-size:12px">(follows the selector ←)</span></h2>
        <div class="sub">X: <b>${({effort:"effort score",calls:"outbound calls",conn:"conversations",appts:"appointments",newLeads:"new leads",gci:"effort score",touch:"coverage 30d %"})[scoreMetric]}</b> · Y: GCI closed (${range}) · bubble size: pending GCI</div>
        <div class="chartbox tall"><canvas id="scatter"></canvas></div></div>
    </div>`;

  const sorted=rows.slice().sort((x,y)=>(y.m[scoreMetric]||0)-(x.m[scoreMetric]||0));
  mkChart($("#scoreBar"),{type:"bar",
    data:{labels:sorted.map(r=>r.a.name.split(" ")[0]),
      datasets:[{data:sorted.map(r=>r.m[scoreMetric]||0),
        backgroundColor:sorted.map((_,i)=>i===0?GOLD:"rgba(7,98,97,.75)"),borderRadius:6}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>scoreMetric==="gci"?moneyK(c.raw):fmt(c.raw)}}},
      scales:{x:{...softGrid,title:ax($("#plotMetric")?$("#plotMetric").selectedOptions[0].text.toUpperCase():"")},y:{...gridless,title:ax("AGENT")}}}});

  const xKey=scoreMetric==="gci"?"effort":scoreMetric;
  const xLbl=({effort:"EFFORT SCORE",calls:"OUTBOUND CALLS",conn:"CONVERSATIONS",appts:"APPOINTMENTS",newLeads:"NEW LEADS",touch:"COVERAGE 30D %"})[xKey]||"EFFORT";
  mkChart($("#scatter"),{type:"bubble",
    data:{datasets:rows.map((r,i)=>({label:r.a.name,
      data:[{x:Math.round(r.m[xKey]||0),y:r.m.gci,r:Math.max(4,Math.sqrt(r.m.pending)/40)}],
      backgroundColor:PALETTE[i%PALETTE.length]+"cc"}))},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${xLbl.toLowerCase()} ${fmt(c.raw.x)}, GCI ${moneyK(c.raw.y)}, pending ${moneyK(rows.find(r=>r.a.name===c.dataset.label).m.pending)}`}}},
      scales:{x:{title:{display:true,text:xLbl,font:{size:9}},...softGrid},
              y:{title:{display:true,text:"GCI CLOSED",font:{size:9}},...softGrid,ticks:{callback:v=>moneyK(v)}}}}});
}
function setSort(k){ if(sortKey===k) sortDir*=-1; else {sortKey=k; sortDir=-1;} render(); }

/* ---------- LEAD FLOW ---------- */
function renderLeadflow(dates){
  const mv=DATA.leads15.reduce((m,l)=>{m[l.movement]=(m[l.movement]||0)+1;return m;},{});
  const total15=DATA.leads15.length;
  const srcCount={};
  DATA.leads15.forEach(l=>{srcCount[l.source]=(srcCount[l.source]||0)+1;});
  const topSrc=Object.entries(srcCount).sort((a,b)=>b[1]-a[1]).slice(0,8);
  const redisRows=DATA.leads15.filter(l=>l.movement==="redistributed").slice(0,60)
    .map(l=>`<tr><td><a href="${fub(l.id)}" target="_blank">${esc(l.name)}</a></td>
      <td class="mini">${esc(l.source)}</td><td class="mini">${l.created}</td>
      <td><span class="badge b-grey">${esc(l.agent)}</span></td></tr>`).join("");
  const stalledRows=DATA.leads15.filter(l=>l.movement==="stalled").slice(0,80)
    .map(l=>`<tr><td><a href="${fub(l.id)}" target="_blank">${esc(l.name)}</a></td>
      <td class="mini">${esc(l.agent)}</td><td class="mini">${esc(l.source)}</td><td class="mini">${l.created}</td></tr>`).join("");

  const card=(lbl,n,cls)=>`<div class="card kpi"><div class="lbl">${lbl}</div><div class="val">${fmt(n||0)}</div>
    <div class="delta fl">${total15?Math.round(100*(n||0)/total15):0}% of 15-day intake</div></div>`;

  $("#p-leadflow").innerHTML=`
    <h2 class="sec">How leads are spinning up</h2>
    <div class="sub">Every lead created in the last 15 days, and what's happened to it since.</div>
    <div class="grid kpis">
      ${card("New (≤1 day)",mv.new)}
      ${card("Progressing",mv.progressing)}
      ${card("Stalled at Lead",mv.stalled)}
      ${card("Converted",mv.converted)}
      ${card("Trashed",mv.trashed)}
      ${card("Redistributed / Pond",mv.redistributed)}
      ${card("Recruiting (imports)",mv.recruiting)}
    </div>
    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Daily lead intake — ${range}</h2>
        <div class="sub">Team-wide new leads per day</div>
        <div class="chartbox"><canvas id="lfDaily"></canvas></div></div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Where they come from (15d)</h2>
        <div class="chartbox"><canvas id="lfSrc"></canvas></div></div>
    </div>
    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 8px">Stalled at Lead stage (15d)</h2>
        <div class="sub">Assigned but never moved — these are conversion leaks.</div>
        <div style="max-height:340px;overflow:auto"><table><thead><tr><th>Lead</th><th>Agent</th><th>Source</th><th>Created</th></tr></thead><tbody>${stalledRows||'<tr><td class="mini" colspan="4">None 🎉</td></tr>'}</tbody></table></div></div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 8px">Redistributed / Pond (15d)</h2>
        <div class="sub">Leads that left the display team — where they went.</div>
        <div style="max-height:340px;overflow:auto"><table><thead><tr><th>Lead</th><th>Source</th><th>Created</th><th>Destination</th></tr></thead><tbody>${redisRows||'<tr><td class="mini" colspan="4">None</td></tr>'}</tbody></table></div></div>
    </div>`;

  const daily=dates.map(d=>AG.reduce((s,a)=>{const e=(DATA.series[a.id]||{})[d];return s+((e&&e.nl)||0);},0));
  mkChart($("#lfDaily"),{type:"line",
    data:{labels:bucketLabels(dates),
      datasets:[{data:bucket(daily),fill:true,borderColor:TEAL,backgroundColor:"rgba(7,98,97,.10)",tension:.4,pointRadius:0,borderWidth:2}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
      scales:{x:{...gridless,ticks:{maxTicksLimit:10},title:ax("DATE")},y:{...softGrid,title:ax("NEW LEADS / DAY")}}}});
  mkChart($("#lfSrc"),{type:"doughnut",
    data:{labels:topSrc.map(s=>s[0]),datasets:[{data:topSrc.map(s=>s[1]),backgroundColor:PALETTE,borderWidth:2,borderColor:"#fff"}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:"62%",
      plugins:{legend:{position:"right",labels:{boxWidth:10,boxHeight:10,font:{size:11}}}}}});
}


/* ---------- DEALS ---------- */
function renderDeals(dates){
  const offTeam=DATA.deals.filter(d=>!/lost/i.test(d.stage)&&d.agentId&&!AGI[d.agentId]).length;
  const noAgent=DATA.deals.filter(d=>!/lost/i.test(d.stage)&&!d.agentId).length;
  const all=DATA.deals.filter(d=>!/lost/i.test(d.stage)&&AGI[d.agentId]);
  const listings=all.filter(d=>/mls live/i.test(d.stage));
  const signed=all.filter(d=>/^signed$/i.test(d.stage));
  const pending=all.filter(d=>/^pending$/i.test(d.stage));
  const closed=all.filter(d=>/^closed$/i.test(d.stage));
  const vol=ds=>ds.reduce((s,d)=>s+(d.price||0),0);
  const gciSum=ds=>ds.reduce((s,d)=>s+(d.gci||0),0);
  const month=dstr(NOW).slice(0,7);
  const closedMTD=closed.filter(d=>d.closeDate&&d.closeDate.startsWith(month));
  const ds=new Set(dates);
  const closedRange=closed.filter(d=>d.closeDate&&ds.has(d.closeDate));
  const noGciPending=pending.filter(d=>!d.gci).length;
  const noPricePending=pending.filter(d=>!d.price).length;
  const today=dstr(NOW);
  const fmtDay=d=>{const dt=new Date(d+"T00:00:00Z");
    const rel=d===today?" · TODAY":d===dstr(new Date(NOW-DAY))?" · yesterday":d===dstr(new Date(+NOW+DAY))?" · tomorrow":"";
    return dt.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric",timeZone:"UTC"})+rel;};
  const sideBadge=d=>`<span class="badge ${d.side==="Seller"?"b-amber":"b-teal"}">${d.side}</span>`;
  const gciCell=d=>d.gci?`<span class="money">${moneyK(d.gci)}</span>`:'<span class="badge b-red" title="No commission entered on the deal card">no GCI</span>';
  const priceCell=d=>d.price?moneyK(d.price):'<span class="badge b-red">no price</span>';
  const cLink=d=>d.clientId?`<a href="${fub(d.clientId)}" target="_blank">${esc(d.client||"")}</a>`:esc(d.client||"—");
  const row=(d,dateCol)=>`<tr><td><b>${esc((d.address||d.name||"—").slice(0,52))}</b><div class="mini">${cLink(d)}${d.source?` · ${esc(d.source)}`:""}</div></td>
    <td class="mini">${esc((d.agentName||"—").split(" ")[0])}</td><td>${sideBadge(d)}</td>
    <td class="num">${priceCell(d)}</td><td class="num">${gciCell(d)}</td>
    <td class="mini" style="white-space:nowrap">${dateCol||""}</td></tr>`;
  const thead=`<thead><tr><th>Property / Client / Source</th><th>Agent</th><th>Side</th><th class="num">Volume</th><th class="num">GCI</th><th>Date</th></tr></thead>`;

  /* closing tape */
  const d7=dstr(new Date(+NOW-7*DAY)), d30=dstr(new Date(+NOW+30*DAY));
  const closedLast7=closed.filter(d=>d.closeDate&&d.closeDate>=d7&&d.closeDate<=today).sort((a,b)=>b.closeDate.localeCompare(a.closeDate));
  const upcoming=pending.filter(d=>d.projClose&&d.projClose>=today&&d.projClose<=d30).sort((a,b)=>a.projClose.localeCompare(b.projClose));
  const overdue=pending.filter(d=>d.projClose&&d.projClose<today).sort((a,b)=>a.projClose.localeCompare(b.projClose));
  const later=pending.filter(d=>d.projClose&&d.projClose>d30).length;
  const noDate=pending.filter(d=>!d.projClose);
  const tape=(items,dateKey)=>{let cur="",out="";items.forEach(d=>{const dd=d[dateKey];
    if(dd!==cur){cur=dd;out+=`<tr><td colspan="6" style="background:var(--tint);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);font-weight:600;padding:7px 12px">${fmtDay(dd)} — ${items.filter(x=>x[dateKey]===dd).length} deal(s) · ${moneyK(vol(items.filter(x=>x[dateKey]===dd)))} volume</td></tr>`;}
    out+=row(d,"");});return out;};

  const kpi=(l,v,sub)=>`<div class="card kpi"><div class="lbl">${l}</div><div class="val">${v}</div><div class="delta fl">${sub||""}</div></div>`;
  $("#p-deals").innerHTML=`
    <h2 class="sec">Deals & Listings</h2>
    <div class="sub">TEAM AGENTS ONLY — leadership production (${offTeam} deals) and unassigned cards (${noAgent}) are excluded. Volume = contract/list price. ${noGciPending?`<span class="badge b-red">${noGciPending} of ${pending.length} pending deals missing GCI</span> <span class="badge ${noPricePending?"b-red":"b-grey"}">${noPricePending} missing price</span> — have agents complete their deal cards.`:""}</div>
    <div class="grid kpis">
      ${kpi("On Market Now",fmt(listings.length),moneyK(vol(listings))+" list volume")}
      ${kpi("Signed — Coming Soon",fmt(signed.length),moneyK(vol(signed))+" volume")}
      ${kpi("Pending",fmt(pending.length),moneyK(vol(pending))+" · "+moneyK(gciSum(pending))+" GCI entered")}
      ${kpi("Closed This Month",fmt(closedMTD.length),moneyK(vol(closedMTD))+" · "+moneyK(gciSum(closedMTD))+" GCI")}
      ${kpi("Closed — "+range,fmt(closedRange.length),moneyK(vol(closedRange))+" · "+moneyK(gciSum(closedRange))+" GCI")}
    </div>

    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">The closing tape</h2>
        <div class="sub">What closed, what's closing, day by day.</div>
        ${overdue.length?`<div class="alert red" style="margin-bottom:8px"><span class="ic">⏰</span><div><b>${overdue.length} pending deal${overdue.length>1?"s are":" is"} past the expected close date</b> — chase status with the TC.</div></div>`:""}
        <div style="max-height:560px;overflow:auto"><table>${thead}<tbody>
          ${overdue.length?`<tr><td colspan="6" style="background:var(--redbg);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--red);font-weight:600;padding:7px 12px">PAST EXPECTED CLOSE</td></tr>`+overdue.map(d=>row(d,fmtDay(d.projClose))).join(""):""}
          ${upcoming.length?`<tr><td colspan="6" style="background:#faf7f0;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:#8a6d2f;font-weight:600;padding:7px 12px">COMING UP — NEXT 30 DAYS</td></tr>`+tape(upcoming,"projClose"):""}
          ${closedLast7.length?`<tr><td colspan="6" style="background:var(--greenbg);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:600;padding:7px 12px">CLOSED — LAST 7 DAYS</td></tr>`+tape(closedLast7,"closeDate"):""}
        </tbody></table></div>
        <div class="mini" style="margin-top:8px">${later?`${later} more pending close beyond 30 days. `:""}${noDate.length?`<b style="color:${RED}">${noDate.length} pending deals have NO expected close date</b> — fix on the deal card.`:""}</div></div>
      <div>
        <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Closed volume by month — ${NOW.getFullYear()}</h2>
          <div class="chartbox"><canvas id="dealMonthly"></canvas></div></div>
        <div class="card" style="margin-top:16px"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">What sources are closing — ${range}</h2>
          <div class="chartbox"><canvas id="dealSrc"></canvas></div></div>
      </div>
    </div>

    <h2 class="sec">Active listings (${listings.length})</h2>
    <div class="card" style="padding:6px;overflow:auto;max-height:430px">
      <table>${thead}<tbody>${listings.sort((a,b)=>(b.price||0)-(a.price||0)).map(d=>row(d,d.mlsLive?("MLS live "+fmtDay(d.mlsLive)):'<span class="badge b-red" title="No MLS live date on the deal card — backfill from Paragon">no MLS date</span>')).join("")||'<tr><td class="mini" colspan="6">None live</td></tr>'}</tbody></table></div>

    <h2 class="sec">All pending (${pending.length})</h2>
    <div class="card" style="padding:6px;overflow:auto;max-height:430px">
      <table>${thead}<tbody>${pending.sort((a,b)=>(a.projClose||"9999").localeCompare(b.projClose||"9999")).map(d=>row(d,d.projClose?("est. "+fmtDay(d.projClose)):'<span class="badge b-red">no close date</span>')).join("")}</tbody></table></div>`;

  /* monthly chart */
  const months=[...Array(12).keys()].map(i=>`${NOW.getFullYear()}-${String(i+1).padStart(2,"0")}`);
  const mv=months.map(m=>vol(closed.filter(d=>d.closeDate&&d.closeDate.startsWith(m))));
  const mg=months.map(m=>gciSum(closed.filter(d=>d.closeDate&&d.closeDate.startsWith(m))));
  mkChart($("#dealMonthly"),{type:"bar",
    data:{labels:months.map(m=>new Date(m+"-02").toLocaleDateString("en-US",{month:"short"})),
      datasets:[{type:"bar",label:"Volume",data:mv,backgroundColor:"rgba(7,98,97,.55)",borderRadius:5},
                {type:"line",label:"GCI",data:mg,borderColor:GOLD,tension:.4,pointRadius:2,borderWidth:2,yAxisID:"y1"}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{boxWidth:10,boxHeight:10}},
      tooltip:{callbacks:{label:c=>c.dataset.label+": "+moneyK(c.raw)}}},
      scales:{x:{...gridless,title:ax("MONTH")},y:{...softGrid,ticks:{callback:v=>moneyK(v)},title:ax("CLOSED VOLUME")},y1:{position:"right",...gridless,ticks:{callback:v=>moneyK(v),maxTicksLimit:5},title:ax("GCI")}}}});
  /* source chart */
  const sv={};
  closedRange.forEach(d=>{const s=d.source||"Unknown";sv[s]=(sv[s]||0)+(d.price||0);});
  const top=Object.entries(sv).sort((a,b)=>b[1]-a[1]).slice(0,8);
  mkChart($("#dealSrc"),{type:"bar",
    data:{labels:top.map(t=>t[0]),datasets:[{data:top.map(t=>t[1]),backgroundColor:"rgba(181,152,90,.8)",borderRadius:5}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>moneyK(c.raw)+" closed volume"}}},
      scales:{x:{...softGrid,ticks:{callback:v=>moneyK(v)},title:ax("CLOSED VOLUME")},y:{...gridless,ticks:{font:{size:10}},title:ax("LEAD SOURCE")}}}});
}

/* ---------- SOURCES ---------- */
let srcPick="";
function renderSources(dates){
  const rows=AG.map(a=>{
    const bk=a.book.buckets||{};
    const ag=bk.agent||{total:0,active:0,touched30:0,stuck:0};
    const co=bk.company||{total:0,active:0,touched30:0,stuck:0};
    return {a, ag, co,
      callsA:sumA(a.id,"ca",dates), callsK:sumA(a.id,"ck",dates),
      nlA:sumA(a.id,"nla",dates), nlK:sumA(a.id,"nlk",dates)};
  });
  const tpct=(t,act)=>act?Math.round(100*t/act):null;
  const cell=(v)=>v==null?'<span class="mini">—</span>':v;
  const body=rows.map(r=>`<tr onclick="openAgent(${r.a.id})" style="cursor:pointer">
    <td class="agname">${esc(r.a.name)}</td>
    <td class="num" style="background:#f4f8f7">${fmt(r.co.active)}</td>
    <td class="num" style="background:#f4f8f7">${fmt(r.callsK)}</td>
    <td class="num" style="background:#f4f8f7">${cell(tpct(r.co.touched30,r.co.active)!=null?pct(tpct(r.co.touched30,r.co.active)):null)}</td>
    <td class="num" style="background:#f4f8f7;color:${r.co.stuck>10?RED:"inherit"}">${fmt(r.co.stuck)}</td>
    <td class="num" style="background:#faf7f0">${fmt(r.ag.active)}</td>
    <td class="num" style="background:#faf7f0">${fmt(r.callsA)}</td>
    <td class="num" style="background:#faf7f0">${cell(tpct(r.ag.touched30,r.ag.active)!=null?pct(tpct(r.ag.touched30,r.ag.active)):null)}</td>
    <td class="num" style="background:#faf7f0">${fmt(r.ag.stuck)}</td></tr>`).join("");

  /* per-source drill */
  const srcTotals={};
  AG.forEach(a=>{ for(const [s,v] of Object.entries(a.book.sourceDetail||{})){
    srcTotals[s]=(srcTotals[s]||0)+v[0]; }});
  const srcList=Object.entries(srcTotals).sort((x,y)=>y[1]-x[1]).slice(0,40);
  if(!srcPick&&srcList.length) srcPick=srcList[0][0];
  const drill=AG.map(a=>{
    const v=(a.book.sourceDetail||{})[srcPick];
    if(!v||!v[0]) return null;
    return `<tr onclick="openAgent(${a.id})" style="cursor:pointer"><td class="agname">${esc(a.name)}</td>
      <td class="num">${fmt(v[0])}</td><td class="num">${fmt(v[1])}</td>
      <td><div class="heat" style="max-width:90px"><i style="width:${v[1]?Math.min(100,100*v[2]/v[1]):0}%;background:${v[1]&&v[2]/v[1]>=.6?GREEN:v[1]&&v[2]/v[1]>=.35?AMBER:RED}"></i></div><span class="mini">${v[1]?pct(100*v[2]/v[1]):"—"}</span></td>
      <td class="num" style="color:${v[3]>5?RED:"inherit"}">${fmt(v[3])}</td></tr>`;
  }).filter(Boolean).join("");

  $("#p-sources").innerHTML=`
    <h2 class="sec">Source Lens — who works what</h2>
    <div class="sub"><span class="badge b-teal">Company-generated</span> = every paid/team source (Zillow, HomeLight, Ruuster, ZConnect, Fello…)&nbsp;&nbsp;
      <span class="badge" style="background:#faf3e4;color:#8a6d2f">Agent-generated</span> = Open House + Agent Lead&nbsp;&nbsp;
      <span class="badge b-grey">Recruiting imports excluded</span></div>
    <div class="card" style="padding:6px;overflow-x:auto">
      <table><thead>
        <tr><th rowspan="2" style="vertical-align:bottom">Agent</th>
          <th colspan="4" style="text-align:center;background:#f4f8f7;color:${TEAL}">COMPANY-GENERATED</th>
          <th colspan="4" style="text-align:center;background:#faf7f0;color:#8a6d2f">AGENT-GENERATED</th></tr>
        <tr><th class="num" style="background:#f4f8f7">Active</th><th class="num" style="background:#f4f8f7">Calls (${range})</th><th class="num" style="background:#f4f8f7">Touch 30d</th><th class="num" style="background:#f4f8f7">Stuck</th>
            <th class="num" style="background:#faf7f0">Active</th><th class="num" style="background:#faf7f0">Calls (${range})</th><th class="num" style="background:#faf7f0">Touch 30d</th><th class="num" style="background:#faf7f0">Stuck</th></tr>
      </thead><tbody>${body}</tbody></table></div>
    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Call effort by lead type — ${range}</h2>
        <div class="sub">Are company leads getting worked as hard as agents' own leads?</div>
        <div class="chartbox tall"><canvas id="srcCalls"></canvas></div></div>
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;gap:10px">
          <h2 class="sec serif" style="font-size:20px;margin:0">Single-source drill-down</h2>
          <select onchange="srcPick=this.value;render()">${srcList.map(s=>`<option ${srcPick===s[0]?"selected":""} value="${esc(s[0])}">${esc(s[0])} (${s[1]})</option>`).join("")}</select>
        </div>
        <div style="max-height:330px;overflow:auto"><table>
          <thead><tr><th>Agent</th><th class="num">Total</th><th class="num">Active</th><th>Touch 30d</th><th class="num">Stuck</th></tr></thead>
          <tbody>${drill||'<tr><td colspan="5" class="mini">No agents hold leads from this source</td></tr>'}</tbody></table></div></div>
    </div>`;

  const sorted=rows.slice().sort((x,y)=>(y.callsK+y.callsA)-(x.callsK+x.callsA)).filter(r=>r.callsK+r.callsA>0);
  mkChart($("#srcCalls"),{type:"bar",
    data:{labels:sorted.map(r=>r.a.name.split(" ")[0]),
      datasets:[{label:"Company leads",data:sorted.map(r=>r.callsK),backgroundColor:"rgba(7,98,97,.75)",borderRadius:4},
                {label:"Their own leads",data:sorted.map(r=>r.callsA),backgroundColor:"rgba(181,152,90,.85)",borderRadius:4}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:"bottom",labels:{boxWidth:10,boxHeight:10}}},
      scales:{x:{...softGrid,title:ax("OUTBOUND CALLS — "+range)},y:{...gridless,title:ax("AGENT")}}}});
}

/* ---------- PLANS ---------- */
function findAgentByName(name){
  const n=(name||"").toLowerCase();
  return AG.find(a=>a.name.toLowerCase()===n)||AG.find(a=>n&&a.name.toLowerCase().startsWith(n.split(" ")[0]));
}
function renderPlans(){
  if(!PLANS.length){ $("#p-plans").innerHTML='<h2 class="sec">Performance Plans</h2><div class="sub">No active plans. Add them to plans.json in TNG Operations.</div>'; return; }
  let html='<h2 class="sec">Performance Plans</h2><div class="sub">Commitments are tracked automatically from FUB — deals from the pipeline, dials from call logs. Edit plans.json to add or close out a plan.</div>';
  const chartJobs=[];
  PLANS.forEach((pl,pi)=>{
    const a=findAgentByName(pl.agent);
    const start=new Date(pl.start+"T00:00:00Z");
    const end=new Date(start.getTime()+pl.days*DAY);
    const elapsed=Math.max(0,Math.floor((NOW-start)/DAY));
    const remaining=Math.max(0,pl.days-elapsed);
    const tPct=Math.min(100,Math.round(100*elapsed/pl.days));
    let targetsHtml="";
    (pl.targets||[]).forEach((t,ti)=>{
      if(t.kind==="uc"&&a){
        const hits=DATA.deals.filter(d=>d.agentId===a.id&&/^(pending|closed)$/i.test(d.stage)&&d.enteredStageAt&&new Date(d.enteredStageAt)>=start);
        const n=hits.length, goal=t.goal||0;
        const met=n>=goal;
        const pace=elapsed<7?null:(n/goal)>=(elapsed/pl.days);
        const badge=met?'<span class="badge b-green">TARGET MET 🎉</span>':pace==null?'<span class="badge b-grey">EARLY DAYS</span>':pace?'<span class="badge b-green">ON PACE</span>':'<span class="badge b-red">BEHIND PACE</span>';
        targetsHtml+=`<div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--line)">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div class="lbl" style="font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted)">${esc(t.label)}</div>${badge}</div>
          <div style="display:flex;align-items:baseline;gap:10px;margin-top:6px">
            <span class="serif" style="font-size:44px;font-weight:500">${n}<span class="dim" style="font-size:26px;color:var(--muted)"> / ${goal}</span></span>
            <div class="heat" style="flex:1;height:8px"><i style="width:${Math.min(100,goal?100*n/goal:0)}%;background:linear-gradient(90deg,${TEAL2},${TEAL})"></i></div>
          </div>
          ${hits.length?`<div class="mini" style="margin-top:8px">${hits.map(d=>`✓ ${esc((d.name||"Deal").slice(0,38))} — ${esc(d.stage)} ${d.enteredStageAt?new Date(d.enteredStageAt).toLocaleDateString("en-US",{month:"short",day:"numeric"}):""} (${moneyK(d.gci)} GCI)`).join("<br>")}</div>`:'<div class="mini" style="margin-top:8px">No qualifying deals yet since plan start.</div>'}
        </div>`;
      }
      if(t.kind==="dials"&&a){
        const days=[]; const today=new Date(dstr(NOW)+"T00:00:00Z");
        const officeDays=(t.officeDays&&t.officeDays.length)?t.officeDays:[1,2,3,4,5];
        const DOWN=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
        const odLbl=DOWN[officeDays[0]]+"–"+DOWN[officeDays[officeDays.length-1]];
        for(let d=new Date(start);d<=today&&d<end;d=new Date(d.getTime()+DAY)){
          if(officeDays.includes(d.getUTCDay())) days.push(dstr(d));
        }
        const s=DATA.series[a.id]||{};
        const vals=days.map(dd=>(s[dd]&&s[dd].c)||0);
        const compliant=vals.filter(v=>v>=t.goal).length;
        const avg=vals.length?Math.round(vals.reduce((x,y)=>x+y,0)/vals.length):0;
        let streak=0; for(let i=vals.length-1;i>=0;i--){ if(vals[i]>=t.goal) streak++; else break; }
        const ok=vals.length<3?null:compliant/vals.length>=0.7;
        const badge=ok==null?'<span class="badge b-grey">EARLY DAYS</span>':ok?'<span class="badge b-green">HOLDING THE STANDARD</span>':'<span class="badge b-red">MISSING OFFICE DAYS</span>';
        targetsHtml+=`<div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--line)">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div class="lbl" style="font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted)">${esc(t.label)} — goal ${t.goal}/day ${odLbl}</div>${badge}</div>
          <div style="display:flex;gap:22px;margin:10px 0 4px;flex-wrap:wrap">
            <div><span class="serif" style="font-size:32px;font-weight:500">${compliant}<span style="font-size:18px;color:var(--muted)">/${vals.length}</span></span><div class="mini">office days hit ${t.goal}+</div></div>
            <div><span class="serif" style="font-size:32px;font-weight:500">${avg}</span><div class="mini">avg dials / office day</div></div>
            <div><span class="serif" style="font-size:32px;font-weight:500">${streak}</span><div class="mini">current streak</div></div>
          </div>
          <div class="chartbox" style="height:170px"><canvas id="planChart${pi}_${ti}"></canvas></div>
          <div class="mini" style="margin-top:4px">Counts all outbound dials logged in FUB for the day (not just the 9–11am block).</div>
        </div>`;
        chartJobs.push({id:`planChart${pi}_${ti}`,days,vals,goal:t.goal});
      }
      if(t.kind==="appts"&&a){
        const startDay=dstr(start), todayISO=dstr(NOW);
        const all=(DATA.apptsByAgent&&DATA.apptsByAgent[a.id])||[];
        const list=all.filter(ap=>ap.created&&ap.created>=startDay).sort((x,y)=>String(x.start||x.created).localeCompare(String(y.start||y.created)));
        const n=list.length;
        const upcomingN=list.filter(ap=>ap.start&&String(ap.start).slice(0,10)>=todayISO).length;
        const fmtWhen=ap=>{
          if(!ap.start) return ap.created?new Date(ap.created+"T00:00:00Z").toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"}):"—";
          const dt=new Date(ap.start), ds=dt.toLocaleDateString("en-US",{month:"short",day:"numeric"});
          return ap.allDay?ds:ds+" "+dt.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit"});
        };
        const rows=list.map(ap=>{
          const upc=ap.start?(String(ap.start).slice(0,10)>=todayISO):false;
          const who=ap.clientId?`<a href="${fub(ap.clientId)}" target="_blank">${esc(ap.client||"Client")}</a>`:(ap.client?esc(ap.client):'<span class="dim">internal</span>');
          const what=esc(ap.type||ap.title||"Appointment");
          const oc=ap.outcome?` · <span class="dim">${esc(ap.outcome)}</span>`:"";
          const tag=upc?' <span class="badge b-green" style="font-size:9px;padding:1px 6px;vertical-align:middle">UPCOMING</span>':"";
          return `<tr><td style="white-space:nowrap;vertical-align:top;padding:3px 10px 3px 0">${esc(fmtWhen(ap))}${tag}</td><td style="vertical-align:top;padding:3px 10px 3px 0">${who}</td><td style="vertical-align:top;padding:3px 0">${what}${oc}</td></tr>`;
        }).join("");
        targetsHtml+=`<div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--line)">
          <div class="lbl" style="font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted)">${esc(t.label)}</div>
          <div style="display:flex;align-items:baseline;gap:10px;margin-top:6px">
            <span class="serif" style="font-size:32px;font-weight:500">${n}</span>
            <div class="mini">appointment${n===1?"":"s"} set since plan start${upcomingN?` · ${upcomingN} upcoming`:""}</div>
          </div>
          ${n?`<table class="mini" style="width:100%;margin-top:10px;border-collapse:collapse"><thead><tr style="text-align:left;color:var(--muted)"><th style="font-weight:600;padding:2px 10px 6px 0">When</th><th style="font-weight:600;padding:2px 10px 6px 0">Client</th><th style="font-weight:600;padding:2px 0 6px 0">Type / title</th></tr></thead><tbody>${rows}</tbody></table>`:`<div class="mini" style="margin-top:8px">No appointments logged yet since plan start.</div>`}
        </div>`;
      }
    });
    const checkin=pl.checkIn?new Date(pl.checkIn+"T00:00:00Z"):null;
    const daysToCheck=checkin?Math.ceil((checkin-NOW)/DAY):null;
    html+=`<div class="card" style="margin-bottom:18px">
      <div class="dethead" style="margin-bottom:10px">
        <div class="av" style="width:54px;height:54px;font-size:18px">${a&&a.picture?`<img src="${a.picture}">`:initials(pl.agent)}</div>
        <div style="flex:1">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <h1 style="font-size:26px;margin:0" class="serif">${esc(pl.agent)}</h1>
            <span class="badge b-amber">${esc(pl.type)}</span>
            ${checkin?`<span class="badge ${daysToCheck<=7?"b-red":"b-grey"}">Check-in ${checkin.toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"})}${daysToCheck>=0?` · in ${daysToCheck}d`:""}</span>`:""}
          </div>
          <div class="mini" style="margin-top:4px">Day ${Math.min(elapsed+1,pl.days)} of ${pl.days} · ${remaining} days left · started ${start.toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"})}</div>
        </div>
        ${a?`<button onclick="openAgent(${a.id})" style="font:inherit;font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:9px 14px;border:1px solid var(--line);background:#fff;border-radius:10px;cursor:pointer;color:var(--teal)">Open book →</button>`:""}
      </div>
      <div class="heat" style="height:7px;margin-bottom:10px"><i style="width:${tPct}%;background:linear-gradient(90deg,${GOLD},${TEAL})"></i></div>
      <div class="mini" style="margin-bottom:4px">${esc(pl.context||"")}</div>
      ${targetsHtml}
    </div>`;
  });
  $("#p-plans").innerHTML=html;
  chartJobs.forEach(j=>{
    mkChart($("#"+j.id),{type:"bar",
      data:{labels:j.days.map(d=>d.slice(5)),datasets:[
        {type:"bar",data:j.vals,backgroundColor:j.vals.map(v=>v>=j.goal?"rgba(47,125,79,.8)":"rgba(179,64,47,.55)"),borderRadius:3},
        {type:"line",data:j.days.map(()=>j.goal),borderColor:GOLD,borderWidth:1.5,borderDash:[5,4],pointRadius:0}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
        scales:{x:{...gridless,ticks:{maxTicksLimit:12,font:{size:9}},title:ax("OFFICE DAY")},y:{...softGrid,title:ax("DIALS")}}}});
  });
}

/* ---------- BOTTLENECKS ---------- */
let bnAgent="", bnStage="", bnStatus="", bnMin=0;
function goBottlenecks(status){ bnStatus=status||""; switchPage("bottlenecks"); }
function renderBottlenecks(){
  const stages=[...new Set(DATA.stuck.map(s=>s.stage))];
  let rows=DATA.stuck.filter(s=>(!bnAgent||s.agentId==bnAgent)&&(!bnStage||s.stage===bnStage)&&s.dsa>=bnMin);
  const byStage={}; DATA.stuck.forEach(s=>{byStage[s.stage]=(byStage[s.stage]||0)+1;});
  const avgIdle=rows.length?Math.round(rows.reduce((s,x)=>s+x.dsa,0)/rows.length):0;

  let watch=DATA.watch.slice().sort((a,b)=>{
    const o={no_contact:0,under_worked:1,working:2,responded:3,reached:4};
    return (o[a.status]-o[b.status])||(b.ageDays-a.ageDays);});
  if(bnStatus) watch=watch.filter(w=>w.status===bnStatus);
  const wBadge={no_contact:["NO CONTACT","b-red"],under_worked:["UNDER-WORKED","b-amber"],working:["WORKING","b-teal"],responded:["RESPONDED","b-green"],reached:["REACHED","b-green"]};
  const watchRows=watch.map(w=>{const[t,c]=wBadge[w.status]||["—","b-grey"];
    return `<tr><td><a href="${fub(w.id)}" target="_blank">${esc(w.name)}</a></td>
      <td class="mini">${esc(w.agent)}</td><td class="mini">${esc(w.source)}</td>
      <td class="num">${w.ageDays}d</td><td class="num">${w.outbound}</td>
      <td class="num">${w.inbound>0?`<b style="color:${GREEN}">${w.inbound}</b>`:0}</td>
      <td><span class="badge ${c}">${t}</span></td></tr>`;}).join("");

  const stuckRows=rows.slice(0,250).map(s=>`<tr>
    <td><a href="${fub(s.id)}" target="_blank">${esc(s.name)}</a></td>
    <td class="mini">${esc(s.agent)}</td>
    <td><span class="badge b-grey">${esc(s.stage)}</span></td>
    <td class="mini">${esc(s.source)}</td>
    <td class="num"><b style="color:${s.dsa>30?RED:s.dsa>14?AMBER:MUTED}">${s.dsa}d</b></td>
    <td class="num mini">${s.age}d</td></tr>`).join("");

  $("#p-bottlenecks").innerHTML=`
    <h2 class="sec">New-Lead Watchlist <span class="mini" style="font-size:13px">— last 7 days, the 3-3-3-3 standard</span></h2>
    <div class="sub">Sorted so the leads that need eyes are on top. Outbound counts calls + texts + emails.</div>
    <div class="filters">
      <select onchange="bnStatus=this.value;render()">
        <option value="">All statuses</option>
        <option value="no_contact" ${bnStatus==="no_contact"?"selected":""}>No contact</option>
        <option value="under_worked" ${bnStatus==="under_worked"?"selected":""}>Under-worked</option>
        <option value="working" ${bnStatus==="working"?"selected":""}>Working</option>
        <option value="responded" ${bnStatus==="responded"?"selected":""}>Responded</option>
        <option value="reached" ${bnStatus==="reached"?"selected":""}>Reached</option>
      </select><span class="count">${watch.length} leads</span></div>
    <div class="card" style="padding:6px;max-height:420px;overflow:auto">
      <table><thead><tr><th>Lead</th><th>Agent</th><th>Source</th><th class="num">Age</th><th class="num">Outbound</th><th class="num">Inbound</th><th>Status</th></tr></thead>
      <tbody>${watchRows||'<tr><td class="mini" colspan="7">No new leads in window</td></tr>'}</tbody></table></div>

    <h2 class="sec">Stuck Pipeline — leads not moving</h2>
    <div class="sub">Anyone idle past their stage's dwell threshold. ${fmt(DATA.stuck.length)} total · average ${avgIdle} days idle in current view.</div>
    <div class="filters">
      <select onchange="bnAgent=this.value;render()"><option value="">All agents</option>
        ${AG.map(a=>`<option value="${a.id}" ${bnAgent==a.id?"selected":""}>${esc(a.name)}</option>`).join("")}</select>
      <select onchange="bnStage=this.value;render()"><option value="">All stages</option>
        ${stages.map(s=>`<option ${bnStage===s?"selected":""}>${esc(s)}</option>`).join("")}</select>
      <select onchange="bnMin=+this.value;render()">
        <option value="0">Any idle time</option><option value="14" ${bnMin===14?"selected":""}>14+ days idle</option>
        <option value="30" ${bnMin===30?"selected":""}>30+ days idle</option><option value="60" ${bnMin===60?"selected":""}>60+ days idle</option></select>
      <span class="count">${rows.length} leads</span></div>
    <div class="grid three">
      <div class="card" style="padding:6px;max-height:520px;overflow:auto">
        <table><thead><tr><th>Lead</th><th>Agent</th><th>Stage</th><th>Source</th><th class="num">Idle</th><th class="num">Age</th></tr></thead>
        <tbody>${stuckRows||'<tr><td class="mini" colspan="6">Nothing stuck under these filters 🎉</td></tr>'}</tbody></table></div>
      <div class="card"><h2 class="sec serif" style="font-size:18px;margin:0 0 8px">Where the pipe leaks</h2>
        <div class="chartbox"><canvas id="bnStage"></canvas></div></div>
    </div>`;

  const se=Object.entries(byStage).sort((a,b)=>b[1]-a[1]);
  mkChart($("#bnStage"),{type:"bar",
    data:{labels:se.map(x=>x[0]),datasets:[{data:se.map(x=>x[1]),backgroundColor:"rgba(7,98,97,.7)",borderRadius:6}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
      scales:{x:{...softGrid,title:ax("LEADS SITTING IDLE")},y:{...gridless,ticks:{font:{size:10}},title:ax("STAGE")}}}});
}

/* ---------- AGENTS ---------- */
function renderAgents(dates,prev){
  if(detailAgent){ renderAgentDetail(detailAgent,dates,prev); return; }
  const cards=AG.map((a,i)=>{
    const m=metrics(a.id,dates);
    const sp=bucket(seriesA(a.id,"c",dates));
    return `<div class="card acard" onclick="openAgent(${a.id})">
      <div class="ahead">
        <div class="av">${a.picture?`<img src="${a.picture}">`:initials(a.name)}</div>
        <div><div class="agname">${esc(a.name)}</div>
        <div class="mini">${fmt(m.active)} working · ${fmt(nurtureOf(a))} nurture · ${fmt(m.book)} total</div></div>
      </div>
      <div class="astats">
        <div><div class="n">${fmt(m.calls)}</div><div class="l">Calls</div></div>
        <div><div class="n">${fmt(m.appts)}</div><div class="l">Appts</div></div>
        <div><div class="n" style="color:${TEAL}">${moneyK(m.gci)}</div><div class="l">GCI ${range}</div></div>
      </div>
      <div style="margin-top:12px">${spark(sp)}</div>
      <div class="mini" style="display:flex;justify-content:space-between;margin-top:6px">
        <span>Coverage 30d ${pct(m.touch)}</span><span>Pending ${moneyK(m.pending)}</span></div>
    </div>`;}).join("");
  $("#p-agents").innerHTML=`
    <h2 class="sec">Agent Books of Business</h2>
    <div class="sub">Every agent measured the same way, over the same ${range} window. Click a card to open the full book.</div>
    <div class="grid agrid">${cards}</div>`;
}

function openAgent(id){ detailAgent=id; switchPage("agents"); }
function renderAgentDetail(id,dates,prev){
  const a=AGI[id]; if(!a){detailAgent=null;return renderAgents(dates,prev);}
  const m=metrics(id,dates), mp=metrics(id,prev);
  const b=a.book;
  const stuckA=DATA.stuck.filter(s=>s.agentId===id);
  const watchA=DATA.watch.filter(w=>w.agentId===id);
  const dealsA=DATA.deals.filter(d=>d.agentId===id&&!/lost/i.test(d.stage));
  const closedA=dealsA.filter(d=>d.closeDate&&new Set(dates).has(d.closeDate));
  const pendA=dealsA.filter(d=>/pending/i.test(d.stage));
  const liveA=dealsA.filter(d=>/mls live|signed/i.test(d.stage));
  const stages=Object.entries(b.stages).sort((x,y)=>y[1]-x[1]);
  const sources=Object.entries(b.sources).sort((x,y)=>y[1]-x[1]).slice(0,6);

  const kpi=(l,v,d)=>`<div class="card kpi"><div class="lbl">${l}</div><div class="val">${v}</div>${d||""}</div>`;
  const dealRow=d=>`<tr><td class="mini">${esc(d.name||"").slice(0,40)}</td>
    <td><span class="badge ${/closed/i.test(d.stage)?"b-green":/pending/i.test(d.stage)?"b-amber":"b-teal"}">${esc(d.stage)}</span></td>
    <td class="num mini">${moneyK(d.price)}</td><td class="num money">${moneyK(d.gci)}</td></tr>`;

  $("#p-agents").innerHTML=`
    <div class="back" onclick="detailAgent=null;render()">← All agents</div>
    <div class="dethead">
      <div class="av">${a.picture?`<img src="${a.picture}">`:initials(a.name)}</div>
      <div><h1>${esc(a.name)}</h1>
      <div class="mini">${fmt(b.active)} working pipeline · ${fmt(nurtureOf(a))} nurture · ${fmt(b.total)} total in FUB · ${fmt(b.neverTouched)} never touched · ${fmt(a.upcomingTasks)} tasks next 7d</div></div>
    </div>
    <div class="grid kpis">
      ${kpi("New Leads",fmt(m.newLeads),delta(m.newLeads,mp.newLeads))}
      ${kpi("Outbound Calls",fmt(m.calls),delta(m.calls,mp.calls))}
      ${kpi("Conversations",fmt(m.conn),delta(m.conn,mp.conn))}
      ${kpi("Appointments",fmt(m.appts),delta(m.appts,mp.appts))}
      ${kpi("Coverage 30d",pct(m.touch),`<span class="delta fl">of ${fmt(m.active)} working leads touched in last 30 days</span>`)}
      ${kpi("GCI Closed",moneyK(m.gci),delta(m.gci,mp.gci))}
      ${kpi("Pending GCI",moneyK(m.pending),`<span class="delta fl">${pendA.length} under contract</span>`)}
    </div>
    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Activity — ${range}</h2>
        <div class="chartbox"><canvas id="agAct"></canvas></div></div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 4px">Book composition</h2>
        <div class="grid two" style="gap:8px">
          <div class="chartbox" style="height:240px"><canvas id="agStage"></canvas></div>
          <div>
            <div class="lbl mini" style="letter-spacing:.14em;text-transform:uppercase;font-size:10px;color:var(--muted);margin-bottom:8px">Top sources</div>
            ${sources.map(s=>`<div style="display:flex;justify-content:space-between;font-size:12.5px;padding:5px 0;border-bottom:1px solid var(--line)"><span>${esc(s[0])}</span><b>${s[1]}</b></div>`).join("")}
          </div>
        </div></div>
    </div>
    <div class="grid two" style="margin-top:20px">
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 8px">Needs attention (${stuckA.length+watchA.filter(w=>w.status==="no_contact"||w.status==="under_worked").length})</h2>
        <div style="max-height:320px;overflow:auto"><table>
        <thead><tr><th>Lead</th><th>Stage</th><th class="num">Idle</th><th>Flag</th></tr></thead><tbody>
        ${watchA.filter(w=>w.status==="no_contact"||w.status==="under_worked").map(w=>`<tr>
          <td><a href="${fub(w.id)}" target="_blank">${esc(w.name)}</a></td><td class="mini">${esc(w.stage)}</td>
          <td class="num">${w.ageDays}d</td><td><span class="badge ${w.status==="no_contact"?"b-red":"b-amber"}">${w.status==="no_contact"?"NEW — NO CONTACT":"NEW — UNDER-WORKED"}</span></td></tr>`).join("")}
        ${stuckA.slice(0,60).map(s=>`<tr><td><a href="${fub(s.id)}" target="_blank">${esc(s.name)}</a></td>
          <td class="mini">${esc(s.stage)}</td><td class="num">${s.dsa}d</td><td><span class="badge b-grey">STUCK</span></td></tr>`).join("")}
        ${(!stuckA.length&&!watchA.length)?'<tr><td class="mini" colspan="4">Clean book 🎉</td></tr>':""}
        </tbody></table></div></div>
      <div class="card"><h2 class="sec serif" style="font-size:20px;margin:0 0 8px">Deals (${dealsA.length})</h2>
        <div style="max-height:320px;overflow:auto"><table>
        <thead><tr><th>Property</th><th>Stage</th><th class="num">Price</th><th class="num">GCI</th></tr></thead>
        <tbody>${[...pendA,...liveA,...closedA.slice(0,30)].map(dealRow).join("")||'<tr><td class="mini" colspan="4">No active deals</td></tr>'}</tbody></table></div></div>
    </div>`;

  mkChart($("#agAct"),{type:"bar",
    data:{labels:bucketLabels(dates),datasets:[
      {type:"bar",label:"Calls",data:bucket(seriesA(id,"c",dates)),backgroundColor:"rgba(7,98,97,.3)",borderRadius:4},
      {type:"line",label:"Conversations",data:bucket(seriesA(id,"cc",dates)),borderColor:GOLD,tension:.4,pointRadius:0,borderWidth:2}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{boxWidth:10}}},
      scales:{x:{...gridless,ticks:{maxTicksLimit:10},title:ax("DATE")},y:{...softGrid,title:ax("COUNT / DAY")}}}});
  mkChart($("#agStage"),{type:"doughnut",
    data:{labels:stages.map(s=>s[0]),datasets:[{data:stages.map(s=>s[1]),backgroundColor:PALETTE,borderWidth:2,borderColor:"#fff"}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:"60%",
      plugins:{legend:{position:"bottom",labels:{boxWidth:9,font:{size:9.5}}}}}});
}

/* ---------- nav ---------- */
function switchPage(p){ page=p;
  $$("#nav button").forEach(b=>b.classList.toggle("on",b.dataset.p===p));
  $$(".page").forEach(el=>el.classList.toggle("on",el.id==="p-"+p));
  render(); window.scrollTo({top:0}); }
$("#nav").addEventListener("click",e=>{ const b=e.target.closest("button"); if(b){ if(b.dataset.p!=="agents") detailAgent=null; switchPage(b.dataset.p);} });

/* range chips */
const chipBox=$("#chips");
RANGES.forEach(([k])=>{ const b=document.createElement("button"); b.textContent=k;
  b.className=k===range?"on":""; b.onclick=()=>{range=k;localStorage.setItem("tngRange",k);
    $$("#chips button").forEach(x=>x.classList.toggle("on",x===b)); render();};
  chipBox.appendChild(b); });

const startAgent=QP.get("agent"); if(startAgent&&AGI[+startAgent]) detailAgent=+startAgent;
const startPage=QP.get("page");
if(startPage&&["overview","scoreboard","leadflow","sources","deals","bottlenecks","plans","agents"].includes(startPage)) switchPage(startPage);
else render();
</script>
</body>
</html>"""

html = HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
html = html.replace("__PLANS__", json.dumps(PLANS, separators=(",", ":")))
with open(out_path, "w") as f:
    f.write(html)
print(f"wrote {out_path} ({len(html)//1024} KB)")
