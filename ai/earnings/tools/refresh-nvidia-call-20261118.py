#!/usr/bin/env python3
"""Attach reviewed main-call evidence to the existing NVIDIA quarter, once."""
import copy
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads((ROOT / path).read_text())


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def blob(path):
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


packet_path = 'ai/earnings/research/nvidia-main-call-20261118.json'
e = read(packet_path)
c = read('ai/analysts/corpus.json')
l = read('ai/earnings/refresh-ledger.json')
p = read('ai/earnings/coverage-progression.json')
run, cutoff, questions = e['run_id'], e['cutoff'], e['questions']
ids = [q['id'] for q in questions]

if l['current'].get('run_id') == run:
    assert c['earnings_refresh'] == l['current']
    assert [q for q in c['ledger'] if q['id'] in ids] == questions
    assert c['cutoff_at'] == p['evidence_cutoff_at'] == cutoff
    print('Already integrated; no mutation.')
    raise SystemExit(0)

for path, expected in e['baseline_blob_shas'].items():
    assert blob(path) == expected, 'Concurrent input change; review before applying: ' + path
assert ids == [f'QA{i}' for i in range(225, 233)]
assert not set(ids).intersection(q['id'] for q in c['ledger'])
before = copy.deepcopy(c)
previous = copy.deepcopy(l['current'])
old_progression = copy.deepcopy(p['updates'])
assert len(c['ledger']) == 224
assert sum(len(q['subasks']) for q in questions) == 15

# A call backfill changes evidence depth, not quarterly/event denominators.
event = next(x for x in c['event_increments'] if x['call_id'] == 'NVDA_2027Q3')
assert event['question_ids'] == []
event.update(question_ids=ids, call_verification_status='available_main_call_mirror_qa_reviewed',
             data_quality_status='All 8 available main-call mirror analyst exchanges reviewed; 15 substantive asks. Not audio-verified. Full Q3 10-Q pending publication.',
             transcript_coverage=copy.deepcopy(e['transcript_coverage']),
             full_filing_status='pending_publication', review_record='research/nvidia-main-call-20261118.json')
c['ledger'].extend(copy.deepcopy(questions))
for q in questions:
    person = next(a for a in c['analysts'] if a['name'] == q['analyst'])
    assert q['id'] not in person['questions'] and 'NVIDIA' in person['companies']
    person['questions'].append(q['id'])
    participant = dict(company='NVIDIA', analyst=q['analyst'], raw_name=q['raw_name'],
                       institution=q['institution_hint'], quarter=q['quarter'], call_id=q['call_id'],
                       date=q['date'], url=q['url'], locator=q['locator'], verified_at=q['verified_at'],
                       source_type=q['source_type'], identity_status=q['identity_status'],
                       participation_status='Dated main-call transcript attribution; not current IR coverage')
    c['call_participants'].append(participant)
    person.setdefault('participants', []).append(copy.deepcopy(participant))

d = next(x for x in c['financial_disclosures'] if x['id'] == 'NVDA_2027Q3_results_20261117')
d['data_quality_status'] = 'Official unaudited results and CFO/supplemental statements reviewed; all 8 main-call mirror Q&A exchanges reviewed without audio verification; full Q3 10-Q pending publication.'
d['sources'].extend(copy.deepcopy(e['sources']))
d['full_filing_review'] = copy.deepcopy(e['full_filing_review'])
d['accounting_boundary']['10Q_status'] = 'Pending publication: no Q3 10-Q in the successfully retrieved SEC current index at ' + e['full_filing_review']['checked_at'] + '. Full filing review is incomplete; Q3 8-K exhibits remain separate evidence.'
d['main_call_review'] = dict(source_id='Q1', call_id='NVDA_2027Q3', question_ids=ids,
                            transcript_coverage=copy.deepcopy(e['transcript_coverage']),
                            data_origin='Public transcript mirror; management claims are not independent measurements')
d['prepared_call_guidance'] = dict(source_id='Q1', locator='Colette Kress prepared remarks lines 143–183; separate from analyst Q&A',
                                   classification='Management guidance / commentary; not a filed 10-Q',
                                   fy2028_revenue_growth_outlook_pct_approx=75,
                                   previous_fy2028_outlook_pct_as_recalled_by_management=70,
                                   fy2028_gross_margin_pct_range=[72, 73],
                                   q4_margin_trough='Management expects Q4 to be the trough; not a guaranteed permanent floor.',
                                   major_frontier_labs_current_fiscal_year_share_of_data_center_revenue_pct_approx=15,
                                   boundary='Fiscal horizons and Data Center denominator retained. No independently frozen consensus or unconstrained-demand estimate.')
