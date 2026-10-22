'use strict';
(()=>{
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const bi=o=>o?`<span class="bi" lang="zh">${esc(o.zh)}</span><span class="bi" lang="en">${esc(o.en)}</span>`:'';
const getJSON=async u=>{const r=await fetch(u+'?v=20261022-conference-locations');if(!r.ok)throw Error(u);return r.json()};
function lang(){
  let v='both';try{v=localStorage.getItem('ai-lang')||'both'}catch{}
  const set=x=>{document.body.dataset.lang=x;try{localStorage.setItem('ai-lang',x)}catch{}$$('#langbar button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.l===x)))};
  const bar=$('#langbar');if(bar){bar.innerHTML='<span>语言 / Language</span>'+[['zh','中文'],['both','双语 / Both'],['en','English']].map(([l,t])=>`<button type="button" data-l="${l}" aria-pressed="false">${t}</button>`).join('');bar.onclick=e=>{const b=e.target.closest('button');if(b)set(b.dataset.l)}}
  set(v);
}
const SHORT={'primary-read':{zh:'原文已读',en:'Primary read'},'primary-located':{zh:'原文已定位',en:'Primary located'},'secondary-authoritative':{zh:'权威二手',en:'Authoritative secondary'},'secondary':{zh:'二手摘要',en:'Secondary'}};
const evBadge=(k,lv)=>`<span class="badge ${esc(k)}" title="${esc(lv[k]?.en||'')}">${bi(SHORT[k]||{zh:k,en:k})}</span>`;
const fmtQA=(q,id)=>q?`<a href="/ai/earnings/#${esc(id)}">${esc(id)} · ${esc(q.company)} ${esc(q.quarter)} — ${esc(q.ask)}</a>`:`<span class="muted">${esc(id)}</span>`;
async function policy(){
  const [p,c,b,rep]=await Promise.all([getJSON('policy.json'),getJSON('/ai/analysts/corpus.json'),getJSON('/ai/bridge/bridge.json'),Promise.resolve(0)]);
  const qa=Object.fromEntries(c.ledger.map(q=>[q.id,q])),cards=Object.fromEntries(b.cards.map(x=>[x.id,x]));
  $('#scope').innerHTML=bi(p.scope);
  $('#legend').innerHTML=Object.entries(p.evidence_levels).map(([k,v])=>`<div>${evBadge(k,p.evidence_levels)}<div>${bi(v)}</div></div>`).join('');
  let kind='',node='',q='';
  const kinds=Object.entries(p.kinds),nodes=Object.entries(p.nodes);
  $('#filters').innerHTML=`<div class="controls"><input id="q" type="search" placeholder="搜索 / Search (BIS, HBM, H200…)" aria-label="search"><span class="muted">类型 / Type</span><button class="chip-btn" data-k="" aria-pressed="true">全部 / All</button>${kinds.map(([k,v])=>`<button class="chip-btn" data-k="${k}" aria-pressed="false">${bi(v)}</button>`).join('')}</div><div class="controls"><span class="muted">环节 / Node</span><button class="chip-btn" data-n="" aria-pressed="true">全部 / All</button>${nodes.map(([k,v])=>`<button class="chip-btn" data-n="${k}" aria-pressed="false">${bi(v)}</button>`).join('')}</div><p id="count" role="status" class="muted"></p>`;
  function draw(){
    const ev=p.events.filter(e=>(!kind||e.kind===kind)&&(!node||e.nodes.includes(node))&&(!q||JSON.stringify(e).toLowerCase().includes(q)));
    $('#count').textContent=`${ev.length} / ${p.events.length}`;
    let y='',h='';
    for(const e of ev){
      const yr=e.date.slice(0,4);if(yr!==y){y=yr;h+=`<div class="year">${y}</div>`}
      const L=e.links||{};
      h+=`<article class="card" id="${e.id}"><header><span class="id">${e.id}</span><span class="date">${e.date}${e.date_note?'':''}</span><span class="badge">${esc(e.region)}</span><span class="badge">${bi(p.kinds[e.kind])}</span>${evBadge(e.evidence,p.evidence_levels)}</header>
      <h3>${bi(e.title)}</h3><p>${bi(e.summary)}</p>${e.date_note?`<p class="muted"><small>${bi(e.date_note)}</small></p>`:''}
      <div class="tags">${e.nodes.map(n=>`<span class="tag">${bi(p.nodes[n])}</span>`).join('')}</div>
      <ul class="srcs">${e.sources.map(s=>`<li><a target="_blank" rel="noopener" href="${esc(s.url)}">${esc(s.label)}</a> <span class="muted">· ${esc(s.type)}</span></li>`).join('')}</ul>
      <p class="caveat">${bi(e.caveat)}</p>
      ${(L.earnings||[]).length||(L.reports||[]).length||(L.bridge||[]).length?`<ul class="rel">${(L.earnings||[]).map(id=>`<li>↳ ${fmtQA(qa[id],id)}</li>`).join('')}${(L.reports||[]).map(f=>`<li>↳ <a href="/ai/${esc(f)}">${esc(f.replace('.html',''))}</a></li>`).join('')}${(L.bridge||[]).map(id=>cards[id]?`<li>↳ <a href="/ai/bridge/#${id}">${id} · ${esc(cards[id].topic)}</a></li>`:'').join('')}${L.note?`<li class="muted"><small>${bi(L.note)}</small></li>`:''}</ul>`:(L.note?`<p class="muted"><small>${bi(L.note)}</small></p>`:'')}
      </article>`;
    }
    $('#list').innerHTML=h||'<p class="empty">没有匹配项 / No matching events.</p>';
  }
  $('#filters').onclick=e=>{const b=e.target.closest('button');if(!b)return;if('k' in b.dataset){kind=b.dataset.k;$$('[data-k]',$('#filters')).forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}else{node=b.dataset.n;$$('[data-n]',$('#filters')).forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}draw()};
  $('#q').oninput=e=>{q=e.target.value.trim().toLowerCase();draw()};
  draw();
  const earn=c.ledger.filter(x=>/china|chinese|export|tariff|licen[cs]e|sanction|entity list/i.test(`${x.ask} ${x.management_answer} ${x.follow_up}`)).length;
  $('#coverage-note').innerHTML=bi({zh:`覆盖说明：178条精选财报问答中，仅${earn}条的提问、回答或追问文字涉及中国/出口管制类关键词。这反映精选方式（按主题，而非按政策），不是公司没有被问到政策问题。`,en:`Coverage note: of the ${c.ledger.length} selected earnings Q&As, only ${earn} mention China or export-control keywords in the ask, answer or follow-up text. That reflects how Q&As were selected (by theme, not by policy), not that companies were not asked about policy.`});
  if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
}
async function standards(){
  const [s,b,c,g]=await Promise.all([getJSON('standards.json'),getJSON('/ai/bridge/bridge.json'),getJSON('/ai/analysts/corpus.json'),getJSON('/ai/method/glossary.json')]);
  const cards=Object.fromEntries(b.cards.map(x=>[x.id,x])),qa=Object.fromEntries(c.ledger.map(q=>[q.id,q])),terms=Object.fromEntries(g.terms.map(t=>[t.id,t]));
  $('#scope').innerHTML=bi(s.scope);
  $('#legend').innerHTML=Object.entries(s.evidence_levels).map(([k,v])=>`<div>${evBadge(k,s.evidence_levels)}<div>${bi(v)}</div></div>`).join('');
  $('#matrix').innerHTML=`<table><thead><tr><th>ID</th><th>Spec / 规范</th><th>Org / 组织</th><th>Layer / 层</th><th>Date / 日期</th><th>Evidence / 证据</th></tr></thead><tbody>${s.items.map(i=>`<tr><td><a href="#${i.id}">${i.id}</a></td><td>${esc(i.name)}</td><td>${esc(i.org)}</td><td>${bi(s.layers[i.layer])}</td><td>${i.date}</td><td>${evBadge(i.evidence,s.evidence_levels)}</td></tr>`).join('')}</tbody></table>`;
  const byId=Object.fromEntries(s.items.map(i=>[i.id,i]));
  $('#relations').innerHTML=s.relations.map(r=>`<li><a href="#${r.a}">${esc(byId[r.a].name)}</a> ↔ <a href="#${r.b}">${esc(byId[r.b].name)}</a> — ${bi(r.note)}</li>`).join('');
  $('#list').innerHTML=Object.keys(s.layers).map(l=>{const its=s.items.filter(i=>i.layer===l);return its.length?`<h2>${bi(s.layers[l])}</h2>`+its.map(i=>{const L=i.links||{};return `<article class="card" id="${i.id}"><header><span class="id">${i.id}</span><span class="date">${i.date}</span><span class="badge">${esc(i.org)}</span>${evBadge(i.evidence,s.evidence_levels)}</header><h3>${esc(i.name)} · ${bi(i.status)}</h3><p>${bi(i.summary)}</p>${i.date_note?`<p class="muted"><small>${bi(i.date_note)}</small></p>`:''}${(i.facts||[]).map(f=>`<p class="muted"><small>${bi(f)}</small></p>`).join('')}
      <ul class="srcs">${i.sources.map(x=>`<li><a target="_blank" rel="noopener" href="${esc(x.url)}">${esc(x.label)}</a> <span class="muted">· ${esc(x.type)}</span></li>`).join('')}</ul><p class="caveat">${bi(i.caveat)}</p>
      <ul class="rel">${(L.hotchips||[]).map(h=>`<li>↳ <a href="/ai/hot-chips/${h.year}.html">Hot Chips ${h.year}</a> · ${esc(h.title)}</li>`).join('')}${(L.bridge||[]).map(id=>cards[id]?`<li>↳ <a href="/ai/bridge/#${id}">${id} · ${esc(cards[id].topic)}</a></li>`:'').join('')}${(L.policy||[]).map(id=>`<li>↳ <a href="/ai/policy/#${id}">政策 / Policy ${id}</a></li>`).join('')}${(L.earnings||[]).map(id=>`<li>↳ ${fmtQA(qa[id],id)}</li>`).join('')}${(L.terms||[]).map(id=>terms[id]?`<li>↳ <a href="/ai/method/glossary.html#${id}">${esc(terms[id].en)} / ${esc(terms[id].zh)}</a></li>`:'').join('')}</ul></article>`}).join(''):''}).join('');
  if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
}
async function glossary(){
  const g=await getJSON('glossary.json');let cat='',q='';
  $('#filters').innerHTML=`<div class="controls"><input id="q" type="search" placeholder="搜索术语 / Search terms" aria-label="search"><button class="chip-btn" data-c="" aria-pressed="true">全部 / All</button>${Object.entries(g.categories).map(([k,v])=>`<button class="chip-btn" data-c="${k}" aria-pressed="false">${bi(v)}</button>`).join('')}</div><p id="count" role="status" class="muted"></p>`;
  $('#note').innerHTML=bi(g.note);
  const draw=()=>{const ts=g.terms.filter(t=>(!cat||t.cat===cat)&&(!q||JSON.stringify(t).toLowerCase().includes(q)));$('#count').textContent=`${ts.length} / ${g.terms.length}`;
    $('#list').innerHTML=ts.length?`<dl class="terms">${ts.map(t=>`<dt id="${t.id}">${esc(t.en)} · ${esc(t.zh)} <span class="sectag">${esc(g.categories[t.cat].en)}</span></dt><dd>${bi({zh:t.def_zh,en:t.def_en})}${t.see.length?`<br><small>${t.see.map(s=>`<a href="${esc(s.url)}">${esc(s.label)}</a>`).join(' · ')}</small>`:''}</dd>`).join('')}</dl>`:'<p class="empty">没有匹配项 / No match.</p>'};
  $('#filters').onclick=e=>{const b=e.target.closest('[data-c]');if(!b)return;cat=b.dataset.c;$$('[data-c]',$('#filters')).forEach(x=>x.setAttribute('aria-pressed',String(x===b)));draw()};
  $('#q').oninput=e=>{q=e.target.value.trim().toLowerCase();draw()};
  draw();if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
}
async function method(){
  const [cu,bm,en,cat,t,c,b,p,s,g,sg,sk]=await Promise.all([getJSON('/ai/customers/customers.json'),getJSON('/ai/benchmarks/benchmarks.json'),getJSON('/ai/energy/energy.json'),getJSON('/ai/architects/catalog.json'),getJSON('/ai/analysts/thought-atlas.json'),getJSON('/ai/analysts/corpus.json'),getJSON('/ai/bridge/bridge.json'),getJSON('/ai/policy/policy.json'),getJSON('/ai/standards/standards.json'),getJSON('/ai/method/glossary.json'),getJSON('/ai/analysts/skill-graph.json'),Promise.resolve(0)]);
  const rows=[
   ['架构师思想库 / Architect Mode','/ai/architects/',`${cat.profiles.length}`,cat.updated,'zh','profiles','/ai/architects/catalog.json'],
   ['分析师思想地图 / Analyst thought atlas','/ai/analysts/thoughts.html',`${t.profiles.length} / ${t.cards.length}`,t.as_of,'zh','profiles / cards','/ai/analysts/thought-atlas.json'],
   ['财报问答与分析师目录 / Earnings Q&A and analyst directory','/ai/analysts/',`${c.counts.questions} / ${c.counts.companies}`,c.cutoff||'','zh','Q&A / companies','/ai/analysts/corpus.json'],
   ['技术 × 投资 / Technology × Investment','/ai/bridge/',`${b.cards.length}`,b.as_of,'zh','cards','/ai/bridge/bridge.json'],
   ['政策与地缘 / Policy','/ai/policy/',`${p.events.length}`,p.as_of,'zh+en','events','/ai/policy/policy.json'],
   ['标准与联盟 / Standards','/ai/standards/',`${s.items.length}`,s.as_of,'zh+en','items','/ai/standards/standards.json'],
   ['需求与买家 / Customers','/ai/customers/',`${cu.items.length}`,cu.as_of,'zh+en','items','/ai/customers/customers.json'],
   ['基准 / Benchmarks','/ai/benchmarks/',`${bm.items.length}`,bm.as_of,'zh+en','items','/ai/benchmarks/benchmarks.json'],
   ['能源与站点 / Energy & sites','/ai/energy/',`${en.items.length}`,en.as_of,'zh+en','items','/ai/energy/energy.json'],
   ['日历 / Calendar','/ai/calendar/','live','ledger','zh+en','events','/ai/calendar/events.json'],
   ['术语表 / Glossary','/ai/method/glossary.html',`${g.terms.length}`,g.as_of,'zh+en','terms','/ai/method/glossary.json']];
  $('#datatable').innerHTML=`<table><thead><tr><th>Section / 板块</th><th>Count / 数量</th><th>As of / 截至</th><th>Language / 语言</th><th>Data / 数据</th></tr></thead><tbody>${rows.map(r=>`<tr><td><a href="${r[1]}">${esc(r[0])}</a></td><td>${esc(r[2])} <span class="muted">${r[5]}</span></td><td>${esc(r[3])}</td><td>${r[4]}</td><td><a href="${r[6]}" download>JSON ↓</a></td></tr>`).join('')}</tbody></table>`;
  const unresolved=c.counts.ir_unresolved_companies;
  $('#dyn-gaps').innerHTML=bi({zh:`当前数字：${c.counts.questions}条精选财报问答（${c.counts.companies}家公司）；${c.counts.ir_named_companies}家公司具名IR名单已读取，${unresolved}家公司的完整IR名单尚未找到；分析师技能${sg.length}项；桥接卡${b.cards.length}张；政策事件${p.events.length}条；标准条目${s.items.length}条。`,en:`Current numbers: ${c.counts.questions} selected earnings Q&As (${c.counts.companies} companies); named IR lists read for ${c.counts.ir_named_companies} companies, full IR lists still not located for ${unresolved}; ${sg.length} analyst skills; ${b.cards.length} bridge cards; ${p.events.length} policy events; ${s.items.length} standards entries.`});
}
async function cards(){
  const pg=document.body.dataset.page,f={customers:'customers.json',benchmarks:'benchmarks.json',energy:'energy.json'}[pg];
  const [d,b,c,g,p,s]=await Promise.all([getJSON(f),getJSON('/ai/bridge/bridge.json'),getJSON('/ai/analysts/corpus.json'),getJSON('/ai/method/glossary.json'),getJSON('/ai/policy/policy.json'),getJSON('/ai/standards/standards.json')]);
  const bc=Object.fromEntries(b.cards.map(x=>[x.id,x])),qa=Object.fromEntries(c.ledger.map(q=>[q.id,q])),terms=Object.fromEntries(g.terms.map(t=>[t.id,t])),pol=Object.fromEntries(p.events.map(e=>[e.id,e])),std=Object.fromEntries(s.items.map(e=>[e.id,e]));
  const X={customers:['C','/ai/customers/'],energy:['E','/ai/energy/'],benchmarks:['M','/ai/benchmarks/']};
  $('#scope').innerHTML=bi(d.scope);
  $('#legend').innerHTML=Object.entries(d.evidence_levels).map(([k,v])=>`<div>${k==='editorial'?`<span class="badge">${bi({zh:'编辑归纳',en:'Editorial'})}</span>`:evBadge(k,d.evidence_levels)}<div>${bi(v)}</div></div>`).join('');
  const rel=L=>{
    const o=[];
    (L.earnings||[]).forEach(id=>o.push(`<li>↳ ${fmtQA(qa[id],id)}${qa[id]?`<br><small class="muted">${esc(qa[id].management_answer)}</small>`:''}</li>`));
    (L.reports||[]).forEach(r=>o.push(`<li>↳ <a href="/ai/${esc(r)}">${esc(r.replace('.html',''))}</a></li>`));
    (L.bridge||[]).forEach(id=>bc[id]&&o.push(`<li>↳ <a href="/ai/bridge/#${id}">${id} · ${esc(bc[id].topic)}</a></li>`));
    (L.policy||[]).forEach(id=>pol[id]&&o.push(`<li>↳ <a href="/ai/policy/#${id}">${id} · ${esc(pol[id].title.en)}</a></li>`));
    (L.standards||[]).forEach(id=>std[id]&&o.push(`<li>↳ <a href="/ai/standards/#${id}">${id} · ${esc(std[id].name)}</a></li>`));
    (L.customers||[]).forEach(id=>o.push(`<li>↳ <a href="/ai/customers/#${id}">${bi({zh:'买家',en:'Customers'})} ${id}</a></li>`));
    (L.energy||[]).forEach(id=>o.push(`<li>↳ <a href="/ai/energy/#${id}">${bi({zh:'能源与站点',en:'Energy & sites'})} ${id}</a></li>`));
    (L.benchmarks||[]).forEach(id=>o.push(`<li>↳ <a href="/ai/benchmarks/#${id}">${bi({zh:'基准',en:'Benchmarks'})} ${id}</a></li>`));
    (L.terms||[]).forEach(id=>terms[id]&&o.push(`<li>↳ <a href="/ai/method/glossary.html#${id}">${esc(terms[id].en)} / ${esc(terms[id].zh)}</a></li>`));
    return o.length?`<ul class="rel">${o.join('')}</ul>`:'';
  };
  $('#list').innerHTML=Object.keys(d.groups).map(k=>{const its=d.items.filter(i=>i.group===k);return its.length?`<h2>${bi(d.groups[k])}</h2>`+its.map(i=>`<article class="card" id="${i.id}"><header><span class="id">${i.id}</span>${i.date?`<span class="date">${i.date}</span>`:''}${i.evidence==='editorial'?`<span class="badge">${bi({zh:'编辑归纳',en:'Editorial'})}</span>`:evBadge(i.evidence,d.evidence_levels)}</header><h3>${bi(i.title)}</h3><p>${bi(i.summary)}</p>${(i.facts||[]).map(x=>`<p class="muted"><small>${bi(x)}</small></p>`).join('')}${i.sources.length?`<ul class="srcs">${i.sources.map(x=>`<li><a target="_blank" rel="noopener" href="${esc(x.url)}">${esc(x.label)}</a> <span class="muted">· ${esc(x.type)}</span></li>`).join('')}</ul>`:''}<p class="caveat">${bi(i.caveat)}</p>${rel(i.links||{})}</article>`).join(''):''}).join('');
  if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
}
async function calendar(){
  const [e,led]=await Promise.all([getJSON('events.json'),getJSON('/ai/earnings/refresh-ledger.json')]);
  const cur=led.current,ev=[];
  (cur.next_confirmed_events||[]).forEach((x,i)=>ev.push({id:'L'+String(i+1).padStart(2,'0'),date:x.date,cat:'earnings',title:{zh:`${x.company} ${x.period} 财报`,en:`${x.company} ${x.period} results`},evidence:'primary-located',url:x.url,note:{zh:x.date_resolution||x.locator||'公司公告的日期。',en:x.date_resolution||x.locator||'Date from the company announcement.'},links:{},ledger:1}));
  e.events.forEach(x=>ev.push(x));
  ev.sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id));
  const today=new Date().toISOString().slice(0,10);let cat=location.hash==='#bank-conferences'?'bank':'',past=false;
  $('#scope').innerHTML=bi(e.scope)+` <span class="muted">· ${esc(cur.as_of)} (${esc(cur.timezone)})</span>`;
  $('#legend').innerHTML=Object.entries(e.evidence_levels).map(([k,v])=>`<div>${k==='editorial'?`<span class="badge">${bi({zh:'编辑归纳',en:'Editorial'})}</span>`:evBadge(k,e.evidence_levels)}<div>${bi(v)}</div></div>`).join('');
  $('#filters').innerHTML=`<div class="controls"><button class="chip-btn" data-c="" aria-pressed="true">全部 / All</button>${Object.entries(e.cats).map(([k,v])=>`<button class="chip-btn" data-c="${k}" aria-pressed="false">${bi(v)}</button>`).join('')}<button class="chip-btn" id="pastbtn" aria-pressed="false">${bi({zh:'含已过去',en:'Include past'})}</button><button class="chip-btn" id="ics">${bi({zh:'下载 .ics',en:'Download .ics'})}</button></div><p id="count" role="status" class="muted"></p>`;
  const vis=()=>ev.filter(x=>(!cat||x.cat===cat)&&(past||(x.end||x.date)>=today));
  const when=x=>x.precision==='month'?x.date.slice(0,7):x.end?`${x.date} → ${x.end}`:x.date;
  function draw(){
    const agenda=$('#bank-conferences');if(agenda)agenda.hidden=cat!=='bank';
    $('[data-c]',$('#filters')).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.c===cat)));
    const v=vis();$('#count').textContent=`${v.length} / ${ev.length}`;
    $('#list').innerHTML=v.length?`<div class="table-wrap"><table><thead><tr><th>Date / 日期</th><th>Event / 事件</th><th>Type / 类型</th><th>Evidence / 证据</th></tr></thead><tbody>${v.map(x=>`<tr${(x.end||x.date)<today?' style="opacity:.6"':''}><td style="white-space:nowrap">${esc(when(x))}</td><td><a target="_blank" rel="noopener" href="${esc(x.url)}">${bi(x.title)}</a><br><small class="muted">${bi(x.note)}</small>${x.links&&(x.links.customers||x.links.energy||x.links.benchmarks||x.links.standards)?`<br><small>${(x.links.customers||[]).map(i=>`<a href="/ai/customers/#${i}">↳ ${i}</a>`).join(' ')}${(x.links.energy||[]).map(i=>`<a href="/ai/energy/#${i}">↳ ${i}</a>`).join(' ')}${(x.links.benchmarks||[]).map(i=>`<a href="/ai/benchmarks/#${i}">↳ ${i}</a>`).join(' ')}${(x.links.standards||[]).map(i=>`<a href="/ai/standards/#${i}">↳ ${i}</a>`).join(' ')}</small>`:''}</td><td>${bi(e.cats[x.cat])}</td><td>${x.evidence==='editorial'?`<span class="badge">${bi({zh:'编辑归纳',en:'Editorial'})}</span>`:evBadge(x.evidence,e.evidence_levels)}</td></tr>`).join('')}</tbody></table></div>`:'<p class="empty">没有即将到来的事件 / No upcoming events.</p>';
  }
  $('#filters').onclick=ev2=>{const b=ev2.target.closest('button');if(!b)return;if(b.id==='pastbtn'){past=!past;b.setAttribute('aria-pressed',String(past))}else if(b.id==='ics'){ics()}else if('c' in b.dataset){cat=b.dataset.c;$$('[data-c]',$('#filters')).forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}draw()};
  function ics(){
    const d8=s=>s.replace(/-/g,''),nx=s=>{const t=new Date(s+'T00:00:00Z');t.setUTCDate(t.getUTCDate()+1);return t.toISOString().slice(0,10).replace(/-/g,'')};
    const rows=vis().filter(x=>x.precision!=='month').map(x=>`BEGIN:VEVENT\r\nUID:${x.id}@wilwan01.github.io\r\nDTSTAMP:${new Date().toISOString().replace(/[-:]/g,'').slice(0,15)}Z\r\nDTSTART;VALUE=DATE:${d8(x.date)}\r\nDTEND;VALUE=DATE:${nx(x.end||x.date)}\r\nSUMMARY:${x.title.en.replace(/[,;]/g,' ')}\r\nURL:${x.url}\r\nEND:VEVENT`);
    const blob=new Blob([`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//wilwan01.github.io//AI research//EN\r\n${rows.join('\r\n')}\r\nEND:VCALENDAR\r\n`],{type:'text/calendar'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='ai-research-calendar.ics';a.click();
  }
  draw();
}
const page=document.body.dataset.page;
lang();
({policy,standards,glossary,method,customers:cards,benchmarks:cards,energy:cards,calendar})[page]?.().catch(e=>{const m=$('#list')||$('#datatable');if(m)m.innerHTML='<p class="empty">数据读取失败 / Failed to load data: '+esc(e.message)+'</p>'});
})();
