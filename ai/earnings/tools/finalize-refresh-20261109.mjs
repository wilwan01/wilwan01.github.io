// Mechanical fixes found by validation; safe to rerun.
import fs from 'node:fs';
for(const p of ['ai/earnings/index.html','ai/analysts/index.html','ai/analysts/master-prompt.txt','ai/earnings/tools/refresh-20261109.mjs']){
 let s=fs.readFileSync(p,'utf8').replaceAll('28 total','26 staged / 28 cases total').replaceAll('累计28个','累计26个分阶段练习／28个案例').replaceAll('/28 exercises','/26 staged exercises and28 cases').replaceAll('210 of 210 probes','216 of 216 probes').replaceAll('staged_refresh_exercises:cases.cases.length','staged_refresh_exercises:cases.cases.filter(x=>x.training?.stages?.length).length');
 if(p==='ai/earnings/index.html')s=s.replace(/<select id="theme">[\s\S]*?<\/select>/,()=>'<select id="theme"><option value="">All themes</option>'+[...new Set(JSON.parse(fs.readFileSync('ai/analysts/corpus.json')).ledger.map(q=>q.theme))].sort().map(t=>'<option>'+t+'</option>').join('')+'</select>');
 fs.writeFileSync(p,s);
}
for(const p of ['ai/earnings/refresh-ledger.json','ai/analysts/corpus.json']){let j=JSON.parse(fs.readFileSync(p));let r=j.current||j.earnings_refresh;delete r.count_corrections;if(j.counts){j.counts.staged_refresh_exercises=26;j.counts.reasoning_cases=28;}fs.writeFileSync(p,JSON.stringify(j,null,2)+'\n');}
const cp='ai/analysts/refresh-cases.json',cs=JSON.parse(fs.readFileSync(cp));
for(const c of cs.cases.filter(x=>x.id.startsWith('CASE-20261109-'))){
 if(c.company==='Arm')c.next_evidence_date='Next two formal quarterly disclosures; exact dates not yet verified. Benchmark thesis additionally requires a matched-generation independent test; timing unknown.';
 if(c.id.endsWith('QCOM-MARGIN-PERIMETER')){c.training.stages[0]=c.training.stages[0].replace('合成：','合成，全部金额为百万美元：');c.training.stages[2]=c.training.stages[2].replace('传统业务单位成本总额上升5','传统业务COGS总额增加5百万美元');}
}fs.writeFileSync(cp,JSON.stringify(cs,null,2)+'\n');
const kp='ai/analysts/refresh-answer-keys.json',ks=JSON.parse(fs.readFileSync(kp));ks.keys['CASE-20261109-ARM-ROYALTY-MIX'].model=ks.keys['CASE-20261109-ARM-ROYALTY-MIX'].model.replace('利润还需成本和回款。','权责发生制利润仍需成本、确认与减值信息；回款另用于现金转化分析。');fs.writeFileSync(kp,JSON.stringify(ks,null,2)+'\n');
const up='ai/earnings/tools/refresh-20261109.mjs';let u=fs.readFileSync(up,'utf8').replace('传统业务单位成本总额上升5','传统业务COGS总额增加5百万美元').replace('合成：传统业务收入100','合成，全部金额为百万美元：传统业务收入100').replace('利润还需成本和回款。','权责发生制利润仍需成本、确认与减值信息；回款另用于现金转化分析。');fs.writeFileSync(up,u);
// Default reference cards must not leak qualitative models into a fresh exercise.
const jp='ai/analysts/analysts.js';let j=fs.readFileSync(jp,'utf8');
j=j.replace('<p><strong>研究者归纳</strong><br>${esc(x.researcher_inference)}</p><details><summary>不确定性、模型修正、反例与证伪（研究者编译）</summary>', '<details data-refresh-hints="${esc(x.id)}"><summary>明确请求：查看编辑归纳、模型与提示（记录为已辅助）</summary><p><strong>研究者归纳</strong><br>${esc(x.researcher_inference)}</p>');
if(!j.includes('function markRefreshHints'))j+='\nfunction markRefreshHints(event){const el=event.target;if(!el.matches?.("details[data-refresh-hints]")||!el.open)return;const id=el.dataset.refreshHints;refreshProgress[id]??={stage:0,answers:{},model_seen:false};refreshProgress[id].model_seen=true;saveRefreshStage();if(refreshId===id)$("refresh-practice-status").textContent="已查看编辑提示；不计无提示独立掌握证据。";}\ndocument.addEventListener("toggle",markRefreshHints,true);\n';
fs.writeFileSync(jp,j);
