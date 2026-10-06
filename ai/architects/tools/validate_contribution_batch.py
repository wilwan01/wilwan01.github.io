#!/usr/bin/env python3
"""Validate profile preservation, source thresholds, aliases and static indexes."""
import json,subprocess,unicodedata,re
from pathlib import Path
from collections import Counter
from lxml import html
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
c=json.loads((ROOT/'catalog.json').read_text());b=json.loads((ROOT/'research/batches/2026-10-06.json').read_text());h=json.loads((ROOT/'research/history/2026-10-06-before.json').read_text())
batchpaths=c['research'].get('batchLogs',[c['research']['batchLog']]);batches=[json.loads((ROOT/path).read_text()) for path in batchpaths]
assert len(batchpaths)==len(set(batchpaths))
old=json.loads(subprocess.check_output(['git','show',b['baseCommit']+':ai/architects/catalog.json'],cwd=REPO));by={p['id']:p for p in c['profiles']};oldby={p['id']:p for p in old['profiles']};done={r['id'] for batch in batches for r in batch['records'] if r['status']=='complete'}
record_ids=[r['id'] for batch in batches for r in batch['records']]
assert len(record_ids)==len(set(record_ids)), 'A person must belong to only one fixed batch'
for batchpath,batch in zip(batchpaths,batches):
 counts=Counter(r['status'] for r in batch['records'])
 assert all(counts.get(k,0)==batch['counts'].get(k,0) for k in set(counts)|set(batch['counts']))
 assert sum(r['status']=='complete' and r['kind']=='existing' for r in batch['records'])==batch['completedExisting']
 assert sum(r['status']=='complete' and r['kind']=='candidate' for r in batch['records'])==batch['completedNew']
 for r in batch['records']:
  if r['status']=='complete':assert by[r['id']]['researchStatus']['batch']==Path(batchpath).stem
 report_html=html.fromstring((ROOT/Path(batchpath).with_suffix('.html')).read_text())
 assert len(report_html.xpath('//tbody/tr'))==len(batch['records'])
 assert {url.removeprefix('../../#') for url in report_html.xpath('//tbody/tr/td/a/@href')}=={r['id'] for r in batch['records'] if r['status']=='complete'}
 if batchpath != c['research']['batchLog']:
  assert len(batch['records'])==batch['plannedScope']==batch['plannedExisting']+batch['plannedCandidates']
  for record in batch['records']:
   if record['status']=='complete':assert record['sources']==by[record['id']]['sourceAudit']
assert len(by)==len(c['profiles'])==len(oldby)+sum(batch['completedNew'] for batch in batches)
assert len(b['records'])==76 and len({r['id'] for r in b['records']})==76
assert dict(Counter(r['status'] for r in b['records']))==b['counts']
assert sum(r['status']=='complete' and r['kind']=='existing' for r in b['records'])==b['completedExisting']
assert sum(r['status']=='complete' and r['kind']=='candidate' for r in b['records'])==b['completedNew']
assert set(oldby)<=set(by) and by['tushar-krishna']==oldby['tushar-krishna']
histories=[json.loads(f.read_text()) for f in (ROOT/'research/history').glob('2026-10-06*before.json')]
preserved={p['id']:p for history in histories for p in history['profiles']}
assert preserved=={p['id']:p for p in old['profiles'] if p['id'] in done}
for p in old['profiles']:
 if p['id'] not in done:assert by[p['id']]==p,p['id']
 else:
  assert all(s in by[p['id']]['sources'] for s in p['sources']),p['id']
  assert by[p['id']]['notes']==p['notes']
normalize=lambda s:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).casefold())
# Classify primary bodies by their actual format; a specification or patent is
# not a paper, and a colleague's recollection is not the subject's own interview.
PRIMARY_BODY_TYPES={'论文全文','作者技术文章','作者幻灯片','作者教程','作者讲义/幻灯片','本人访谈文字稿','技术专著全文','专利说明书全文','技术规范全文','作者演讲文字稿','参与者访谈文字稿'}
# Explicit aliases are identity checks, not new people.
aliases={'peter-hofstee':['Peter Hofstee','H. Peter Hofstee'],'tim-mattson':['Tim Mattson','Timothy G. Mattson']}
seen={}
for p in c['profiles']:
 for name in [p['name']]+p.get('aliases',[])+aliases.get(p['id'],[]):
  k=normalize(name);assert k not in seen or seen[k]==p['id'],name;seen[k]=p['id']
