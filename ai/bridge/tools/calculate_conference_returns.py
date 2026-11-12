#!/usr/bin/env python3
"""Reproduce bounded historical price associations, never fetch or impute prices."""
import argparse
import datetime as dt
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'research/conference-return-inputs-20261112.json'
METHOD = ROOT / 'research/conference-return-method-20261112.json'
OUTPUT = ROOT / 'research/conference-return-results-20261112.json'


def calculate():
    raw = INPUT.read_bytes()
    data = json.loads(raw)
    method = json.loads(METHOD.read_bytes())
    assert data['cutoff'] == method['cutoff']
    assert [e['id'] for e in data['events']] == method['universe']
    cutoff = dt.datetime.fromisoformat(data['cutoff'])
    rows = {r['date']: r for r in data['price_rows']}
    assert len(rows) == len(data['price_rows'])
    for date, row in rows.items():
        close = dt.datetime.combine(dt.date.fromisoformat(date), dt.time(16), ZoneInfo('America/New_York'))
        assert close <= cutoff, f'Post-cutoff close: {date}'
        assert all(Decimal(str(row[t])) > 0 for t in ('AMD', 'SOXX'))
    results = []
    for event in data['events']:
        sessions = event['sessions_after_event']
        assert sessions == sorted(set(sessions))
        assert all(d > event['event_date'] for d in sessions)
        baseline = event['baseline']
        assert baseline <= event['event_date']
        windows = {}
        for window, endpoint in event['endpoints'].items():
            if endpoint is None:
                windows[window] = {'status': 'unavailable', 'reason': event['pending'][window]}
                continue
            if window == 'event_day':
                assert endpoint == event['event_date'] and baseline < endpoint
            else:
                assert endpoint == sessions[int(window[:-1]) - 1], (event['id'], window)
            assert baseline < endpoint
            values = {}
            for ticker in ('AMD', 'SOXX'):
                start = Decimal(str(rows[baseline][ticker]))
                end = Decimal(str(rows[endpoint][ticker]))
                values[ticker] = (end / start - 1) * 100
            windows[window] = {
                'status': 'calculated', 'baseline': baseline, 'endpoint': endpoint,
                'AMD_return_pct': round(float(values['AMD']), 6),
                'SOXX_return_pct': round(float(values['SOXX']), 6),
                'relative_pp': round(float(values['AMD'] - values['SOXX']), 6),
            }
        results.append({'id': event['id'], 'windows': windows})
    return {'cutoff': data['cutoff'], 'method_sha256': hashlib.sha256(METHOD.read_bytes()).hexdigest(),
            'input_sha256': hashlib.sha256(raw).hexdigest(), 'unit': 'percent; relative difference in percentage points',
            'interpretation': 'Retrospective cumulative split-adjusted close price association, excluding dividends; not causal or ex-ante.',
            'events': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate saved result without modifying files')
    args = parser.parse_args()
    rendered = json.dumps(calculate(), ensure_ascii=False, indent=2) + '\n'
    if args.check:
        assert OUTPUT.read_text() == rendered, 'Saved result differs; regenerate explicitly'
        print('PASS: inputs, cutoff, endpoints and deterministic calculation match saved results')
    else:
        OUTPUT.write_text(rendered)
        print(rendered)
