#!/usr/bin/env python3
"""Validate profile preservation, source thresholds, aliases and static indexes."""
import json,subprocess,unicodedata,re
from pathlib import Path
from collections import Counter
from lxml import html
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
c=json.loads((ROOT/'catalog.json').read_text());b=json.loads((ROOT/'research/batches/2026-10-06.json').read_text());h=json.loads((ROOT/'research/history/2026-10-06-before.json').read_text())
old=json.loads(subprocess.check_output(['git','show',b['baseCommit']+':ai/architects/catalog.json'],cwd=REPO));by={p['id']:p for p in c['profiles']};oldby={p['id']:p for p in old['profiles']};done={r['id'] for r in b['records'] if r['status']=='complete'}
assert len(by)==len(c['profiles'])==259
assert len(b['records'])==76 and len({r['id'] for r in b['records']})==76
assert dict(Counter(r['status'] for r in b['records']))==b['counts']==dict(complete=19,partial=19,pending=38)
assert sum(r['status']=='complete' and r['kind']=='existing' for r in b['records'])==11
assert sum(r['status']=='complete' and r['kind']=='candidate' for r in b['records'])==8
assert set(oldby)<=set(by) and by['tushar-krishna']==oldby['tushar-krishna']
assert h['profiles']==[p for p in old['profiles'] if p['id'] in done]
for p in old['profiles']:
 if p['id'] not in done:assert by[p['id']]==p,p['id']
 else:
  assert all(s in by[p['id']]['sources'] for s in p['sources']),p['id']
  assert by[p['id']]['notes']==p['notes']
normalize=lambda s:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).casefold())
# Explicit aliases are identity checks, not new people.
aliases={'peter-hofstee':['Peter Hofstee','H. Peter Hofstee'],'tim-mattson':['Tim Mattson','Timothy G. Mattson']}
seen={}
for p in c['profiles']:
 for name in [p['name']]+aliases.get(p['id'],[]):
  k=normalize(name);assert k not in seen or seen[k]==p['id'],name;seen[k]=p['id']
for pid in done:
 p=by[pid];assert p['researchStatus']['status']=='complete';assert 1<=len(p['contributions'])<=3
 substantive=[s for s in p['sourceAudit'] if s['type']!='机构报告简介'];assert len({s['url'] for s in substantive})>=2,pid
 assert any(s['type'] in ['论文全文','作者技术文章','作者幻灯片','作者教程','作者讲义/幻灯片'] and '未取得全文' not in s['contentStatus'] for s in substantive),pid
 for s in p['sourceAudit']:
  assert all(s.get(k) for k in ['title','authors','date','url','locator','type','contentStatus','evidenceStrength','role']),pid
  assert s['url'].startswith('https://'),s
 for w in p.get('awardsVerified',[]):assert w['paraphrase'] is True and w['year']<=2026
 assert all(k in ['A'+str(n) for n in range(1,11)] for k in p['challenge']['skills'])
for d in c['domains']:assert d['members']==[p['id'] for p in c['profiles'] if p['domain']==d['id']]
r=html.fromstring((ROOT/'index.html').read_text());ids=[x.get('id') for x in r.xpath('//*[@id]')];assert len(ids)==len(set(ids))
articles=r.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," profile ")]');assert {a.get('id') for a in articles}==set(by)
rows=r.xpath('//*[@id="architect-skill-table"]/tbody/tr');assert len(rows)==259
for row,p in zip(rows,c['profiles']):
 assert row.get('data-name')==p['name'];assert row.get('data-skills').split()==p['challenge']['skills']
 assert row.xpath('./th/a/@href')==['#'+p['id']]
 assert [td.get('data-skill') for td in row.xpath('./td[contains(@class,"associated")]')]==sorted(p['challenge']['skills'],key=lambda x:int(x[1:]))
for p in c['profiles']:
 a=r.xpath('//article[@id="'+p['id']+'"]')[0];assert a.xpath('./h2')[0].text==p['name'];assert a.xpath('./p[@class="thesis"]')[0].text==p['core']
 d=r.xpath('//*[@id="directory-'+p['domain']+'"]//tbody/tr[td/a[@href="#'+p['id']+'"]]')[0];assert d.xpath('./td')[3].text==p['core']
for o in r.xpath('//*[@id="matrix-skill"]/option'):
 k=o.get('value');expected=259 if not k else sum(k in p['challenge']['skills'] for p in c['profiles']);assert str(expected)+' 位' in o.text
broken=[]
for url in r.xpath('//@href'):
 if url.startswith('#') and url[1:] not in ids:broken.append(url)
 if url.startswith('/'):
  clean=url.split('?',1)[0].split('#',1)[0];path=REPO/clean.lstrip('/');path=path/'index.html' if clean.endswith('/') else path
  if not path.exists():broken.append(url)
 if url.startswith('research/') and not (ROOT/url).exists():broken.append(url)
assert not broken,broken
for d in c['domains']:
 de=r.xpath('//aside[@class="toc"]/details[summary[contains(text(),"'+d['label']+'")]]')[0]
 assert de.xpath('./a[not(@class)]/@href')==['#'+pid for pid in d['members']]
 assert de.xpath('./summary')[0].text.endswith(' · '+str(len(d['members'])))
print('PASS: 259 unique profiles; 76 fixed records; 19 audited; all old profiles/sources retained; directories, skills, counts and internal links consistent.')
