import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const c=read('ai/analysts/corpus.json'),l=read('ai/earnings/refresh-ledger.json'),cs=read('ai/analysts/refresh-cases.json'),ks=read('ai/analysts/refresh-answer-keys.json');
const before=JSON.parse(execFileSync('git',['show','a039624e4f8d7ee631aa796e21ba29bd0dac025c:ai/analysts/corpus.json'],{maxBuffer:20e6}));
assert.deepEqual(c.ledger.slice(0,210),before.ledger,'Historical questions changed');
const unique=(rows,key)=>assert.equal(new Set(rows.map(x=>x[key])).size,rows.length,`Duplicate ${key}`);
unique(c.ledger,'id');unique(c.financial_disclosures,'id');unique(cs.cases,'id');unique(c.event_increments.map(e=>({id:e.call_id||e.quarter_id})),'id');unique(l.current.company_checks,'company');
assert.equal(c.ledger.length,216);assert.equal(c.counts.questions,216);assert.equal(c.counts.companies,35);assert.equal(l.current.company_checks.length,35);
assert.equal(c.counts.events,c.counts.quarterly_events+c.counts.post_earnings_calls);
assert.equal(c.counts.quarterly_events,162);assert.equal(c.counts.post_earnings_calls,2);
assert.equal(c.counts.staged_refresh_exercises,cs.cases.filter(x=>x.training?.stages?.length).length);assert.equal(cs.cases.length,28);assert.equal(c.counts.staged_refresh_exercises,26);
assert.equal(c.counts.financial_disclosure_records,c.financial_disclosures.length);
const qids=new Set(c.ledger.map(q=>q.id)),dids=new Set(c.financial_disclosures.map(d=>d.id));
const skill=read('ai/analysts/skill-graph.json');
for(const entry of cs.cases){if(entry.training?.stages?.length)assert.ok(ks.keys[entry.id],entry.id);for(const q of entry.question_ids||[])assert.ok(qids.has(q),q);for(const s of entry.skills)assert.ok(/^F([1-9]|1[0-9]|2[0-5])$/.test(s),s);}
for(const e of c.event_increments){assert.ok(dids.has(e.source_disclosure_id));for(const q of e.question_ids)assert.ok(qids.has(q));}
assert.equal(l.current.new_selected_questions,6);assert.equal(l.current.new_staged_synthetic_exercises,4);
for(const ck of l.current.company_checks)assert.equal(ck.release_check.confirmed_absence,false);
let html=fs.readFileSync('ai/earnings/index.html','utf8');const ids=[...html.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size);
const embedded=JSON.parse(html.match(/<script id="ledger-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);assert.deepEqual(embedded,c.ledger);
for(const q of c.ledger)assert.ok(ids.includes(q.id),q.id);
const theme=html.match(/<select id="theme">([\s\S]*?)<\/select>/)[1];for(const q of c.ledger)assert.ok(theme.includes('>'+q.theme+'</option>'),q.theme);
for(const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
assert.ok(html.includes('216 of 216 probes'));assert.ok(html.includes('cutoff 28 September 2026'));
const js=fs.readFileSync('ai/analysts/analysts.js','utf8');new vm.Script(js);const oldjs=execFileSync('git',['show','a039624:ai/analysts/analysts.js'],{encoding:'utf8'});assert.deepEqual([...js.matchAll(/(?:const|let)\s+\w*KEY\w*\s*=\s*['"][^'"]+['"]/g)].map(m=>m[0]),[...oldjs.matchAll(/(?:const|let)\s+\w*KEY\w*\s*=\s*['"][^'"]+['"]/g)].map(m=>m[0]));
console.log(JSON.stringify({status:'passed',companies:35,quarters:162,post_calls:2,questions:216,reasoning_cases:28,staged_exercises:26,new_exercises:4,historical_questions_unchanged:210,old_download_cutoff_preserved:true,question_ids_unique:true,relations_valid:true,embedded_data_matches:true,js_syntax:true,draft_keys_unchanged:true},null,2));
