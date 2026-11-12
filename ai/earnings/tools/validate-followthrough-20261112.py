"""Validate selected-body backfill without upgrading its evidence scope."""
import json,re,subprocess
from pathlib import Path
R=lambda p:json.loads(Path(p).read_text())
c=R('ai/analysts/corpus.json');f=R('ai/earnings/refresh-followthrough-20261112.json');l=R('ai/earnings/refresh-ledger.json');h=Path('ai/earnings/index.html').read_text()
subprocess.run(['node','ai/earnings/tools/sync-coverage.mjs','--check'],check=True)
assert c['cutoff_at']==f['research_cutoff_at']=='2026-11-12T11:19:08+00:00'
assert len(c['ledger'])==c['counts']['questions']==224
assert len({q['id'] for q in c['ledger']})==224
assert c['counts']['quarterly_events']==163 and c['counts']['events']==165
assert c['counts']['post_earnings_calls']==2
assert c['counts']['reasoning_cases']==29 and c['counts']['staged_refresh_exercises']==27
assert len(f['records'])==6 and f['new_quarters']==f['new_event_slots']==0
assert c['earnings_refresh']==l['current']
assert not any(e.get('call_verification_status')=='main_call_body_not_reviewed' for e in c['event_increments'])
base=json.loads(subprocess.check_output(['git','show','HEAD:ai/analysts/corpus.json']))
assert c['ledger'][:218]==base['ledger'], 'Historical Q&A changed'
assert c['financial_disclosures']==base['financial_disclosures'], 'Quarter disclosures changed'
assert c['coverage']==base['coverage'], 'Coverage directory changed'
for r in f['records']:
 e=next(e for e in c['event_increments'] if e['quarter_id']==r['quarter_id']);q=next(q for q in c['ledger'] if q['id']==r['question_ids'][0])
 assert e['question_ids']==r['question_ids'] and e['call_id']==q['call_id']
 assert 'selected_transcript_passages' in e['call_verification_status']
 assert q['source_id']==r['sources'][0]['id'] and q['locator']==r['sources'][0]['locator']
 assert r['sources'][0]['publication_date']<=f['research_cutoff_at'][:10]
 assert h.count('id="'+q['id']+'"')==1
 assert q['pattern_status'].startswith('single-question')
embedded=json.loads(re.search(r'<script id="ledger-data" type="application/json">(.*?)</script>',h,re.S)[1]);assert embedded==c['ledger']
for key in ['ledger','fresh_examples','call_participants']:
 assert len(c[key])==len(base[key])+6
assert c['counts']['call_participant_records']==len(c['call_participants'])
print(json.dumps({'status':'passed','preserved_historical_qa':218,'selected_qa_added':6,'quarters_added':0,'existing_calls_backfilled':6,'remaining_full_call_audio_gap':6}))