for pid in done:
 p=by[pid];assert p['researchStatus']['status']=='complete';assert 1<=len(p['contributions'])<=3
 substantive=[s for s in p['sourceAudit'] if s['type'] not in ['机构报告简介','官方获奖名单']];assert len({s['url'] for s in substantive})>=2,pid
 assert any(s['type'] in PRIMARY_BODY_TYPES and '未取得全文' not in s['contentStatus'] for s in substantive),pid
 for s in p['sourceAudit']:
  assert all(s.get(k) for k in ['title','authors','date','url','locator','type','contentStatus','evidenceStrength','role']),pid
  assert s['url'].startswith('https://'),s
 for w in p.get('awardsVerified',[]):assert w['paraphrase'] is True and w['year']<=2026
 assert all(k in ['A'+str(n) for n in range(1,11)] for k in p['challenge']['skills'])
# This continuation uses an explicit work-level gate; a second URL or an award
# citation is not a second substantive technical work.
for continuation in [item for batch in batches for item in batch.get('continuations',[])]:
 if continuation.get('evidenceGate')!='two-distinct-substantive-primary-works-v1':continue
 for pid in continuation['completedIds']:
  p=by[pid];sources=p['sourceAudit']
  eligible=[s for s in sources if s.get('primary') is True and s.get('substantive') is True and s['type'] in PRIMARY_BODY_TYPES]
  assert len({s['workId'] for s in eligible})>=2,pid
  assert p.get('sourceFacts') and all(f['workId'] in {s['workId'] for s in eligible} for f in p['sourceFacts']),pid
  if continuation.get('requiresMechanismBody'):
   assert any(s.get('mechanismBody') is True for s in eligible),pid
for d in c['domains']:assert d['members']==[p['id'] for p in c['profiles'] if p['domain']==d['id']]
r=html.fromstring((ROOT/'index.html').read_text());ids=[x.get('id') for x in r.xpath('//*[@id]')];assert len(ids)==len(set(ids))
articles=r.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," profile ")]');assert {a.get('id') for a in articles}==set(by)
rows=r.xpath('//*[@id="architect-skill-table"]/tbody/tr');assert len(rows)==len(by)
for row,p in zip(rows,c['profiles']):
 assert row.get('data-name')==p['name'];assert row.get('data-skills').split()==p['challenge']['skills']
 assert row.xpath('./th/a/@href')==['#'+p['id']]
 assert [td.get('data-skill') for td in row.xpath('./td[contains(@class,"associated")]')]==sorted(p['challenge']['skills'],key=lambda x:int(x[1:]))
for p in c['profiles']:
 a=r.xpath('//article[@id="'+p['id']+'"]')[0];assert a.xpath('./h2')[0].text==p['name'];assert a.xpath('./p[@class="thesis"]')[0].text==p['core']
 for fact in p.get('sourceFacts',[]):assert fact['text'] in a.text_content(),p['id']
 d=r.xpath('//*[@id="directory-'+p['domain']+'"]//tbody/tr[td/a[@href="#'+p['id']+'"]]')[0];assert d.xpath('./td')[3].text==p['core']
for o in r.xpath('//*[@id="matrix-skill"]/option'):
 k=o.get('value');expected=len(by) if not k else sum(k in p['challenge']['skills'] for p in c['profiles']);assert str(expected)+' 位' in o.text
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
assert c['research']['completedThisBatch']==b['counts']['complete']
assert c['research'].get('completedTotal',len(done))==len(done)
assert c['research'].get('remainingCatalog',len(by)-len(done))==len(by)-len(done)
assert c['research']['totalProfiles']==len(by)
print(f'PASS: {len(by)} unique profiles; {len(batches)} fixed batches ({len(record_ids)} records); {len(done)} audited; all old profiles/sources retained; directories, skills, counts and internal links consistent.')