d['prepared_call_operating_claims'] = dict(source_id='Q1',
    locator='Colette Kress prepared remarks, Rubin ramp line 143 and networking line 174',
    classification='Call-attributed management commentary; not independently measured or full-10-Q-verified',
    rubin_first_production_quarter_revenue_usd_billion=dict(value=20, qualifier='nearly'),
    q3_networking_revenue_usd_billion=dict(value=21, operator='greater than'),
    boundary='Preserve approximate wording. This does not establish an exact Data Center compute/networking split or product-level profit bridge.')
d['margin_explanation']['main_call_followthrough'] = dict(source_id='Q1', question_id='QA227',
    management_explanation='Arcuri answer: supply costs absorbed while honoring existing purchase orders; new pricing with the next fiscal year; FY2028 outlook unchanged.',
    boundary='Qualitative mechanism only; no numerical price/mix/cost bridge or long-term margin floor disclosed.')
d['gaps'] = [x for x in d['gaps'] if not x.startswith(('Main-call Q&A', 'CFO commentary dated 17 November', 'Standalone Data Center'))]
d['gaps'].extend([
    'Exact Data Center compute/networking and product-level margin bridges remain unreconciled. Prepared remarks separately report networking revenue above $21bn; this is call-attributed commentary, not a full filing reconciliation.',
    'All 8 analyst turns in the available main-call mirror were reviewed; audio, transcription completeness and any separate post-call remain unverified.',
    'Full Q3 10-Q remains unavailable in the current SEC index at the stated check. No filing-specific notes, controls, legal or risk-factor review is claimed.',
    'Call answers leave quantitative margin attribution, future frontier-lab mix, financing hurdle rates and exact capital sequencing unresolved.'
])
# Preserve the original inference and record why its evidence boundary changed.
d['architecture_decision_signals'][0]['mechanism'] = 'Calendar length changes reported growth. The main-call followthrough adds a qualitative supply-cost / existing-order / new-pricing explanation, but no numerical Q4 margin attribution.'
d['architecture_decision_signals'][0]['source_ids'].append('Q1')
d['architecture_decision_signals'].extend(copy.deepcopy(e['decision_signals']))
d['review_change_log'] = [dict(reviewed_at=cutoff, previous_record='research/nvidia-results-20261118.json',
    reason='Main-call body now inspected and official SEC filing availability checked; the prior results-only receipt remains unchanged.',
    changes=['Added 8 transcript exchanges to existing quarter', 'Qualified margin mechanism with main-call evidence', 'Recorded full Q3 10-Q as pending publication'],
    reported_actuals_changed=False, prior_source_dates_changed=False)]

checks = copy.deepcopy(previous['company_checks'])
row = next(x for x in checks if x['company'] == 'NVIDIA')
row.update(status='main_call_mirror_reviewed_full_10q_pending', inspection_status='partial_coverage',
           checked_at=cutoff, checked_on='2026-11-18', research_cutoff=cutoff,
           check_time_note='Research cutoff and SEC-index observation time are separate fields; filing check was observed at 11:25:07 London.',
           check_method=e['scope'], observation='8 of 8 available main-call analyst exchanges reviewed ; 15 substantive asks. No full Q3 10-Q in the successful SEC index check; full filing review pending.',
           success_coverage_advanced=False, search_audit_url='research/nvidia-main-call-20261118.json',
           primary_call_check=dict(status='available_main_call_mirror_qa_reviewed', new_selected_questions=8,
                                   new_reviewed_call_bodies=1, transcript_coverage=copy.deepcopy(e['transcript_coverage'])),
           full_filing_check=copy.deepcopy(e['full_filing_review']),
           guidance_check=dict(status='fy2028_prepared_call_guidance_and_main_call_answers_reviewed', source_ids=['Q1']),
           post_earnings_call_check=dict(status='not_reviewed_this_increment', new_selected_questions=0, audio_verified=False),
           limitation='NVIDIA-only main-call textual followthrough. Full Q3 10-Q and separate post-calls pending; inherited unresolved issuer window stays open.')
