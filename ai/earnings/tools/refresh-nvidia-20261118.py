#!/usr/bin/env python3
"""Integrate one NVIDIA results packet without advancing other issuer checks."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def read(path):
    return json.loads((ROOT / path).read_text())

def write(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def blob(path):
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

e = read('ai/earnings/research/nvidia-results-20261118.json')
c = read('ai/analysts/corpus.json')
l = read('ai/earnings/refresh-ledger.json')
p = read('ai/earnings/coverage-progression.json')
run, cutoff = e['run_id'], e['cutoff']
d, event = e['financial_disclosures'][0], e['event_increments'][0]

if l['current'].get('run_id') == run:
    assert next(x for x in c['financial_disclosures'] if x['id'] == d['id']) == d
    assert c['earnings_refresh'] == l['current']
    assert c['cutoff_at'] == p['evidence_cutoff_at'] == cutoff
    print('Already integrated; no mutation.')
    raise SystemExit(0)

for path, expected in e['baseline_blob_shas'].items():
    assert blob(path) == expected, 'Concurrent input change; review before applying: ' + path
assert d['company'] == 'NVIDIA' and d['counts_as_call'] is False
assert not any(x['id'] == d['id'] for x in c['financial_disclosures'])
assert not any(x['quarter_id'] == event['quarter_id'] for x in c['event_increments'])
before = copy.deepcopy(c)
previous = copy.deepcopy(l['current'])
checks = copy.deepcopy(previous['company_checks'])
row = next(x for x in checks if x['company'] == 'NVIDIA')
row.update(
    status='results_verified_call_pending', inspection_status='partial_coverage',
    checked_at=cutoff, checked_on='2026-11-18', research_cutoff=cutoff,
    check_time_note='checked_at is the fixed research cutoff; source retrieval retained at date precision.',
    success_coverage_advanced=False,
    observation='FY2027 Q3 release, written CFO commentary, selected supplemental statements and prior guidance reviewed. Main-call Q&A and 10-Q not reviewed.',
    check_method=e['scope'], sources=copy.deepcopy(d['sources']),
    results_search_query=None, search_audit_url='research/nvidia-results-20261118.json',
    release_check={'status':'new_quarterly_results_verified','confirmed_absence':False},
    guidance_check={'status':'q4_management_guidance_and_dated_q3_guide_verified'},
    primary_call_check={'status':'main_call_body_not_reviewed','new_selected_questions':0},
    post_earnings_call_check={'status':'not_reviewed_this_increment','new_selected_questions':0,'audio_verified':False},
    limitation='One-issuer results increment; inherited unresolved window remains open. No full filing, call or post-call census.'
)
cur = {
    'run_id':run, 'as_of':cutoff, 'timezone':'Europe/London',
    'baseline_commit':e['baseline_commit'], 'previous_earnings_cutoff':previous['as_of'],
    'previous_cutoff_precision':'Previous exact increment cutoff retained; issuer-specific successful coverage is unchanged.',
    'method':e['scope'], 'new_quarterly_events':1, 'new_full_quarterly_results':1,
    'new_quarterly_revenue_updates':0, 'new_primary_calls':0, 'new_post_earnings_calls':0,
    'new_selected_questions':0, 'new_long_term_guidance_disclosures':0,
    'new_preliminary_earnings_disclosures':0, 'new_monthly_revenue_disclosures':0,
    'financial_disclosure_ids':[d['id']], 'question_ids':[], 'new_reasoning_cases':0,
    'new_staged_synthetic_exercises':0, 'new_recurring_individual_patterns':0,
    'next_confirmed_events':[x for x in previous.get('next_confirmed_events',[]) if x['company'] != 'NVIDIA'],
    'company_checks':checks,
    'coverage_summary':{'companies':35,'issuer_releases_rechecked':1,'other_company_checks_inherited':34,
                        'new_disclosure_reviewed':1,'complete_company_windows':0,'confirmed_absence':0},
    'gaps':[(('Prior 15 November followthrough: ' + x[len('This followthrough '):]) if x.startswith('This followthrough ') else x) for x in previous.get('gaps',[])] + [
        'NVIDIA FY2027 Q3 release/CFO/supplemental statements reviewed; full 10-Q, main-call Q&A and any post-call remain outside this increment.',
        'The current increment rechecks NVIDIA only. Other 34 issuer check objects and timestamps are inherited unchanged.'
    ],
    'counting_rule':'One results-only quarter; zero new reviewed calls, selected questions or training cases.',
    'delivery_state':'integrated_release_data; deployment acceptance is recorded separately'
}
l['history'].append(previous)
l['current'] = cur
c['earnings_refresh_history'].append(copy.deepcopy(c['earnings_refresh']))
c['earnings_refresh'] = copy.deepcopy(cur)
c['financial_disclosures'].append(d)
c['event_increments'].append(event)
c['cutoff'] = '2026-11-18'
c['cutoff_at'] = cutoff
c['counts']['quarterly_events'] += 1
c['counts']['events'] += 1
c['counts']['financial_disclosure_records'] = len(c['financial_disclosures'])
p['evidence_cutoff_at'] = cutoff

assert c['ledger'] == before['ledger'] and c['counts']['questions'] == 224
assert c['counts']['quarterly_events'] == 166 and c['counts']['events'] == 168
assert c['counts']['post_earnings_calls'] == 2
assert [x for x in checks if x['company'] != 'NVIDIA'] == [x for x in previous['company_checks'] if x['company'] != 'NVIDIA']
assert p['updates'] == read('ai/earnings/coverage-progression.json')['updates']

hpath = ROOT / 'ai/earnings/index.html'
h = hpath.read_text()
old = 'Architecture research • Evidence check 12 November 2026'
new = 'Architecture research • NVIDIA financial increment 18 November 2026 · Q&amp;A snapshot 12 November 2026'
assert h.count(old) == 1
h = h.replace(old, new)
summary = '<aside class="note" id="current-results-update"><strong>Latest results update · NVIDIA FY2027 Q3</strong><p>Released 17 November; financial evidence checked 18 November 2026. Revenue <strong>$115.844bn</strong>; Data Center <strong>$107.6bn</strong>; GAAP / non-GAAP EPS <strong>$2.70 / $2.68</strong>. Q4 management guidance is <strong>$130bn ±3%</strong> with an extra week, excludes China Data Center compute, and carries <strong>71–72% gross margin</strong>.</p><p><a href="#company-evidence-NVDA_2027Q3_results_20261117">Financials, sources and decision implications</a> · <a href="research/nvidia-results-20261118.json">Evidence record</a> · <a href="refresh-ledger.json">Refresh ledger</a></p><small>Unaudited results, written CFO commentary and selected supplemental statements reviewed. Main-call Q&amp;A and full 10-Q remain unreviewed in this increment. Other issuer checks retain their own dates.</small></aside>'
anchor = '<section id="call-followthrough">'
assert h.count(anchor) == 1 and 'id="current-results-update"' not in h
h = h.replace(anchor, summary + '\n' + anchor)
hpath.write_text(h)
write('ai/analysts/corpus.json', c)
write('ai/earnings/refresh-ledger.json', l)
write('ai/earnings/coverage-progression.json', p)
print(json.dumps({'run_id':run,'quarterly_slots':166,'financial_disclosures':32,'selected_qa':224,
                  'other_company_checks_preserved':34,'new_reviewed_calls':0,'publication':'not_claimed'}))
