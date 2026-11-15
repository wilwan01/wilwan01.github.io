#!/usr/bin/env python3
"""Two-release-only integration. Abort on stale inputs; never publish or modify a schedule."""
import copy, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
R = lambda p: json.loads((ROOT/p).read_text())
def W(p,d): (ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def blob(p):
 b=(ROOT/p).read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
e=R('ai/earnings/research/results-followthrough-20261115.json')
c=R('ai/analysts/corpus.json'); l=R('ai/earnings/refresh-ledger.json'); n=R('ai/earnings/coverage-progression.json')
run=e['run_id']; cut=e['cutoff']; additions=e['financial_disclosures']; companies={d['company'] for d in additions}
if l['current'].get('run_id')==run:
 saved={d['id']:d for d in c['financial_disclosures']}
 assert all(saved.get(d['id'])==d for d in additions), 'Existing integration differs'
 assert n['evidence_cutoff_at']==c['cutoff_at']==cut
 print('Already integrated; no mutation.'); raise SystemExit(0)
expected={'ai/analysts/corpus.json':'4c3a41d4c70aa13a6158193ebd31638b7eaa44d9','ai/earnings/refresh-ledger.json':'21a6cd7b26c42b48ccd4f0fcb05aece1efcf8230','ai/earnings/coverage-progression.json':'357b79ce3186964d915293e81cadcd5dcb22fffa','ai/earnings/index.html':'eb040b98fa370ed03400291187b90dce2a1d6a58'}
for p,h in expected.items(): assert blob(p)==h, 'Concurrent change; re-review before applying: '+p
assert companies=={'Cisco','Applied Materials'} and len(additions)==2
assert not ({d['id'] for d in additions}&{d['id'] for d in c['financial_disclosures']})
assert not ({v['call_id'] for v in e['event_increments']}&{v.get('call_id') for v in c['event_increments']})
before=copy.deepcopy(c); previous=copy.deepcopy(l['current']); checks=copy.deepcopy(previous['company_checks'])
for x in checks:
 if x['company'] not in companies: continue
 d=next(d for d in additions if d['company']==x['company'])
 x.update(status='results_verified_call_pending',inspection_status='partial_coverage',checked_at=cut,success_coverage_advanced=False,observation=d['period']+' official results and selected reconciliation tables rechecked; call Q&A unreviewed.',check_method='Bounded two-release followthrough; not full issuer-window coverage.',sources=copy.deepcopy(d['sources']),results_search_query=None,search_audit_url='research/results-followthrough-20261115.json')
 x['release_check']={'status':'new_quarterly_results_verified','confirmed_absence':False}
 x['guidance_check']={'status':'selected_management_guidance_verified'}
 x['primary_call_check']={'status':'main_call_body_not_reviewed','new_selected_questions':0}
 x['post_earnings_call_check']={'status':'not_reviewed_this_followthrough','new_selected_questions':0,'audio_verified':False}
cur={'run_id':run,'as_of':cut,'timezone':'Europe/London','baseline_commit':e['baseline_commit'],'previous_earnings_cutoff':previous['as_of'],'previous_cutoff_precision':'Prior attempt boundary retained; per-company successful coverage is unchanged.','method':e['scope'],'new_quarterly_events':2,'new_full_quarterly_results':2,'new_quarterly_revenue_updates':0,'new_primary_calls':0,'new_post_earnings_calls':0,'new_selected_questions':0,'new_long_term_guidance_disclosures':0,'new_preliminary_earnings_disclosures':0,'new_monthly_revenue_disclosures':0,'financial_disclosure_ids':[d['id'] for d in additions],'question_ids':[],'new_reasoning_cases':0,'new_staged_synthetic_exercises':0,'new_recurring_individual_patterns':0,'next_confirmed_events':[v for v in previous.get('next_confirmed_events',[]) if v['company'] not in companies],'company_checks':checks,'coverage_summary':{'companies':35,'issuer_releases_rechecked':2,'other_company_checks_inherited':33,'new_disclosure_reviewed':2,'complete_company_windows':0,'confirmed_absence':0},'gaps':[v for v in previous.get('gaps',[]) if 'Applied Materials and Cisco scheduled' not in v]+['Cisco and Applied Materials main-call Q&A and any post-calls remain unreviewed.','This followthrough rechecked only two releases. Other issuer timestamps and unresolved coverage are inherited unchanged.'],'counting_rule':'Two results-only quarters; zero reviewed calls, Q&A or skills.','delivery_state':'integrated_release_data; deployment acceptance is recorded separately'}
l['history'].append(previous); l['current']=cur
c['earnings_refresh_history'].append(copy.deepcopy(c['earnings_refresh'])); c['earnings_refresh']=copy.deepcopy(cur)
c['financial_disclosures']+=additions; c['event_increments']+=e['event_increments']
c['cutoff']='2026-11-15'; c['cutoff_at']=cut
c['counts']['quarterly_events']+=2; c['counts']['events']+=2
c['counts']['financial_disclosure_records']=len(c['financial_disclosures']); n['evidence_cutoff_at']=cut
assert c['ledger']==before['ledger'] and c['counts']['questions']==224
assert c['counts']['quarterly_events']==165 and c['counts']['post_earnings_calls']==2
assert [x for x in checks if x['company'] not in companies]==[x for x in previous['company_checks'] if x['company'] not in companies]
# Extend formal search with recorded disclosure deep links; do not index research drafts.
sp=ROOT/'scripts/build-search-index.py'; s=sp.read_text(); marker='# --- verified financial disclosures (including results-only quarters)\n'
if marker not in s:
 anchor='# --- notes\n'; assert s.count(anchor)==1
 s=s.replace(anchor,marker+'for d in load("analysts/corpus.json")["financial_disclosures"]:\n    add(f"{d[\'company\']} {d[\'period\']} · {d[\'event_type\'].replace(chr(95), chr(32))}", f"/ai/earnings/#company-evidence-{d[\'id\']}", "earnings", f"{d.get(\'ticker\',\'\')} {d[\'release_date\']} {d.get(\'data_quality_status\',\'\')}", "en")\n'+anchor)
 sp.write_text(s)
W('ai/analysts/corpus.json',c); W('ai/earnings/refresh-ledger.json',l); W('ai/earnings/coverage-progression.json',n)
print(json.dumps({'run_id':run,'quarterly_slots':165,'selected_qa':224,'companies_rechecked':2,'other_company_checks_preserved':33,'new_reviewed_calls':0,'publication':'not_claimed'}))