row['sources'].extend(copy.deepcopy(e['sources']))
cur = dict(run_id=run, as_of=cutoff, timezone='Europe/London', baseline_commit=e['baseline_commit'],
           previous_earnings_cutoff=previous['as_of'], previous_cutoff_precision='Exact previous results-only cutoff retained.',
           method=e['scope'], new_quarterly_events=0, new_full_quarterly_results=0, new_quarterly_revenue_updates=0,
           new_primary_calls=1, new_post_earnings_calls=0, new_selected_questions=8,
           new_long_term_guidance_disclosures=0, new_preliminary_earnings_disclosures=0, new_monthly_revenue_disclosures=0,
           financial_disclosure_ids=[d['id']], new_financial_disclosure_records=0, question_ids=ids,
           new_reasoning_cases=0, new_staged_synthetic_exercises=0, new_recurring_individual_patterns=0,
           next_confirmed_events=copy.deepcopy(previous['next_confirmed_events']), company_checks=checks,
           coverage_summary=dict(companies=35, issuer_call_bodies_rechecked=1, other_company_checks_inherited=34,
                                 full_q3_10q_reviews_completed=0, complete_company_windows=0,
                                 transcript_turns_reviewed=8, transcript_turns_available=8, independently_assessed_asks=15,
                                 full_filing_status='pending_publication'),
           gaps=[x for x in previous['gaps'] if not x.startswith(('NVIDIA FY2027 Q3', 'The current increment rechecks NVIDIA'))] + [
               'NVIDIA: all 8 available main-call mirror analyst turns reviewed; not audio-verified. Any separate post-call remains unreviewed.',
               'NVIDIA full Q3 10-Q: not listed in the successful current SEC index at 11:25:07 London on 18 November; full filing review pending.',
               'The current followthrough updates NVIDIA only; the other 34 issuer check objects and all unresolved windows are preserved.'
           ], counting_rule='Backfill one already-counted quarterly event with one reviewed main-call body and 8 exchange records ; 15 subasks do not add 15 ledger records. No new quarter or post-call.',
           delivery_state='integrated_call_evidence; deployment acceptance recorded separately')
l['history'].append(previous)
l['current'] = cur
c['earnings_refresh_history'].append(copy.deepcopy(c['earnings_refresh']))
c['earnings_refresh'] = copy.deepcopy(cur)
c['cutoff'] = '2026-11-18'
c['cutoff_at'] = cutoff
c['counts'].update(questions=len(c['ledger']), raw_speaker_labels=len({q['raw_name'] for q in c['ledger']}),
                   normalized_ledger_labels=len({q['analyst'] for q in c['ledger']}),
                   call_participant_records=len(c['call_participants']),
                   call_participant_sources=len({x['url'] for x in c['call_participants']}))
p['evidence_cutoff_at'] = cutoff
p['updates']['NVIDIA'] = e['editorial_progression']

assert c['ledger'][:224] == before['ledger']
assert c['financial_disclosures'][:-1] == before['financial_disclosures'][:-1]
assert d['reported_actuals'] == before['financial_disclosures'][-1]['reported_actuals']
for k in ['companies','quarterly_events','events','post_earnings_calls','financial_disclosure_records','directory_labels']:
    assert c['counts'][k] == before['counts'][k], k
assert c['counts']['questions'] == 232 and c['counts']['raw_speaker_labels'] == 131
assert c['counts']['normalized_ledger_labels'] == 115
assert c['counts']['call_participant_records'] == 360 and c['counts']['call_participant_sources'] == 59
assert [x for x in checks if x['company'] != 'NVIDIA'] == [x for x in previous['company_checks'] if x['company'] != 'NVIDIA']
assert {k:v for k,v in p['updates'].items() if k != 'NVIDIA'} == old_progression

esc = lambda value: html.escape(str(value), quote=True)
hpath = ROOT / 'ai/earnings/index.html'
h = hpath.read_text()
h = h.replace('Architecture research • NVIDIA financial increment 18 November 2026 · Q&amp;A snapshot 12 November 2026',
              'Architecture research • NVIDIA main-call review 18 November 2026 · full Q3 10-Q pending')
