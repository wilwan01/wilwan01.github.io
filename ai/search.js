'use strict';
(()=>{
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const SEC={reports:['公司报告','Company reports'],earnings:['财报问答','Earnings Q&A'],analysts:['分析师','Analysts'],architects:['架构师','Architects'],hotchips:['Hot Chips','Hot Chips'],notes:['笔记','Notes'],bridge:['技术×投资','Tech × Invest'],policy:['政策','Policy'],standards:['标准','Standards'],glossary:['术语','Glossary'],method:['方法','Method']};
let entries=[],sec='',q='',limit=40;
const hl=(text,terms)=>{let s=esc(text);for(const t of terms){if(!t)continue;const r=new RegExp('('+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi');s=s.replace(r,'<mark>$1</mark>')}return s};
function score(e,terms){const t=e.t.toLowerCase(),x=e.x.toLowerCase();let sc=0;for(const w of terms){const it=t.indexOf(w),ix=x.indexOf(w);if(it<0&&ix<0)return 0;sc+=it>=0?(it===0?6:3):0;sc+=ix>=0?1:0}return sc}
function draw(){
  const terms=q.toLowerCase().split(/\s+/).filter(Boolean);
  const pool=entries.filter(e=>!sec||e.s===sec);
  const res=terms.length?pool.map(e=>[score(e,terms),e]).filter(a=>a[0]>0).sort((a,b)=>b[0]-a[0]||a[1].t.length-b[1].t.length).map(a=>a[1]):[];
  const counts={};if(terms.length)for(const e of entries){if(score(e,terms)>0)counts[e.s]=(counts[e.s]||0)+1}
  $('#chips').innerHTML=`<button class="chip-btn" data-s="" aria-pressed="${!sec}">全部 / All</button>`+Object.entries(SEC).map(([k,v])=>`<button class="chip-btn" data-s="${k}" aria-pressed="${sec===k}">${v[0]} / ${v[1]}${terms.length?` (${counts[k]||0})`:''}</button>`).join('');
  $('#count').textContent=terms.length?`${res.length} 条结果 / results`:`${entries.length} 条已索引 / entries indexed`;
  $('#results').innerHTML=terms.length?(res.slice(0,limit).map(e=>`<article class="card" style="padding:12px 16px;margin-bottom:10px"><span class="sectag">${SEC[e.s]?SEC[e.s][0]+' / '+SEC[e.s][1]:e.s}</span><span class="sectag">${e.l==='bi'?'中/EN':e.l==='zh'?'中文':'EN'}</span><a href="${esc(e.u)}">${hl(e.t,terms)}</a>${e.x?`<div class="muted" style="font-size:14px">${hl(e.x.slice(0,180),terms)}${e.x.length>180?'…':''}</div>`:''}</article>`).join('')+(res.length>limit?`<p><button class="chip-btn" id="more">显示更多 / Show more</button></p>`:'')||'<p class="empty">没有匹配项 / No results.</p>'):'<p class="empty">输入关键词：公司、人物、术语、标准、事件… / Type a company, person, term, standard or event…</p>';
}
async function init(){
  const r=await fetch('/ai/search-index.json?v=20261011-2');if(!r.ok)throw Error('index');
  const d=await r.json();entries=d.entries;
  q=new URLSearchParams(location.search).get('q')||'';$('#q').value=q;
  $('#q').addEventListener('input',e=>{q=e.target.value;limit=40;history.replaceState(null,'',q?'?q='+encodeURIComponent(q):location.pathname);draw()});
  $('#chips').addEventListener('click',e=>{const b=e.target.closest('[data-s]');if(b){sec=b.dataset.s;limit=40;draw()}});
  $('#results').addEventListener('click',e=>{if(e.target.id==='more'){limit+=40;draw()}});
  draw();
}
init().catch(e=>{$('#results').innerHTML='<p class="empty">索引读取失败 / Failed to load the index: '+esc(e.message)+'</p>'});
})();
