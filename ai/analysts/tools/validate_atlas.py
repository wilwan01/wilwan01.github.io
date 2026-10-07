#!/usr/bin/env python3
"""Check joins and evidence-state boundaries before publishing the thought atlas."""
import json
import pathlib
import re
from collections import Counter

root = pathlib.Path(__file__).resolve().parents[1]
atlas = json.loads((root / 'thought-atlas.json').read_text())
keys = json.loads((root / 'thought-answer-keys.json').read_text())
cohort = json.loads((root / 'candidate-pipeline.json').read_text())
groups = {}
for group in ('profiles', 'sources', 'cards'):
    ids = [item['id'] for item in atlas[group]]
    assert len(ids) == len(set(ids)), f'duplicate {group} IDs'
    groups[group] = set(ids)
for source in atlas['sources']:
    assert source.get('access') and source.get('summary'), source['id']
    assert source['url'].startswith(('https://', 'http://')), source['id']
for profile in atlas['profiles']:
    for field in ('id', 'name', 'side', 'role', 'scope', 'focus', 'boundary', 'timeline', 'gaps', 'comparison'):
        assert field in profile, (profile['id'], field)
    assert profile['side'] in ('buy', 'sell')
    for event in profile['timeline']:
        assert set(event['source_ids']) <= groups['sources'], profile['id']
for card in atlas['cards']:
    assert card['profile'] in groups['profiles'], card['id']
    assert card['source_ids'] and set(card['source_ids']) <= groups['sources'], card['id']
    for field in ('source_paraphrase', 'attribution', 'model', 'boundary', 'counterexample', 'test', 'question', 'constraint', 'transfer', 'locator'):
        assert isinstance(card[field], str) and card[field].strip(), (card['id'], field)
    assert card['id'] in keys and isinstance(keys[card['id']], str), card['id']
    assert 'evaluator_key' not in card and 'answer' not in card, card['id']
    assert all(re.fullmatch(r'F(?:[1-9]|1[0-9]|2[0-5])|T[1-6]', tag) for tag in card['tags']), card['id']
assert set(keys) == groups['cards'], 'answer/card mismatch'
people = cohort['candidates']
assert len(people) == len({p['id'] for p in people}) == 200
assert Counter(p['side'] for p in people) == {'buy': 100, 'sell': 100}
assert sum(p['priority'] for p in people) == 20
for person in people:
    assert person['status'] in ('candidate', 'identity-verified', 'research-ready'), person['id']
    assert not person.get('profileId') or person['profileId'] in groups['profiles'], person['id']
    if person['status'] == 'research-ready':
        sources = person.get('methodSources', []) or person.get('research', {}).get('sources', [])
        assert len({s['url'] for s in sources}) >= 2, person['id']
assert dict(Counter(p['status'] for p in people)) == cohort['counts']
report = {'profiles': len(atlas['profiles']), 'sources': len(atlas['sources']), 'cards': len(atlas['cards']),
          'candidates': len(people), 'priority': 20, 'checks': 'IDs, source/profile joins, answer separation, skill tags, cohort counts and evidence-state references passed'}
print(json.dumps(report, ensure_ascii=False, indent=2))