banner = '''<aside class="note" id="current-results-update"><strong>NVIDIA FY2027 Q3 · main-call review added</strong><p><strong>8 of 8 analyst exchanges</strong> in the available transcript mirror reviewed; <strong>15 substantive asks</strong>. QA225–QA232 extend the existing quarter. Original audio is not verified.</p><p><strong>Full Q3 10-Q pending.</strong> No Q3 filing was listed in the successful SEC submissions check at 11:25:07 GMT on 18 November 2026. The latest listed 10-Q is Q2; the Q3 8-K supplemental statements remain separate evidence.</p><p><a href="#nvidia-main-call-review">What the call changes</a> · <a href="#company-evidence-NVDA_2027Q3_results_20261117">Financials, sources and filing status</a> · <a href="research/nvidia-main-call-20261118.json">Call and filing-check record</a> · <a href="research/nvidia-results-20261118.json">Earlier results-only record</a></p></aside>'''
h, n = re.subn(r'<aside class="note" id="current-results-update">[\s\S]*?</aside>', lambda _:banner, h)
assert n == 1
summary = '''<section id="nvidia-main-call-review"><h2>NVIDIA: what the main call changes</h2><p>Call date: 17 November 2026. Research cutoff: 18 November, 11:28:08 GMT. The eight turn-level records contain 15 separately assessable asks: 3 answered, 5 partially answered and 7 unanswered in the associated main-call exchange. Exchange-level coding is 1 answered and 7 partial. These are editorial coverage counts, not a transparency or sentiment score.</p><div class="cols"><article class="finding"><h3>Capacity needs funded, ready sites</h3><p>Allocation diligence should join component availability to energization, financing, offtake and customer acceptance. Keep management’s approximately 75% FY2028 growth outlook separate from unconstrained demand.</p><p><a href="#QA225">Moore: growth</a> · <a href="#QA231">Buchalter: allocation</a></p></article><article class="finding"><h3>Margin recovery needs a price and cost bridge</h3><p>Separate existing purchase-order economics from new pricing and component costs. The 72–73% outlook is for FY2028; the call does not establish a permanent margin floor or quantify each driver.</p><p><a href="#QA227">Arcuri: margins</a> · <a href="#QA232">Schneider: capital priorities</a></p></article><article class="finding"><h3>Financing conditions remain instrument-specific</h3><p>Management calls the wording a clarification. Keep contingent neocloud commitments and guarantees separate, and verify activation, expiry and post-activation exposure before changing risk assumptions.</p><p><a href="#QA228">Muse: financing</a> · <a href="#QA229">Rasgon: conditions</a></p></article><article class="finding"><h3>Execution claims still need observable checks</h3><p>Test leadership continuity through retention and roadmap delivery; test policy scenarios through dated permits, export eligibility and power milestones. The full Q3 10-Q is still required for filing-specific reconciliation.</p><p><a href="#QA226">Arya: continuity</a> · <a href="#QA230">Reitzes: policy</a></p></article></div><p><a href="https://stockanalysis.com/stocks/nvda/transcripts/739383-q3-2027/" rel="noopener" target="_blank">Public main-call transcript mirror</a> · <a href="https://data.sec.gov/submissions/CIK0001045810.json" rel="noopener" target="_blank">SEC filing index</a>. The mirror’s eight turns were inspected through the operator’s conclusion; transcript completeness and audio accuracy are not independently certified. Prepared remarks are separately recorded, and no post-call review is claimed.</p></section>'''
h = h.replace('<section id="call-followthrough">', summary + '\n<section id="call-followthrough">')
cards = []
for q in questions:
    sub = ''.join('<li>' + esc(a['scope']) + ': ' + esc(a['status']) + '</li>' for a in q['subasks'])
    cards.append(f'''<article class="entry" data-company="NVIDIA" data-status="{esc(q['status'])}" data-theme="{esc(q['theme'])}" id="{q['id']}"><header><h3>{q['id']} · NVIDIA · FY2027 Q3</h3><span class="status {q['status'].replace(' ','-')}">{esc(q['status'])}</span></header><p class="meta">2026-11-17 · Main-call followthrough · {esc(q['theme'])}</p><p><strong>Ask (concise paraphrase):</strong> {esc(q['ask'])}</p><p><strong>Management testimony:</strong> {esc(q['management_answer'])}</p><p><strong>Evidence boundary:</strong> {esc(q['premise_boundary'])}</p><p><strong>Researcher follow-up:</strong> {esc(q['follow_up'])}</p><details><summary>Subasks and editorial model</summary><ul>{sub}</ul><p>{esc(q['model_bridge'])}</p></details><details><summary>Source and attribution</summary><p>{esc(q['raw_name'])} · {esc(q['institution_hint'])} (at event)<br>{esc(q['respondent'])}<br>{esc(q['locator'])}<br>{esc(q['identity_status'])}<br>{esc(q['evidence_status'])}</p><a href="{esc(q['url'])}" rel="noopener" target="_blank">Public transcript mirror</a></details></article>''')
assert h.count('<div class="ledger">') == 1
h = h.replace('<div class="ledger">', '<div class="ledger">\n' + '\n'.join(cards))
ledger_json = json.dumps(c['ledger'], ensure_ascii=False).replace('</', r'<\/')
h, n = re.subn(r'(<script id="ledger-data" type="application/json">)[\s\S]*?(</script>)', lambda m:m[1]+ledger_json+m[2], h)
assert n == 1
hpath.write_text(h)
write('ai/analysts/corpus.json', c)
write('ai/earnings/refresh-ledger.json', l)
write('ai/earnings/coverage-progression.json', p)
print(json.dumps(dict(run_id=run, new_quarters=0, newly_reviewed_main_calls=1,
                     questions=232, new_exchange_records=8, independent_asks=15,
                     full_q3_10q_review=False, other_company_checks_preserved=34)))
