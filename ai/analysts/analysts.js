'use strict';
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='ai-analyst-practice-v1';let corpus,skills,current='F1',stage=0,limit=20,progress={};
try{progress=JSON.parse(localStorage.getItem(KEY)||'{}');if(!progress||Array.isArray(progress)||typeof progress!=='object')progress={}}catch{}
for(const k of Object.keys(progress))if(/^S\d+$/.test(k)&&!progress['F'+k.slice(1)]){progress['F'+k.slice(1)]=progress[k];delete progress[k]}
const stages=['观察与假设','量化与建模','反例与证据','陌生公司迁移'];
const storage=()=>{try{localStorage.setItem(KEY,JSON.stringify(progress));return true}catch{$('practice-status').textContent='浏览器存储不可用，请导出练习记录。';return false}};
const state=()=>progress[current]??={answers:['','','',''],checks:[],stage:0,model_seen:false,updated_at:null};
const skill=()=>skills.find(x=>x.id===current);
const save=()=>{const p=state();p.answers[stage]=$('answer').value;p.stage=stage;p.updated_at=new Date().toISOString();storage()};
const sourceLink=(url,label)=>`<a target="_blank" rel="noopener" href="${esc(url)}">${esc(label)}</a>`;
async function copy(text,status){try{await navigator.clipboard.writeText(text);$(status).textContent='已复制。请粘贴到 ChatGPT 进行评审。'}catch{const ta=document.createElement('textarea');ta.value=text;document.body.append(ta);ta.select();const ok=document.execCommand('copy');ta.remove();$(status).textContent=ok?'已复制。':'复制不可用；请下载练习记录或Master prompt。'}}
function drawPractice(){const s=skill(),p=state();stage=p.stage||0;$('case-title').textContent=`${s.id} · ${s.zh} / ${s.name}`;$('stage-line').textContent=stages.map((x,i)=>`${i===stage?'●':'○'} ${i+1} ${x}`).join(' → ');$('case-question').textContent=stage===0?s.question:stage===1?'给出变量、单位、公式和计算结果。最敏感的变量是哪一个？':stage===2?'构造最强反例：哪个假设改变会使结论反转？给出数据来源、可观察指标和证伪阈值。':s.transfer;$('answer').value=p.answers[stage]||'';$('next-stage').disabled=stage===3;$('model').hidden=true;$('rubric').hidden=true;$('practice-status').textContent=p.updated_at?'已恢复本机草稿；未进行AI评分。':'尚未评估。';}
function model(){save();const s=skill(),p=state();p.model_seen=true;storage();$('model').hidden=false;$('model').innerHTML=`<h3>参考推导 · 合成案例</h3><p>${esc(s.solution)}</p><p class="muted">这是基准模型，边界条件可能改变答案。看过参考推导后，本题不再算独立掌握证据。</p>`;$('rubric').hidden=false;$('rubric').innerHTML='<h3>自评证据清单</h3>'+s.rubric.map((x,i)=>`<label class="rubric-item"><input type="checkbox" data-check="${i}" ${p.checks.includes(i)?'checked':''}>${esc(x)}</label>`).join('')+'<p id="self-summary"></p>';$('rubric').querySelectorAll('input').forEach(el=>el.onchange=()=>{p.checks=[...$('rubric').querySelectorAll('input:checked')].map(x=>Number(x.dataset.check));storage();selfSummary()});selfSummary()}
function selfSummary(){const p=state();$('self-summary').textContent=`自评 ${p.checks.length}/4 项已提供证据。AI评分：未评估；迁移掌握：未验证。`}
function reviewPrompt(){save();const s=skill(),p=state();return `Use $ai-infrastructure-analyst. 请用中文作为AI基建投资分析导师评审，不冒充真实分析师。\n能力：${s.id} ${s.name}\n案例（所有数字是合成教学数据）：${s.question}\n`+stages.map((x,i)=>`${x}: ${p.answers[i]||'[未作答]'}`).join('\n')+`\n迁移题：${s.transfer}\n参考推导已展示：${p.model_seen}\n评分证据要求：${s.rubric.join('；')}\n先指出我已证明和未证明的能力，引用我的推导；按0–2无依据、3–4部分机制、5–6量化基准、7–8反例证据敏感性、9–10陌生迁移证伪评分，未作答标未评估。看过答案不能算独立掌握。只问一个针对最弱假设的追问，等待我的回答，然后增加约束并给新的未见迁移题。不捏造真实共识或买方预期。`}
function rebuildDirectory(){
  const people=new Map();
  for(const p of corpus.analysts.filter(p=>!p.firm_only)){
    const questions=[...p.questions];
    if(!questions.length)continue;
    people.set(p.name,{...p,questions,coverage:[],participants:[],third_party:[],companies:[...new Set(corpus.ledger.filter(q=>questions.includes(q.id)).map(q=>q.company))]});
  }
  for(const [records,kind] of [[corpus.coverage,'coverage'],[corpus.call_participants||[],'participants'],[corpus.third_party_coverage||[],'third_party']]){
    for(const record of records){
      if(!record.analyst||!record.company)continue;
      let p=people.get(record.analyst);
      if(!p){p={name:record.analyst,questions:[],coverage:[],participants:[],third_party:[],companies:[],pattern_status:'single/few-question examples; no stable persona inferred'};people.set(p.name,p)}
      if(!p[kind].some(x=>x.company===record.company&&x.institution===record.institution&&x.url===record.url&&x.rating_date===record.rating_date))p[kind].push(record);
      if(!p.companies.includes(record.company))p.companies.push(record.company);
    }
  }
  for(const record of corpus.coverage_firms||[]){
    people.set('firm:'+record.company+':'+record.institution,{name:record.institution,firm_only:true,questions:[],coverage:[record],participants:[],third_party:[],companies:[record.company],pattern_status:'firm-only official coverage; analyst name not published'});
  }
  corpus.analysts=[...people.values()];
}
const COMPANY_ALIASES={NVIDIA:['NVDA','英伟达','英偉達'],AMD:['超微','Advanced Micro Devices'],Micron:['MU','美光'],Arm:['ARM','安谋','安謀'],Intel:['INTC','英特尔','英特爾']};
function companyNames(company){return [company,...(COMPANY_ALIASES[company]||[]),...corpus.ledger.filter(q=>q.company===company&&q.ticker).map(q=>q.ticker)]}
function companyMatches(company,text){return companyNames(company).some(x=>x.toLowerCase()===text.trim().toLowerCase())}
function directoryMatches(query,co,type){
  query=String(query||'').trim().toLowerCase();
  const companyQuery=[...new Set(corpus.analysts.flatMap(p=>p.companies))].find(c=>companyMatches(c,query));
  const scopedCompany=co||companyQuery;
  return corpus.analysts.map(p=>{
    const coverage=p.coverage.filter(x=>!scopedCompany||x.company===scopedCompany);
    const participants=p.participants.filter(x=>!scopedCompany||x.company===scopedCompany);
    const third=(p.third_party||[]).filter(x=>!scopedCompany||x.company===scopedCompany);
    const questions=corpus.ledger.filter(q=>p.questions.includes(q.id)&&(!scopedCompany||q.company===scopedCompany));
    const text=[p.name,...(scopedCompany?companyNames(scopedCompany):p.companies.flatMap(companyNames)),...coverage.flatMap(x=>[x.institution,x.city]),...participants.flatMap(x=>[x.raw_name,x.institution]),...third.flatMap(x=>[x.institution]),...questions.flatMap(x=>[x.ask,x.theme,x.institution_hint])].join(' ').toLowerCase();
    const queryMatch=!query||(companyQuery?p.companies.includes(companyQuery)&&(!co||co===companyQuery):text.includes(query));
    const sourceMatch=!type||(type==='ir'?coverage.length>0:type==='participants'?participants.length>0:type==='third'?third.length>0:questions.length>0);
    return {person:p,coverage,participants,third,questions,matches:queryMatch&&(!scopedCompany||p.companies.includes(scopedCompany))&&sourceMatch};
  }).filter(x=>x.matches);
}
function filter(){
  const query=$('search').value.trim().toLowerCase(),co=$('company-filter').value,type=$('evidence-filter').value;
  const rows=directoryMatches(query,co,type);
  const selectedCompany=co||[...new Set(corpus.analysts.flatMap(p=>p.companies))].find(c=>companyMatches(c,query));
  const records=corpus.coverage.filter(x=>!selectedCompany||x.company===selectedCompany);
  const participants=(corpus.call_participants||[]).filter(x=>!selectedCompany||x.company===selectedCompany);
  const listed=new Set(records.map(x=>x.analyst)).size;
  const firmRecords=(corpus.coverage_firms||[]).filter(x=>!selectedCompany||x.company===selectedCompany);
  const audit=(corpus.coverage_audit||[]).find(x=>x.company===selectedCompany);
  const auditLabels={published_named_rows_captured:'已收录官方页面全部可见行；公司名单本身可能不穷尽市场覆盖。',published_firms_only:'官方页面仅列机构，不公布个人姓名。',table_unresolved:'已找到官方覆盖页，但完整表格尚未读取；覆盖数未核实。',directory_not_located:'尚未找到完整官方名录；不能据此判断没有分析师覆盖。'};
  $('result-count').textContent=`${rows.length} 个目录标签匹配；显示 ${Math.min(limit,rows.length)} 个。`;
  const status=$('coverage-status');
  if(status){
    status.textContent=selectedCompany
      ?`${selectedCompany}：${listed} 个IR姓名标签、${records.length} 条具名官方覆盖、${firmRecords.length} 条机构或姓名待定记录、${participants.length} 条历史参与。${auditLabels[audit?.status]||'官方覆盖未核实。'} 名单日期：${audit?.page_as_of||'未注明'}；核查：2026-10-05。电话会参与不代表完整覆盖。`
      :`35家公司：14家具名官方名单、2家仅列机构；440条具名覆盖、74条机构或姓名待定记录。另19家公司完整官方覆盖未核实。历史电话会参与单独保留。名单与姓名标签不等于已验证的独立人数。`;
    const url=audit?.url||records[0]?.url;
    if(selectedCompany&&url)status.innerHTML+=` ${sourceLink(url,'核对公司IR覆盖名单')}`;
  }
  $('directory-results').innerHTML=rows.slice(0,limit).map(({person:p,coverage,participants:ps,third:tp,questions:qs})=>`<article class="person"><h3>${esc(p.name)}</h3>${p.firm_only?'<p class="tag">官方机构记录 · 姓名未公布或待定</p>':''}<p>${esc(p.companies.join(' · '))}</p><p class="status">${coverage.length} 条${p.firm_only?'官方机构记录':'具名官方覆盖'} · ${ps.length} 条历史参与 · ${tp.length} 条第三方评级动作（非IR） · ${qs.length} 条精选问答${selectedCompany?'（'+esc(selectedCompany)+'）':''}</p>${coverage.map(x=>`<p>${esc(x.institution)} / ${esc(x.city)} · ${sourceLink(x.url,x.company+' IR')}<br><small>${esc(x.as_of)}</small></p>`).join('')}${tp.length?`<details><summary>第三方评级动作（非IR覆盖表）</summary><ul>${tp.map(x=>`<li>${esc(x.company)} · ${esc(x.institution)} · ${esc(x.rating_date)} · ${esc(x.action)}<br><small>${sourceLink(x.url,x.source)} · ${esc(x.as_of)}</small></li>`).join('')}</ul></details>`:''}${ps.length?`<details><summary>追溯财报参与与机构</summary><ul>${ps.map(x=>`<li>${esc(x.company)} · ${esc(x.quarter)} · ${esc(x.date)}<br>${esc(x.institution)} · ${sourceLink(x.url,'电话会文本')}<br><small>原始标签：${esc(x.raw_name)} · ${esc(x.locator)}<br>${esc(x.identity_status)}；${esc(x.participation_status)}</small></li>`).join('')}</ul></details>`:''}<p class="status">${esc(p.firm_only?'官方名单未提供姓名，不推断个人思想。':p.pattern_status==='single/few-question examples; no stable persona inferred'?'材料不足以提炼稳定个人模式。':'重复模式候选；需人工核验是否重复使用同一种方法。')}</p>${qs.length?`<details><summary>追溯精选提问</summary><ul>${qs.map(x=>`<li>${esc(x.company)} ${esc(x.quarter)} · ${sourceLink(x.url,x.ask)}<br><small>${esc(x.identity_status)}；${esc(x.institution_status)} · ${esc(x.institution_hint)}</small></li>`).join('')}</ul></details>`:''}</article>`).join('')||'<p>没有匹配的已收录记录。官方名单未导入时，零结果不表示无人覆盖。</p>';
  $('more').hidden=limit>=rows.length;
}
function drawCompiler(){const q=corpus.ledger.find(x=>x.id===$('question-select').value);$('compiled').innerHTML=`<p class="tag">${q.verified_at?'DATED TRANSCRIPT CHECK':'IMPORTED SOURCE QUESTION'} / EDITORIAL SKILL MAPPING</p><h3>${esc(q.company)} · ${esc(q.quarter)} · ${esc(q.analyst)}</h3><dl><dt>真实提问转述</dt><dd>${esc(q.ask)}</dd><dt>管理层证词</dt><dd>${esc(q.management_answer)}</dd><dt>回答完整度</dt><dd>${esc(q.status)}</dd><dt>我们拟议追问</dt><dd>${esc(q.follow_up)}</dd><dt>训练能力</dt><dd>${q.skills.map(id=>{const s=skills.find(s=>s.id===id);return `${id} ${s.zh}`}).join(' · ')}</dd><dt>来源与定位</dt><dd>${sourceLink(q.url,'打开原始电话会文本')} · ${esc(q.locator)}<br>${esc(q.evidence_status)}</dd><dt>身份边界</dt><dd>${esc(q.raw_name)} · ${esc(q.identity_status)}<br>机构：${esc(q.institution_hint)} · ${esc(q.institution_status)}</dd></dl><p>训练挑战（我们提出）：这个回答将改变哪条预测？列出未知系数、上下行情景、反例和证伪条件，然后转到另一家公司。</p>`}
function compilerPrompt(){const q=corpus.ledger.find(x=>x.id===$('question-select').value);return `Use $ai-infrastructure-analyst. 请将以下财报问答编译为技能，先核查原文，保留来源、时间和身份的不确定性。\n${JSON.stringify(q,null,2)}\n请区分提问转述、管理层证词和我们的推断。输出隐藏不确定性、KPI、变量单位、因果滞后、看多/看空回答边界、下一季度/FY1/FY2模型修正桥、反例、下一步证据和陌生公司迁移题。没有真实共识时用标明的合成情景，不捏造。个人反复思维模式需要至少3问跨2场并人工检查。同一时刻只问我一题，等待答复。`}
function calc(){const v=['eps0','eps1','pe0','pe1'].map(id=>Number($(id).value));$('valuation').textContent=v.some(x=>!Number.isFinite(x)||x<=0)?'请输入四个正数。':`假设价格 ${ (v[0]*v[2]).toFixed(2)} → ${(v[1]*v[3]).toFixed(2)}，变化 ${((v[1]*v[3]/(v[0]*v[2])-1)*100).toFixed(2)}%。这是同期间EPS×倍数的教学模型，不是真实股票目标价。`}
async function init(){try{[corpus,skills]=await Promise.all(['corpus.json','skill-graph.json'].map(async url=>{const r=await fetch(url+'?v=20261005-ir-audit-1');if(!r.ok)throw Error(url);return r.json()}));rebuildDirectory();const c={...corpus.counts,directory_labels:corpus.analysts.length,ir_coverage_records:corpus.coverage.length};$('stats').innerHTML=[[c.companies,'家公司'],[c.questions,'条精选问答'],[c.directory_labels,'个目录标签'],[c.ir_coverage_records,'条具名IR覆盖'],[corpus.coverage_firms?.length||0,'条IR机构/待定记录'],[c.call_participant_records||0,'条历史参与记录'],[(corpus.third_party_coverage||[]).length,'条第三方评级动作'],[skills.length,'项训练能力']].map(([n,label])=>`<span><strong>${n}</strong>${label}</span>`).join('');$('examples').innerHTML=corpus.fresh_examples.slice(0,6).map(x=>`<article class="example"><p class="tag">FRESH SOURCE CHECK</p><h3>${esc(x.analyst)}</h3><p class="meta">${esc(x.company)} · ${esc(x.date)}</p><p><strong>提问转述</strong><br>${esc(x.ask)}</p><p><strong>我们的推断</strong><br>${esc(x.uncertainty)}</p><p><strong>我们的追问</strong><br>${esc(x.follow_up)}</p><p class="meta">${esc(x.skills.join(' / '))} · 单次问题示例</p>${sourceLink(x.url,'来源 ↗')}<p class="meta">${esc(x.locator)}</p></article>`).join('');$('skill-grid').innerHTML=skills.map(s=>`<article class="skill-card"><span class="tag">${s.id}</span><h3><button data-skill="${s.id}">${esc(s.zh)} ↗</button></h3><small>${esc(s.name)} · 未评估</small><p>${esc(s.rubric[0])} · ${esc(s.rubric[3])}</p></article>`).join('');$('skill-select').innerHTML=skills.map(s=>`<option value="${s.id}">${s.id} ${esc(s.zh)} / ${esc(s.name)}</option>`).join('');const change=id=>{save();current=id;$('skill-select').value=id;drawPractice()};$('skill-select').onchange=e=>change(e.target.value);document.querySelectorAll('[data-skill]').forEach(b=>b.onclick=()=>{change(b.dataset.skill);$('practice').scrollIntoView()});$('save-answer').onclick=()=>{save();$('practice-status').textContent='草稿已保存；尚未进行AI评分。'};$('next-stage').onclick=()=>{if(!$('answer').value.trim()){$('practice-status').textContent='请先写下本阶段的推导。';return}save();state().stage=Math.min(3,stage+1);storage();drawPractice()};$('show-model').onclick=model;$('copy-review').onclick=()=>copy(reviewPrompt(),'practice-status');$('answer').addEventListener('input',save);$('export-progress').onclick=()=>{save();const data={exported_at:new Date().toISOString(),evaluator:'learner drafts and self-assessment only',ai_scores:null,progress};const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='analyst-practice.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};$('reset-progress').onclick=()=>{if(confirm('清除这个浏览器中的全部练习？')){progress={};storage();drawPractice()}};const companies=[...new Set(corpus.analysts.flatMap(p=>p.companies))].sort();$('company-filter').innerHTML+=[...companies].map(x=>`<option>${esc(x)}</option>`).join('');['search','company-filter','evidence-filter'].forEach(id=>$(id).oninput=()=>{limit=20;filter()});$('more').onclick=()=>{limit+=20;filter()};$('question-select').innerHTML=corpus.ledger.map(q=>`<option value="${q.id}">${esc(q.company+' · '+q.quarter+' · '+q.analyst+' — '+q.ask)}</option>`).join('');$('question-select').onchange=drawCompiler;$('copy-compiler').onclick=()=>copy(compilerPrompt(),'compiler-status');['eps0','eps1','pe0','pe1'].forEach(id=>$(id).oninput=calc);drawPractice();drawCompiler();filter();calc()}catch(err){$('stats').textContent='材料读取失败。请刷新页面；可通过页面底部下载文件访问来源。';console.error(err)}}
init();
