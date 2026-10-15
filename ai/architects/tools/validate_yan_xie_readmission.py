#!/usr/bin/env python3
"""Verify the #51 follow-up preserves evidence, identity and unrelated work."""
import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = 'c2e8662922fc014292f02a424bd5a4e194662885'

def read(path):
    return json.loads((ROOT/path).read_text())

def previous(path):
    return json.loads(subprocess.check_output(
        ['git', 'show', BASE+':ai/architects/'+path], cwd=REPO))

catalog = read('catalog.json')
before = previous('catalog.json')
old = {p['id']: p for p in before['profiles']}
current = {p['id']: p for p in catalog['profiles']}
assert len(current) == len(catalog['profiles']) == len(old)+1 == 390
assert set(current)-set(old) == {'yan-xie'}
assert all(current[pid] == p for pid, p in old.items() if pid != 'kuen-hung-tsoi')
expected = copy.deepcopy(old['kuen-hung-tsoi'])
expected['contributions'] = [' '.join(expected['contributions'][:2])] + expected['contributions'][2:]
assert current['kuen-hung-tsoi'] == expected, 'Only join two related bullets; preserve all sentences and sources'

p = current['yan-xie']
eligible = [s for s in p['sourceAudit'] if s.get('primary') and s.get('substantive')]
works = {s['workId'] for s in eligible}
assert works == {'m100-isca2026', 'xie-fan-multiwindow-2015-family'}
assert all(s.get('mechanismBody') and s.get('locator') for s in eligible)
assert len({s['url'] for s in eligible}) == 2
interview = next(s for s in p['sourceAudit'] if s['workId']=='xie-interview-2026')
assert interview['primary'] and interview['technicalContent']
assert not interview['substantive'] and not interview['countsForAdmission']

pending = read('research/yan-xie-admission-pending-20261013.json')
old_pending = previous('research/yan-xie-admission-pending-20261013.json')
assert pending['previousProfilePreserved'] == old_pending['previousProfilePreserved']
assert pending['historicalDecision'] == {k:v for k,v in old_pending.items() if k!='previousProfilePreserved'}
assert pending['status'] == 'resolved_for_admission'
assert set(pending['qualifyingWorkIds']) == works
assert all(s in p['sources'] for s in old_pending['previousProfilePreserved']['sources'])

reconciliation = read('research/pr48-reconciliation-20261014.json')
archive = (ROOT/reconciliation['historicalArchive']).read_bytes()
assert hashlib.sha256(archive).hexdigest() == reconciliation['historicalSha256']
original_intake = subprocess.check_output([
    'git','show',reconciliation['pr48']['headCommit']+':'+reconciliation['pr48']['changedFiles'][0]],cwd=REPO)
assert archive == original_intake, 'Preserve #48 byte for byte'
assert len(reconciliation['candidates']) == 10
assert len({x['canonicalId'] for x in reconciliation['candidates']}) == 10
assert all(x['canonicalId'] in current for x in reconciliation['candidates'])
assert sum(x['status']=='already-admitted' for x in reconciliation['candidates']) == 9
assert len(reconciliation['urlsAbsentFromBaseline']) == 11
assert read('research/history/2026-10-13-approved-six-pr51.snapshot.json') == previous('research/batches/2026-10-13-approved-six.json')

# The superseded migration must fail before it can overwrite the new decision,
# even when called through its Python API instead of its CLI.
spec = importlib.util.spec_from_file_location('historical_migration',ROOT/'tools/apply_approved_admissions_20261013.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
candidate = copy.deepcopy(catalog)
try:
    module.apply(candidate, ROOT, write=False)
except ValueError as exc:
    assert 'superseded' in str(exc)
else:
    raise AssertionError('Historical migration must reject the restored disposition')
assert candidate == catalog
print('PASS: 390 unique profiles; 388 unchanged profile objects; all Kuen Hung Tsoi contribution sentences retained; two qualifying Yan Xie works; exact historical archives; old migration blocked.')
